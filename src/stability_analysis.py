import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import math
import os

# Indian Mining Standards constants
# Based on DGMS (Directorate General of Mine Safety) and MMR (Metalliferous Mines Regulations)
DGMS_SAFETY_FACTOR_MIN = 1.5  # Minimum safety factor for Indian mines
DGMS_PILLAR_WIDTH_MIN = 3.0   # Minimum pillar width in meters
CMRI_RMR_ADJUSTMENT = 5       # Central Mining Research Institute adjustment for Indian rock conditions
IBE_STRESS_FACTOR = 0.028     # Indian Bureau of Mines vertical stress factor (slightly higher than international)

def determine_stope_type(inputs):
    dip = inputs['dip_angle']
    rqd = inputs['rqd']
    
    # Improved classification with Indian mining practices in mind
    if dip > 60 and rqd > 80:
        return "Vertical Crater Retreat"
    elif dip > 45 and rqd > 75:
        return "Sublevel Stoping"
    elif 30 < dip <= 45 and rqd > 60:
        return "Cut-and-Fill"
    elif dip <= 30 and rqd > 50:
        return "Room-and-Pillar"
    else:
        return "Shrinkage Stoping"

def calculate_stope_dimensions(inputs):
    # Improved: Use ore_thickness in calculation, and check for valid values
    rqd = max(0, min(100, inputs['rqd']))  # Clamp RQD to [0, 100]
    dip_angle = inputs['dip_angle']
    safety_factor = max(DGMS_SAFETY_FACTOR_MIN, inputs['safety_factor'])  # Use DGMS minimum if specified is lower
    ore_thickness = max(0.1, inputs.get('ore_thickness', 1))  # Avoid zero

    # Calculate Rock Mass Rating (RMR) with Indian CMRI adjustment
    # CMRI adjustment accounts for tropical weathering patterns in Indian deposits
    rmr = 0.77 * rqd + 12 + CMRI_RMR_ADJUSTMENT  

    # Calculate Q-value with Indian rock mass characteristics
    jn = 9  # Typical value for moderately jointed rock
    jr = 2  # Typical value for rough, undulating joints
    ja = 1  # Typical value for unaltered joint walls
    jw = 1  # Typical value for dry conditions
    srf = 2.5  # Typical value for medium stress
    q_value = (rqd/100) * (jr/ja) * (jw/srf)

    # Modified Stability Number (N') calculation with Indian adjustments
    # NIRM (National Institute of Rock Mechanics) factor for Indian mining conditions
    nirm_factor = 0.85 if inputs['mining_depth'] > 500 else 1.0  # Deeper mines in India need more conservative designs
    
    a_factor = 1.0 * nirm_factor  # Rock stress factor with Indian adjustment
    b_factor = 0.3 + ((dip_angle - 20) / 70)  # Joint orientation factor
    b_factor = max(0.2, min(1.0, b_factor))  # Clamp to realistic range
    c_factor = 8 - 7 * (math.cos(math.radians(dip_angle)))  # Gravity adjustment factor
    n_prime = q_value * a_factor * b_factor * c_factor

    # Hydraulic radius calculation based on stability and N'
    # Adjusted for Indian rock mass conditions
    hydraulic_radius = 0
    if n_prime < 3:
        hydraulic_radius = 2.5 + (n_prime * 0.5)  # More conservative for Indian conditions
    elif n_prime < 10:
        hydraulic_radius = 4 + n_prime * 0.8
    else:
        hydraulic_radius = 7 + math.log10(n_prime) * 5

    # Apply safety factor (higher for Indian regulations)
    hydraulic_radius = hydraulic_radius * safety_factor
    
    # Convert hydraulic radius to dimensions, influenced by ore thickness
    # For Indian methods, width must not be less than DGMS minimum
    width = max(DGMS_PILLAR_WIDTH_MIN, round(hydraulic_radius * 2, 2))
    length = round(width * (1 + (0.2 * ore_thickness/10)), 2)  # Length increases with ore thickness
    height = round(width * (0.8 + (0.1 * ore_thickness/10)), 2)  # Height influenced by ore thickness
    
    volume = round(length * width * height, 2)
    return {
        'length': length,
        'width': width,
        'height': height,
        'volume': volume,
        'hydraulic_radius': round(hydraulic_radius, 2),
        'stability_number': round(n_prime, 2),
        'rmr': round(rmr, 2)  # Added Indian-adjusted RMR value
    }

def assess_stability(inputs, dimensions):
    mining_depth = max(0.1, inputs['mining_depth'])  # Avoid zero
    rqd = max(0, min(100, inputs['rqd']))
    ore_thickness = max(0.1, inputs.get('ore_thickness', 1))

    # Calculate in-situ stress based on depth using Indian Bureau of Engineering standard
    vertical_stress = mining_depth * IBE_STRESS_FACTOR  # MPa, Indian standard calculation
    
    # K-ratio based on Indian Shield measurements (Peninsular gneiss)
    # Indian continental shield has different horizontal-to-vertical stress ratios
    if mining_depth < 300:
        k_ratio = 1.5  # Higher horizontal stresses in shallow Indian mines
    else:
        k_ratio = 0.5 + (1.5 / (mining_depth/100))  # Depth-dependent k-ratio for Indian conditions
        
    k_ratio = min(2.0, max(0.5, k_ratio))  # Clamp to realistic range for Indian mines
    horizontal_stress = vertical_stress * k_ratio
    
    # Calculate rock mass strength using Hoek-Brown empirical approach with Indian standards
    # CIMFR (Central Institute of Mining and Fuel Research) adjustment
    cimfr_factor = 0.85  # Indian rock mass strength reduction factor
    
    ucs = 20 + (rqd * 0.8)  # Unconfined Compressive Strength estimation based on RQD
    gsi = rqd * 0.8  # Geological Strength Index estimation
    mi = 10  # Material constant for average rock
    mb = mi * math.exp((gsi - 100)/28) * cimfr_factor  # Reduced material constant with Indian adjustment
    s = math.exp((gsi - 100)/9) * cimfr_factor  # Rock mass constant with Indian adjustment
    
    # Rock mass strength calculation
    rock_strength = ucs * math.sqrt(mb * s)
    
    # Adjust strength based on ore thickness (thicker ore bodies are typically more stable)
    adjusted_strength = rock_strength * (1 + 0.02 * ore_thickness)
    
    # Calculate safety factor (DGMS requires minimum 1.5)
    safety_factor = round(adjusted_strength / vertical_stress, 2)
    
    # DGMS stability classification
    if safety_factor < DGMS_SAFETY_FACTOR_MIN:
        stability_class = "Unstable (Below DGMS Minimum)"
    elif safety_factor < 2.0:
        stability_class = "Marginally Stable"
    elif safety_factor < 2.5:
        stability_class = "Stable"
    else:
        stability_class = "Highly Stable"
    
    # Generate visualization of stability results
    generate_stability_visualization(safety_factor, vertical_stress, horizontal_stress, adjusted_strength)
    
    return {
        'safety_factor': safety_factor,
        'stability_class': stability_class,
        'vertical_stress': round(vertical_stress, 2),
        'horizontal_stress': round(horizontal_stress, 2),
        'rock_strength': round(adjusted_strength, 2),
        'dgms_compliant': safety_factor >= DGMS_SAFETY_FACTOR_MIN
    }

def generate_stability_visualization(safety_factor, vertical_stress, horizontal_stress, rock_strength):
    """
    Generate visualizations of stability analysis results.
    Creates plots for safety factor, stress comparison, and other relevant metrics.
    """
    os.makedirs('reports', exist_ok=True)
    
    # --- Safety Factor Gauge Chart ---
    plt.figure(figsize=(8, 4))
    
    # Define gauge ranges and colors
    gauge_min = 0
    gauge_max = 4
    danger_zone = 1.5  # DGMS minimum
    warning_zone = 2.0
    safe_zone = 3.0
    
    # Create a half-circle gauge
    theta = np.linspace(0, np.pi, 100)
    r = 1.0
    
    # Background arcs for different safety zones
    danger_arc = np.linspace(0, (danger_zone/gauge_max) * np.pi, 50)
    warning_arc = np.linspace((danger_zone/gauge_max) * np.pi, (warning_zone/gauge_max) * np.pi, 25)
    ok_arc = np.linspace((warning_zone/gauge_max) * np.pi, (safe_zone/gauge_max) * np.pi, 25)
    excellent_arc = np.linspace((safe_zone/gauge_max) * np.pi, np.pi, 25)
    
    # Plot the background arcs
    plt.plot(r * np.cos(danger_arc), r * np.sin(danger_arc), linewidth=20, color='#FF4136', alpha=0.6)  # Red for danger
    plt.plot(r * np.cos(warning_arc), r * np.sin(warning_arc), linewidth=20, color='#FFDC00', alpha=0.6)  # Yellow for warning
    plt.plot(r * np.cos(ok_arc), r * np.sin(ok_arc), linewidth=20, color='#2ECC40', alpha=0.6)  # Green for OK
    plt.plot(r * np.cos(excellent_arc), r * np.sin(excellent_arc), linewidth=20, color='#0074D9', alpha=0.6)  # Blue for excellent
    
    # Calculate needle angle based on safety factor
    if safety_factor > gauge_max:
        needle_value = gauge_max  # Cap at max
    else:
        needle_value = safety_factor
    
    needle_angle = (needle_value / gauge_max) * np.pi
    
    # Plot the needle
    plt.plot([0, 0.8 * np.cos(needle_angle)], [0, 0.8 * np.sin(needle_angle)], 'k-', linewidth=2)
    plt.plot([0], [0], 'ko', markersize=10)  # Needle pivot
    
    # Add labels
    plt.text(0, -0.2, f"Safety Factor: {safety_factor}", fontsize=12, ha='center', fontweight='bold')
    
    # Add zone labels
    plt.text(r * np.cos(danger_arc[25]), r * np.sin(danger_arc[25]), "Unsafe", fontsize=8, ha='center', va='bottom')
    plt.text(r * np.cos(warning_arc[12]), r * np.sin(warning_arc[12]), "Marginal", fontsize=8, ha='center', va='bottom')
    plt.text(r * np.cos(ok_arc[12]), r * np.sin(ok_arc[12]), "Stable", fontsize=8, ha='center', va='bottom')
    plt.text(r * np.cos(excellent_arc[12]), r * np.sin(excellent_arc[12]), "Excellent", fontsize=8, ha='center', va='bottom')
    
    # Add DGMS minimum line
    dgms_angle = (DGMS_SAFETY_FACTOR_MIN / gauge_max) * np.pi
    plt.plot([0, 1.2 * np.cos(dgms_angle)], [0, 1.2 * np.sin(dgms_angle)], 'r--')
    plt.text(1.25 * np.cos(dgms_angle), 1.25 * np.sin(dgms_angle), f"DGMS Min ({DGMS_SAFETY_FACTOR_MIN})", 
             fontsize=8, color='red', ha='center', va='center', rotation=dgms_angle*180/np.pi - 90)
    
    # Set plot properties
    plt.axis('equal')
    plt.xlim(-1.3, 1.3)
    plt.ylim(-0.3, 1.3)
    plt.axis('off')
    plt.title('Stope Stability Safety Factor', fontsize=14, pad=20)
    
    # Add stability class at the bottom
    if safety_factor < DGMS_SAFETY_FACTOR_MIN:
        class_text = "UNSTABLE (Below DGMS Requirements)"
        class_color = '#FF4136'
    elif safety_factor < 2.0:
        class_text = "MARGINALLY STABLE"
        class_color = '#FFDC00'
    elif safety_factor < 2.5:
        class_text = "STABLE"
        class_color = '#2ECC40'
    else:
        class_text = "HIGHLY STABLE"
        class_color = '#0074D9'  # Added the missing color assignment for highly stable case
    
    plt.figtext(0.5, 0.05, class_text, fontsize=12, ha='center', color=class_color, weight='bold')
    
    # Save the plot
    plt.tight_layout()
    plt.savefig('reports/safety_factor_gauge.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # --- Stress-Strength Comparison Chart ---
    plt.figure(figsize=(8, 6))
    
    # Data for bar chart
    categories = ['Vertical Stress', 'Horizontal Stress', 'Rock Strength']
    values = [vertical_stress, horizontal_stress, rock_strength]
    colors = ['#FF9500', '#FF9500', '#3498DB']  # Orange for stress, blue for strength
    
    bars = plt.bar(categories, values, color=colors, width=0.5)
    
    # Add a line for DGMS minimum strength
    min_strength = vertical_stress * DGMS_SAFETY_FACTOR_MIN
    plt.axhline(y=min_strength, color='r', linestyle='--', label=f'DGMS Min. Required Strength ({min_strength:.2f} MPa)')
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.2f} MPa', ha='center', va='bottom', fontsize=9)
    
    plt.title('Rock Strength vs. In-situ Stress', fontsize=14)
    plt.ylabel('Stress/Strength (MPa)')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    
    # Save the plot
    plt.tight_layout()
    plt.savefig('reports/stress_strength_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_stability_analysis(stability_data):
    try:
        factors = [data['safety_factor'] for data in stability_data]
        depths = [data['depth'] for data in stability_data]
        plt.figure(figsize=(10, 6))
        plt.plot(depths, factors, marker='o', label='Safety Factor')
        plt.axhline(y=DGMS_SAFETY_FACTOR_MIN, color='r', linestyle='--', label=f'DGMS Minimum ({DGMS_SAFETY_FACTOR_MIN})')
        plt.title('Stability Analysis Over Depth (DGMS Standards)')
        plt.xlabel('Depth (m)')
        plt.ylabel('Safety Factor')
        plt.legend()
        plt.grid(True)
        plt.savefig('reports/stability_analysis_plot.png', dpi=300, bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Error generating stability analysis plot: {e}")

def plot_rock_quality_histogram(rock_quality_data):
    try:
        plt.figure(figsize=(8, 5))
        plt.hist(rock_quality_data, bins=20, color='blue', alpha=0.7, edgecolor='black')
        plt.title('Rock Quality Distribution')
        plt.xlabel('Rock Quality Designation (RQD)')
        plt.ylabel('Frequency')
        plt.grid(axis='y', alpha=0.75)
        plt.savefig('reports/rock_quality_histogram.png', dpi=300, bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Error generating rock quality histogram: {e}")
