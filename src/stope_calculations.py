from stability_analysis import (
    determine_stope_type,
    calculate_stope_dimensions,
    assess_stability,
    generate_enhanced_stope_visualizations,
)
from cost_estimation import estimate_mining_costs

REQUIRED_FIELDS = [
    'dip_angle', 'ore_thickness', 'rqd', 'mining_depth'
]

def validate_inputs(inputs):
    """Enhanced input validation with realistic mining parameters"""
    missing = [f for f in REQUIRED_FIELDS if f not in inputs or inputs[f] is None]
    if missing:
        return False, f"Missing or invalid fields: {', '.join(missing)}."
    
    # Additional validation for realistic mining parameters
    try:
        dip_angle = float(inputs['dip_angle'])
        ore_thickness = float(inputs['ore_thickness'])
        rqd = float(inputs['rqd'])
        mining_depth = float(inputs['mining_depth'])
        
        # Validate realistic ranges
        if not (0 <= dip_angle <= 90):
            return False, "Dip angle must be between 0 and 90 degrees."
        if not (0.3 <= ore_thickness <= 100):
            return False, "Ore thickness must be between 0.3 and 100 meters."
        if not (25 <= rqd <= 100):
            return False, "RQD must be between 25% and 100%."
        if not (5 <= mining_depth <= 2000):
            return False, "Mining depth must be between 5 and 2000 meters."
            
    except (ValueError, TypeError):
        return False, "All numerical inputs must be valid numbers."
    
    return True, None

def calculate_stope_design(inputs):
    """Enhanced stope design calculation with realistic parameters"""
    valid, error = validate_inputs(inputs)
    if not valid:
        return {'error': error}

    # Determine stope type first
    stope_type = determine_stope_type(inputs)
    inputs['stope_type'] = stope_type
    
    # Calculate dimensions (no safety_factor input)
    dimensions = calculate_stope_dimensions(inputs)
    
    # Assess stability (safety_factor is calculated inside)
    stability = assess_stability(inputs, dimensions)

    # Calculate costs based on realistic parameters
    costs = estimate_mining_costs(inputs, dimensions)

    # Generate all enhanced visualizations for GUI and PDF
    # Extract required values for visualization
    safety_factor = stability['safety_factor']
    vertical_stress = stability['vertical_stress']
    horizontal_stress = stability['horizontal_stress']
    adjusted_strength = stability['rock_strength']
    generate_enhanced_stope_visualizations(dimensions, inputs, safety_factor, vertical_stress, horizontal_stress, adjusted_strength)

    # Add stope type to dimensions for visualization
    dimensions['stope_type'] = stope_type
    
    return {
        'stope_type': stope_type,
        'dimensions': dimensions,
        'stability': stability,
        'costs': costs
    }

def summarize_results(results):
    """Enhanced results summary with detailed information"""
    if 'error' in results:
        return f"Error: {results['error']}"
    
    stope_type = results['stope_type']
    dimensions = results['dimensions']
    stability = results['stability']
    costs = results['costs']
    
    # Format dimensions nicely
    dim_text = f"L:{dimensions['length']}m × W:{dimensions['width']}m × H:{dimensions['height']}m"
    volume_text = f"Volume: {dimensions['volume']} m³"
    
    # Safety factor with compliance
    safety_factor = stability.get('safety_factor', 'N/A')
    dgms_status = "✓ DGMS Compliant" if stability.get('dgms_compliant', False) else "✗ Non-compliant"
    
    # Cost summary
    total_cost = costs.get('total', 0)
    cost_text = f"₹{total_cost:,.2f}" if total_cost > 0 else "Not calculated"
    
    summary = f"""STOPE DESIGN SUMMARY
Mining Method: {stope_type}
Dimensions: {dim_text}
{volume_text}
Safety Factor: {safety_factor} ({dgms_status})
Estimated Cost: {cost_text}
Stability Class: {stability.get('stability_class', 'Unknown')}"""
    
    return summary

def get_stope_type_characteristics(stope_type):
    """Get characteristics of different stope types for validation"""
    characteristics = {
        "Sublevel Stoping": {
            "typical_width": (15, 25),
            "typical_length": (40, 80), 
            "typical_height": (20, 60),
            "min_dip": 45,
            "min_rqd": 75,
            "description": "Large-scale method with sublevel development"
        },
        "Room-and-Pillar": {
            "typical_width": (6, 12),
            "typical_length": (20, 50),
            "typical_height": (3, 8),
            "max_dip": 30,
            "min_rqd": 50,
            "description": "Systematic extraction with support pillars"
        },
        "Cut-and-Fill": {
            "typical_width": (8, 15),
            "typical_length": (30, 60),
            "typical_height": (4, 12),
            "min_dip": 30,
            "min_rqd": 60,
            "description": "Sequential cutting and backfilling"
        },
        "Shrinkage Stoping": {
            "typical_width": (4, 8),
            "typical_length": (20, 40),
            "typical_height": (15, 50),
            "min_dip": 50,
            "min_rqd": 40,
            "description": "Ore storage method for steep deposits"
        },
        "Vertical Crater Retreat": {
            "typical_width": (20, 35),
            "typical_length": (50, 100),
            "typical_height": (30, 80),
            "min_dip": 60,
            "min_rqd": 80,
            "description": "Large-hole blasting method"
        }
    }
    return characteristics.get(stope_type, {})
