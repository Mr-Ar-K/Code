import pandas as pd
import json

# Indian Mining Standards and Regulatory Limits
DGMS_SAFETY_FACTOR_MIN = 1.5  # Minimum safety factor per DGMS guidelines
DGMS_MIN_RQD = 25  # Minimum RQD for any type of mining operation
DGMS_MIN_PILLAR_WIDTH = 3.0  # Minimum pillar width in meters
MMR_MAX_DIP = 70  # Maximum allowable dip angle per MMR for certain methods

def validate_inputs(inputs):
    # Improved: type conversion, range checks, and error messages
    validated = {}
    errors = []
    dgms_warnings = []
    
    # Define field limits with Indian regulatory requirements
    float_fields = {
        'ore_thickness': (0.3, 100),  # Minimum 0.3m per IBM economic standards
        'dip_angle': (0, MMR_MAX_DIP),  # Maximum per MMR for most methods
        'rqd': (DGMS_MIN_RQD, 100),  # Minimum RQD per DGMS
        'mining_depth': (5, 2000),  # Practical limits for Indian underground mines
        'safety_factor': (DGMS_SAFETY_FACTOR_MIN, 10)  # Minimum safety factor per DGMS
    }
    
    for field, (min_val, max_val) in float_fields.items():
        val = inputs.get(field, None)
        try:
            val = float(val)
            if val < min_val:
                if field == 'safety_factor' and val > 0:
                    # For safety factor, auto-correct to DGMS minimum but warn
                    dgms_warnings.append(f"{field.replace('_', ' ').title()} increased to DGMS minimum ({DGMS_SAFETY_FACTOR_MIN}).")
                    validated[field] = DGMS_SAFETY_FACTOR_MIN
                else:
                    errors.append(f"{field.replace('_', ' ').title()} must be at least {min_val} (DGMS/IBM requirement).")
            elif val > max_val:
                errors.append(f"{field.replace('_', ' ').title()} exceeds maximum allowed value {max_val}.")
            else:
                validated[field] = val
        except (TypeError, ValueError):
            errors.append(f"{field.replace('_', ' ').title()} must be a number.")
    
    # Validate ore type against Indian mineral classifications
    ore_type = inputs.get('ore_type', 'generic').lower()
    valid_ore_types = ['generic', 'gold', 'copper', 'iron', 'zinc', 'lead', 'bauxite', 'chromite']
    
    if ore_type in valid_ore_types:
        validated['ore_type'] = ore_type
    else:
        validated['ore_type'] = 'generic'
        dgms_warnings.append(f"Ore type '{ore_type}' not recognized. Using 'generic' instead.")
    
    # Check for specific regulatory compliance
    if 'dip_angle' in validated and 'rqd' in validated:
        dip = validated['dip_angle']
        rqd = validated['rqd']
        
        # Check for DGMS special conditions
        if dip > 60 and rqd < 70:
            dgms_warnings.append("DGMS Safety Alert: High dip angle with moderate RQD requires additional ground support.")
        
        if dip < 20 and validated.get('mining_depth', 0) > 500:
            dgms_warnings.append("DGMS Compliance Note: Shallow dip at depth may require specialized support systems.")
    
    if errors:
        return {'valid': False, 'message': '\n'.join(errors)}
    
    # Include any warnings in the result
    if dgms_warnings:
        validated['dgms_warnings'] = dgms_warnings
        
    return {'valid': True, 'data': validated, 'warnings': dgms_warnings}

def load_rock_properties(file_path):
    """
    Load rock properties from a JSON file containing Indian rock mass classification data.
    """
    try:
        with open(file_path, 'r') as file:
            rock_properties = json.load(file)
        return rock_properties
    except Exception as e:
        print(f"Error loading rock properties: {e}")
        return None
