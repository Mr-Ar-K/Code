from stability_analysis import (
    determine_stope_type,
    calculate_stope_dimensions,
    assess_stability,
)
from cost_estimation import estimate_mining_costs

REQUIRED_FIELDS = [
    'dip_angle', 'ore_thickness', 'rqd', 'mining_depth', 'safety_factor'
]

def validate_inputs(inputs):
    missing = [f for f in REQUIRED_FIELDS if f not in inputs or inputs[f] is None]
    if missing:
        return False, f"Missing or invalid fields: {', '.join(missing)}."
    return True, None

def calculate_stope_design(inputs):
    valid, error = validate_inputs(inputs)
    if not valid:
        return {'error': error}

    # Add ore_type and stope_type to inputs for cost estimation
    stope_type = determine_stope_type(inputs)
    inputs['stope_type'] = stope_type
    dimensions = calculate_stope_dimensions(inputs)
    stability = assess_stability(inputs, dimensions)
    costs = estimate_mining_costs(inputs, dimensions)

    return {
        'stope_type': stope_type,
        'dimensions': dimensions,
        'stability': stability,
        'costs': costs
    }

def summarize_results(results):
    if 'error' in results:
        return f"Error: {results['error']}"
    summary = (
        f"Stope Type: {results['stope_type']}\n"
        f"Dimensions: {results['dimensions']}\n"
        f"Stability: {results['stability']}\n"
        f"Estimated Costs: {results['costs']}\n"
    )
    return summary
