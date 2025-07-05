import os
import pandas as pd
import json
import re
from typing import Dict, List, Tuple, Any, Optional

# Indian Mining Standards and Regulatory Limits
DGMS_SAFETY_FACTOR_MIN = 1.5  # Minimum safety factor per DGMS guidelines
DGMS_MIN_RQD = 25  # Minimum RQD for any type of mining operation
DGMS_MIN_PILLAR_WIDTH = 3.0  # Minimum pillar width in meters
MMR_MAX_DIP = 70  # Maximum allowable dip angle per MMR for certain methods
IBM_MAX_DEPTH = 2000  # Maximum practical depth for Indian underground mines

# Valid ore types according to Indian mineral classifications
INDIAN_ORE_TYPES = [
    "generic", "gold", "copper", "iron", "zinc", "lead", 
    "bauxite", "chromite", "manganese", "limestone", "coal"
]

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def validate_inputs(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced input validation with comprehensive error checking and warnings.

    Args:
        inputs: Dictionary containing user inputs

    Returns:
        Dictionary with validation results containing:
        - valid: Boolean indicating if inputs are valid
        - data: Validated and cleaned input data
        - warnings: List of DGMS compliance warnings
        - message: Error message if validation fails
    """
    validated = {}
    errors = []
    dgms_warnings = []

    try:
        # Define field limits with Indian regulatory requirements
        float_fields = {
            'ore_thickness': {
                'min': 0.3, 'max': 100.0,
                'description': 'Ore Body Thickness (m)',
                'reference': 'IBM economic standards'
            },
            'dip_angle': {
                'min': 0.0, 'max': MMR_MAX_DIP,
                'description': 'Dip Angle (degrees)',
                'reference': 'MMR for most methods'
            },
            'rqd': {
                'min': DGMS_MIN_RQD, 'max': 100.0,
                'description': 'Rock Quality Designation (%)',
                'reference': 'DGMS minimum requirements'
            },
            'mining_depth': {
                'min': 5.0, 'max': IBM_MAX_DEPTH,
                'description': 'Mining Depth (m)',
                'reference': 'Practical limits for Indian underground mines'
            },
            'ucs': {
                'min': 10.0, 'max': 300.0,
                'description': 'Unconfined Compressive Strength (MPa)',
                'reference': 'Typical rock strength range',
                'optional': True
            }
        }

        # Only validate fields that are present (do not require safety_factor)
        for field, limits in float_fields.items():
            if field not in inputs:
                if limits.get('optional', False):
                    continue
                else:
                    errors.append(f"{limits['description']} is required.")
                    continue

            val = inputs.get(field, None)

            # Handle optional fields
            if val is None or val == '':
                if limits.get('optional', False):
                    continue
                else:
                    errors.append(f"{limits['description']} is required.")
                    continue

            try:
                val = float(val)

                # Check range
                if val < limits['min']:
                    errors.append(
                        f"{limits['description']} must be at least {limits['min']} "
                        f"({limits['reference']})."
                    )
                elif val > limits['max']:
                    errors.append(
                        f"{limits['description']} exceeds maximum allowed value "
                        f"{limits['max']} ({limits['reference']})."
                    )
                else:
                    validated[field] = val

            except (TypeError, ValueError):
                errors.append(f"{limits['description']} must be a valid number.")

        # Validate ore type against Indian mineral classifications
        ore_type = inputs.get('ore_type', 'generic')
        if isinstance(ore_type, str):
            ore_type = ore_type.lower().strip()

        if ore_type in INDIAN_ORE_TYPES:
            validated['ore_type'] = ore_type
        else:
            validated['ore_type'] = 'generic'
            dgms_warnings.append(
                f"Ore type '{ore_type}' not recognized. Using 'generic' instead. "
                f"Valid types: {', '.join(INDIAN_ORE_TYPES)}"
            )

        # Cross-validation checks for DGMS special conditions
        if 'dip_angle' in validated and 'rqd' in validated:
            dip = validated['dip_angle']
            rqd = validated['rqd']
            depth = validated.get('mining_depth', 0)

            # DGMS safety alerts based on combinations
            if dip > 60 and rqd < 70:
                dgms_warnings.append(
                    "DGMS Safety Alert: High dip angle (>60°) with moderate RQD (<70%) "
                    "requires additional ground support and monitoring."
                )

            if dip < 20 and depth > 500:
                dgms_warnings.append(
                    "DGMS Compliance Note: Shallow dip (<20°) at significant depth (>500m) "
                    "may require specialized support systems per MMR guidelines."
                )

            if rqd < 50 and depth > 300:
                dgms_warnings.append(
                    "DGMS Warning: Poor rock quality (RQD<50%) at depth >300m requires "
                    "enhanced support design per DGMS circular."
                )

        # Validate ore thickness against dip angle
        if 'ore_thickness' in validated and 'dip_angle' in validated:
            thickness = validated['ore_thickness']
            dip = validated['dip_angle']

            if thickness < 1.0 and dip > 45:
                dgms_warnings.append(
                    "DGMS Note: Thin ore bodies (<1m) with steep dip (>45°) may require "
                    "specialized mining methods."
                )

        # Return validation results
        if errors:
            return {
                'valid': False,
                'message': '\n'.join(errors),
                'warnings': dgms_warnings
            }

        return {
            'valid': True,
            'data': validated,
            'warnings': dgms_warnings
        }

    except Exception as e:
        return {
            'valid': False,
            'message': f"Validation error: {str(e)}",
            'warnings': []
        }

def load_rock_properties(file_path: str) -> Optional[Dict]:
    """
    Load rock properties from a JSON file containing Indian rock mass classification data.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dictionary of rock properties or None if loading fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            rock_properties = json.load(file)
        return rock_properties
    except Exception as e:
        print(f"Error loading rock properties from {file_path}: {e}")
        return None

def validate_file_input(file_path: str, expected_format: str = 'csv') -> bool:
    """
    Validate file input for data loading.

    Args:
        file_path: Path to the file
        expected_format: Expected file format ('csv', 'json', etc.)

    Returns:
        Boolean indicating if file is valid
    """
    try:
        if not os.path.exists(file_path):
            return False

        if expected_format.lower() == 'csv':
            # Try to read the CSV file
            df = pd.read_csv(file_path)
            return len(df) > 0
        elif expected_format.lower() == 'json':
            # Try to read the JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return isinstance(data, (dict, list))

        return True

    except Exception:
        return False

def sanitize_input(value: str) -> str:
    """
    Sanitize string input to prevent injection attacks.

    Args:
        value: Input string

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return str(value)

    # Remove potentially harmful characters
    value = re.sub(r'[<>"\'&]', '', value)

    # Limit length
    if len(value) > 1000:
        value = value[:1000]

    return value.strip()

def get_validation_summary(validation_result: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of validation results.

    Args:
        validation_result: Result from validate_inputs()

    Returns:
        Formatted summary string
    """
    if not validation_result['valid']:
        return f"Validation Failed:\n{validation_result['message']}"

    summary = ["✓ Input validation passed successfully"]

    if validation_result.get('warnings'):
        summary.append("\nDGMS Compliance Warnings:")
        for warning in validation_result['warnings']:
            summary.append(f"• {warning}")

    return "\n".join(summary)

# Export the main validation function and classes
__all__ = [
    'validate_inputs',
    'load_rock_properties', 
    'validate_file_input',
    'sanitize_input',
    'get_validation_summary',
    'ValidationError',
    'DGMS_SAFETY_FACTOR_MIN',
    'DGMS_MIN_RQD',
    'DGMS_MIN_PILLAR_WIDTH',
    'MMR_MAX_DIP',
    'INDIAN_ORE_TYPES'
]