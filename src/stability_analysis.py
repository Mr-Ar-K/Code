import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import math
import os
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from concurrent.futures import ThreadPoolExecutor
import threading
import logging
import warnings

# ============================================================================
# CONSTANTS – INDIAN & INTERNATIONAL STANDARDS
# ============================================================================

DGMS_SAFETY_FACTOR_MIN = 1.5    # DGMS minimum safety factor (unitless)
DGMS_PILLAR_WIDTH_MIN  = 3.0    # DGMS minimum pillar width (m)
CMRI_RMR_ADJUSTMENT    = 5      # CMRI adjustment for Indian RMR
IBE_STRESS_FACTOR      = 0.028  # MPa/m vertical stress coefficient

HOEK_MI_DEFAULT        = 15     # Hoek–Brown intact material constant

# Barton Q-System typical parameters for Indian metal mines
Q_JOINT_SET_NUMBER     = 9
Q_JOINT_ROUGHNESS      = 2
Q_JOINT_ALTERATION     = 1
Q_WATER_FACTOR         = 1.0
Q_STRESS_REDUCTION     = 2.5

ENABLE_ASYNC_3D        = True
_3D_EXECUTOR           = ThreadPoolExecutor(max_workers=1)

MAX_PIXEL_WIDTH  = 2000
MAX_PIXEL_HEIGHT = 1500
BASE_DPI         = 150
LOW_DPI          = 100
MAX_DPI          = 300

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
_viz_logger = logging.getLogger('visualization')

# ============================================================================
# VISUALIZATION HELPERS
# ============================================================================

def _save_fig(fig, filepath, max_w=MAX_PIXEL_WIDTH, max_h=MAX_PIXEL_HEIGHT,
              base_dpi=BASE_DPI, facecolor='white', edgecolor='none'):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    w_in, h_in = fig.get_size_inches()
    dpi_needed = min(base_dpi, max_w/w_in, max_h/h_in)
    dpi_final = int(max(LOW_DPI, min(dpi_needed, MAX_DPI)))
    _viz_logger.info(f"Saving {filepath} at {dpi_final} DPI")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fig.savefig(filepath, dpi=dpi_final, bbox_inches='tight',
                    facecolor=facecolor, edgecolor=edgecolor)

def _prism_faces(vertices):
    return [
        [vertices[i] for i in (0,1,2,3)],
        [vertices[i] for i in (4,5,6,7)],
        [vertices[i] for i in (0,1,5,4)],
        [vertices[i] for i in (1,2,6,5)],
        [vertices[i] for i in (2,3,7,6)],
        [vertices[i] for i in (3,0,4,7)],
    ]

# ============================================================================
# GEOTECHNICAL FORMULAE
# ============================================================================

def calculate_rmr_standard(rqd):
    """RMR = 0.77 * RQD + 12 + CMRI adjustment"""
    return max(0, min(100, 0.77*rqd + 12 + CMRI_RMR_ADJUSTMENT))

def calculate_q_standard(rqd):
    """Q = (RQD/Jn)*(Jr/Ja)*(Jw/SRF)"""
    return (rqd/Q_JOINT_SET_NUMBER) * (Q_JOINT_ROUGHNESS/Q_JOINT_ALTERATION) * (Q_WATER_FACTOR/Q_STRESS_REDUCTION)

def calculate_stability_number_standard(q_val, dip, depth):
    """N' = Q * A * B * C"""
    # Depth Adjustment Factor (A): 1.0 if depth > 500, else 0.85
    a = 1.0 if depth > 500 else 0.85
    # Orientation Factor (B): range 0.3 to 0.7
    b = max(0.3, min(0.7, 0.3 + (dip-20)/70))
    # Gravity Factor (C): 1 - cos(theta)
    c = 1 - math.cos(math.radians(dip))
    return q_val * a * b * c

def calculate_horizontal_k_ratio_standard(depth):
    """Brown-Hoek k-ratio decreases with depth"""
    if depth<300:
        k=1.5
    else:
        k=0.65 + 1350/(depth+200)
    return min(2.0, max(0.5, k))

def calculate_ucs_from_rqd_standard(rqd):
    """UCS = 20 + 0.8 * RQD (MPa)"""
    return 20 + 0.8*rqd

def calculate_gsi_from_rqd_standard(rqd):
    """GSI = RQD - 15, bounded 20–85"""
    return max(20, min(85, rqd-15))

def calculate_hoek_brown_strength_standard(rqd):
    """Unconfined rock mass strength σcm = σci * s^a"""
    sigma_ci = calculate_ucs_from_rqd_standard(rqd)
    gsi      = calculate_gsi_from_rqd_standard(rqd)
    # Hoek-Brown disturbance factor D is assumed 0 (undisturbed rock mass)
    HOEK_D_FACTOR = 0  # If D is to be used, update accordingly
    mb       = HOEK_MI_DEFAULT * math.exp((gsi-100)/28) * (1 - HOEK_D_FACTOR)
    s        = math.exp((gsi-100)/9) * (1 - HOEK_D_FACTOR)
    a        = 0.5 + (1/6)*(math.exp(-gsi/15)-math.exp(-20/3))
    return sigma_ci * (s**a)

def calculate_hydraulic_radius_design(n_prime):
    """Mathews-Potvin piecewise hydraulic radius"""
    if n_prime<=3:    return 2.5 + 0.5*n_prime
    if n_prime<=10:   return 4.0 + 0.8*n_prime
    return 7.0 + 5.0*math.log10(n_prime)

# ============================================================================
# MAIN CALCULATION FUNCTIONS
# ============================================================================

def determine_stope_type(inputs):
    dip   = inputs['dip_angle']
    rqd   = inputs['rqd']
    depth = inputs.get('mining_depth', 300)

    # 1. Vertical Crater Retreat
    if dip > 60 and rqd >= 75 and depth < 800:
        return "Vertical Crater Retreat"
    # 2. Sublevel Stoping
    if 45 < dip <= 60 and rqd >= 75:
        return "Sublevel Stoping"
    # 3. Cut-and-Fill
    if 30 < dip <= 45 and rqd >= 60:
        return "Cut-and-Fill"
    # 4. Room-and-Pillar
    if dip <= 30 and rqd >= 50:
        return "Room-and-Pillar"
    # 5. Shrinkage Stoping
    if dip > 50 and rqd >= 40:
        return "Shrinkage Stoping"
    # 6. Default fallback
    return "Shrinkage Stoping"

def calculate_stope_dimensions(inputs):
    """
    Standards‐compliant stope dimension calculation:
      - Width = max(DGMS_PILLAR_WIDTH_MIN, 2·HR_design)
      - Length = 10 * Width
      - Height = 0.8 * Width
    """
    # Sanitize inputs
    rqd           = max(0, min(100, inputs['rqd']))
    dip_angle     = inputs['dip_angle']
    depth         = inputs.get('mining_depth', 300)
    stope_type    = determine_stope_type(inputs)

    # Classification indices
    rmr           = calculate_rmr_standard(rqd)
    q_value       = calculate_q_standard(rqd)
    n_prime       = calculate_stability_number_standard(q_value, dip_angle, depth)

    # Design hydraulic radius (Mathews–Potvin)
    hr_design     = calculate_hydraulic_radius_design(n_prime)

    # Width from stability and DGMS minimum
    width_raw     = max(DGMS_PILLAR_WIDTH_MIN, 2.0 * hr_design)

    # Corrected: Length = 10 × Width
    length_raw    = width_raw * 10

    # Corrected: Height = 0.8 × Width
    height_raw    = width_raw * 0.8

    # Apply DGMS safety adjustment on width
    safety_adj    = max(0.85, min(1.0, DGMS_SAFETY_FACTOR_MIN/1.5*0.9))
    width         = round(width_raw * safety_adj, 2)
    # Use adjusted width for both length and height
    length        = round(width * 10, 2)
    height        = round(width * 0.8, 2)

    # Volume and geometric hydraulic radius
    volume        = round(width * length * height, 2)
    hr_geometric  = round((width * height) / (2 * (width + height)), 2)

    return {
        'length': length,
        'width': width,
        'height': height,
        'volume': volume,
        'hydraulic_radius': hr_geometric,
        'design_hydraulic_radius': round(hr_design, 2),
        'stability_number': round(n_prime, 2),
        'rmr': round(rmr, 2),
        'q_value': round(q_value, 2),
        'stope_type': stope_type
    }

def assess_stability(inputs, dims):
    depth   = max(0.1, inputs['mining_depth'])
    rqd     = max(0, min(100, inputs['rqd']))
    ore_t   = max(0.1, inputs.get('ore_thickness',1))

    # Calculate stresses using IBE and Brown-Hoek formulas
    sig_v   = depth * IBE_STRESS_FACTOR
    k_ratio = calculate_horizontal_k_ratio_standard(depth)
    sig_h   = sig_v * k_ratio

    # Compute rock mass strength per Hoek-Brown criterion
    rock_s  = calculate_hoek_brown_strength_standard(rqd)
    # Apply empirical ore thickness adjustment (empirical factor)
    rock_s *= (1 + 0.015*math.log(ore_t+1))

    sf      = round(rock_s/sig_v,2)
    if sf< DGMS_SAFETY_FACTOR_MIN: cls="Unstable (<DGMS)"
    elif sf<2.0:                  cls="Marginal"
    elif sf<2.5:                  cls="Stable"
    else:                         cls="Highly Stable"

    generate_enhanced_stope_visualizations(dims, inputs, sf, sig_v, sig_h, rock_s)
    return {
        'safety_factor': sf,
        'stability_class': cls,
        'vertical_stress': round(sig_v,2),
        'horizontal_stress': round(sig_h,2),
        'k_ratio': round(k_ratio,2),
        'rock_strength': round(rock_s,2),
        'dgms_compliant': sf>=DGMS_SAFETY_FACTOR_MIN
    }

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def generate_enhanced_stope_visualizations(dimensions, inputs, safety_factor,
                                           vertical_stress, horizontal_stress,
                                           rock_strength):
    os.makedirs('reports', exist_ok=True)
    stope_type = dimensions.get('stope_type', determine_stope_type(inputs))
    w, h, L = dimensions['width'], dimensions['height'], dimensions['length']
    d = inputs.get('mining_depth',300)

    if ENABLE_ASYNC_3D:
        _viz_logger.info("Starting async 3D visualization rendering...")
        _3D_EXECUTOR.submit(_generate_3d_isometric_view, w, h, L, d, stope_type)
    else:
        create_3d_isometric_view(w, h, L, d, stope_type)

    create_cross_section_view(w, h, L, d, stope_type, inputs)
    create_plan_view(w, L, stope_type, inputs)
    generate_safety_factor_gauge(safety_factor)
    create_stress_analysis_chart(vertical_stress, horizontal_stress, rock_strength)

def _generate_3d_isometric_view(width, height, length, depth, stope_type):
    """Background worker function for 3D rendering"""
    try:
        _viz_logger.info(f"Starting 3D isometric view generation for {stope_type}...")
        create_3d_isometric_view(width, height, length, depth, stope_type)
        _viz_logger.info("3D isometric view completed successfully")
    except Exception as e:
        _viz_logger.error(f"Error in 3D visualization: {e}")

def create_3d_isometric_view(width, height, length, depth, stope_type):
    """Create realistic 3D isometric view of the stope"""
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Define colors for different rock types
    ore_color = '#FFD700'  # Gold
    waste_color = '#8B7355'  # Brown
    support_color = '#708090'  # Gray
    
    if stope_type == "Sublevel Stoping":
        create_sublevel_stoping_3d(ax, width, height, length, depth, ore_color, waste_color)
    elif stope_type == "Room-and-Pillar":
        create_room_pillar_3d(ax, width, height, length, depth, ore_color, support_color)
    elif stope_type == "Cut-and-Fill":
        create_cut_fill_3d(ax, width, height, length, depth, ore_color, waste_color)
    elif stope_type == "Shrinkage Stoping":
        create_shrinkage_3d(ax, width, height, length, depth, ore_color)
    elif stope_type == "Vertical Crater Retreat":
        create_vcr_3d(ax, width, height, length, depth, ore_color)
    
    # Add underground context
    add_underground_infrastructure(ax, width, height, length, depth)
    
    # Set labels and title
    ax.set_xlabel('Length (m)', fontsize=10)
    ax.set_ylabel('Width (m)', fontsize=10)
    ax.set_zlabel('Height (m)', fontsize=10)
    ax.set_title(f'{stope_type} - 3D Isometric View\nDepth: {depth}m | Dimensions: {length}×{width}×{height}m', 
                fontsize=12, fontweight='bold')
    
    # Add depth reference
    ax.text2D(0.02, 0.98, f'Mining Depth: {depth}m below surface', 
              transform=ax.transAxes, fontsize=10, 
              bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
              verticalalignment='top')
    
    # Set viewing angle for best perspective
    ax.view_init(elev=20, azim=45)
    
    # Don't use tight_layout for 3D plots as it can cause warnings
    # Instead, adjust the figure dimensions as needed
    fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    
    # Use adaptive DPI for 3D renders
    _save_fig(fig, 'reports/stope_3d_isometric.png', base_dpi=200)
    plt.close()

def create_sublevel_stoping_3d(ax, width, height, length, depth, ore_color, waste_color):
    """Create 3D representation of sublevel stoping"""
    vertices = [
        [0, 0, 0], [length, 0, 0], [length, width, 0], [0, width, 0],
        [0, 0, height], [length, 0, height], [length, width, height], [0, width, height]
    ]
    faces = _prism_faces(vertices)
    sublevel_height = min(15, height/3)
    num_sublevels = int(height / sublevel_height)
    for i in range(1, num_sublevels):
        z = i * sublevel_height
        bench_x = [0, length, length, 0, 0]
        bench_y = [width*0.1, width*0.1, width*0.9, width*0.9, width*0.1]
        bench_z = [z, z, z, z, z]
        ax.plot(bench_x, bench_y, bench_z, 'r-', linewidth=2, alpha=0.8)
    ax.add_collection3d(Poly3DCollection(faces, facecolors=ore_color, edgecolors='black', alpha=0.6, linewidths=0.6))

def create_room_pillar_3d(ax, width, height, length, depth, ore_color, support_color):
    """Create 3D representation of room and pillar mining"""
    pillar_width = max(3, width * 0.4)
    room_width = width - pillar_width
    num_rooms = max(1, int(length / (room_width + pillar_width)))
    for i in range(num_rooms):
        x_start = i * (room_width + pillar_width)
        x_end = x_start + room_width
        if x_end <= length:
            room_vertices = [
                [x_start, 0, 0], [x_end, 0, 0], [x_end, width, 0], [x_start, width, 0],
                [x_start, 0, height], [x_end, 0, height], [x_end, width, height], [x_start, width, height]
            ]
            room_faces = _prism_faces(room_vertices)
            ax.add_collection3d(Poly3DCollection(room_faces, facecolors=ore_color, edgecolors='black', alpha=0.6, linewidths=0.6))
        if i < num_rooms - 1:
            pillar_start = x_end
            pillar_end = pillar_start + pillar_width
            if pillar_end <= length:
                pillar_vertices = [
                    [pillar_start, 0, 0], [pillar_end, 0, 0], [pillar_end, width, 0], [pillar_start, width, 0],
                    [pillar_start, 0, height], [pillar_end, 0, height], [pillar_end, width, height], [pillar_start, width, height]
                ]
                pillar_faces = _prism_faces(pillar_vertices)
                ax.add_collection3d(Poly3DCollection(pillar_faces, facecolors=support_color, edgecolors='black', alpha=0.8, linewidths=0.6))

def create_cut_fill_3d(ax, width, height, length, depth, ore_color, waste_color):
    """3-D representation of cut-and-fill stoping"""
    slice_height = max(2, height / 6)
    num_slices   = int(math.ceil(height / slice_height))
    for i in range(num_slices):
        z_bottom = i * slice_height
        z_top    = min(height, z_bottom + slice_height * 0.7)
        slice_vertices = [
            [0,      0,      z_bottom],
            [length, 0,      z_bottom],
            [length, width,  z_bottom],
            [0,      width,  z_bottom],
            [0,      0,      z_top],
            [length, 0,      z_top],
            [length, width,  z_top],
            [0,      width,  z_top]
        ]
        slice_faces = _prism_faces(slice_vertices)
        face_colour = ore_color if i % 2 == 0 else waste_color
        ax.add_collection3d(
            Poly3DCollection(slice_faces, facecolors=face_colour, edgecolors='black', linewidths=0.6, alpha=0.7)
        )

def create_shrinkage_3d(ax, width, height, length, depth, ore_color):
    """Create 3D representation of shrinkage stoping"""
    vertices = [
        [0, 0, 0], [length, 0, 0], [length, width, 0], [0, width, 0],
        [0, 0, height], [length, 0, height], [length, width, height], [0, width, height]
    ]
    faces = _prism_faces(vertices)
    storage_height = height * 0.6
    ax.add_collection3d(Poly3DCollection(faces, facecolors=ore_color, edgecolors='black', alpha=0.5, linewidths=0.6))
    for i in range(20):
        x = np.random.uniform(0, length)
        y = np.random.uniform(0, width)
        z = np.random.uniform(0, storage_height)
        ax.scatter(x, y, z, c='orange', s=30, alpha=0.8)

def create_vcr_3d(ax, width, height, length, depth, ore_color):
    """Create 3D representation of Vertical Crater Retreat"""
    vertices = [
        [0, 0, 0], [length, 0, 0], [length, width, 0], [0, width, 0],
        [0, 0, height], [length, 0, height], [length, width, height], [0, width, height]
    ]
    faces = _prism_faces(vertices)
    ax.add_collection3d(Poly3DCollection(faces, facecolors=ore_color, edgecolors='black', alpha=0.6, linewidths=0.6))
    hole_spacing = max(3, min(width, length) / 8)
    for x in np.arange(hole_spacing, length, hole_spacing):
        for y in np.arange(hole_spacing, width, hole_spacing):
            ax.plot([x, x], [y, y], [0, height], 'r-', linewidth=3, alpha=0.8)

def add_underground_infrastructure(ax, width, height, length, depth):
    """Add realistic underground mining infrastructure"""
    drift_width = 4
    drift_height = 4
    drift_y = -drift_width - 2
    drift_vertices = [
        [-5, drift_y, 0], [length+5, drift_y, 0], 
        [length+5, drift_y+drift_width, 0], [-5, drift_y+drift_width, 0],
        [-5, drift_y, drift_height], [length+5, drift_y, drift_height],
        [length+5, drift_y+drift_width, drift_height], [-5, drift_y+drift_width, drift_height]
    ]
    drift_faces = _prism_faces(drift_vertices)
    ax.add_collection3d(Poly3DCollection(drift_faces, facecolors='lightgray', edgecolors='black', alpha=0.8, linewidths=0.6))
    raise_x = length + 8
    raise_y = width / 2
    ax.plot([raise_x, raise_x], [raise_y, raise_y], [0, height*1.5], 'b-', linewidth=6, alpha=0.8, label='Ventilation Raise')
    orepass_x = -3
    orepass_y = width / 2
    ax.plot([orepass_x, orepass_x], [orepass_y, orepass_y], [0, height], 'g-', linewidth=4, alpha=0.8, label='Ore Pass')
    ax.legend(loc='upper left', bbox_to_anchor=(0, 1))

def create_cross_section_view(width, height, length, depth, stope_type, inputs):
    """Create detailed cross-section view"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))

    # Longitudinal section
    ax1.add_patch(plt.Rectangle((0, -depth), length, height, 
                               facecolor='gold', alpha=0.7, edgecolor='black', linewidth=2))

    # Draw ore-body layer in cross-section at face
    ore_t = inputs.get('ore_thickness', 1)
    ax1.add_patch(
        plt.Rectangle((0, -depth), length, ore_t,
                     facecolor='orange', alpha=0.5, edgecolor='none',
                     label=f'Orebody ({ore_t} m)')
    )
    ax1.legend(loc='upper right')

    # Draw geological layer
    layer_depth = -depth - 50
    ax1.axhline(y=layer_depth, color='brown', linestyle='--', alpha=0.6)
    ax1.text(length/2, layer_depth-10, 'Geological Layer 1', ha='center', fontsize=9)

    # Cross section
    ax2.add_patch(plt.Rectangle((0, -depth), width, height,
                               facecolor='gold', alpha=0.7, edgecolor='black', linewidth=2))

    # Draw ore-body layer in cross-section ax2
    ax2.add_patch(
        plt.Rectangle((0, -depth), width, ore_t,
                     facecolor='orange', alpha=0.5, edgecolor='none')
    )

    # Add support elements based on stope type
    if stope_type == "Room-and-Pillar":
        pillar_width = width * 0.3
        ax2.add_patch(plt.Rectangle((width*0.35, -depth), pillar_width, height,
                                   facecolor='gray', alpha=0.9, edgecolor='black'))

    # Add dimensions
    ax1.annotate('', xy=(0, -depth+height+10), xytext=(length, -depth+height+10),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax1.text(length/2, -depth+height+20, f'Length: {length}m', 
            ha='center', fontsize=12, color='red', weight='bold')

    ax2.annotate('', xy=(0, -depth+height+10), xytext=(width, -depth+height+10),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax2.text(width/2, -depth+height+20, f'Width: {width}m', 
            ha='center', fontsize=12, color='red', weight='bold')

    ax1.annotate('', xy=(-20, 0), xytext=(-20, -depth),
                arrowprops=dict(arrowstyle='<->', color='blue', lw=2))
    ax1.text(-40, -depth/2, f'Depth: {depth}m', rotation=90,
            ha='center', va='center', fontsize=12, color='blue', weight='bold')

    # Set titles and labels
    ax1.set_title(f'{stope_type} - Longitudinal Section', fontsize=14, weight='bold')
    ax2.set_title(f'{stope_type} - Cross Section', fontsize=14, weight='bold')
    
    ax1.set_xlabel('Length (m)')
    ax1.set_ylabel('Elevation (m)')
    ax2.set_xlabel('Width (m)')
    ax2.set_ylabel('Elevation (m)')
    
    # Add grid
    ax1.grid(True, alpha=0.3)
    ax2.grid(True, alpha=0.3)
    
    # Set equal aspect ratio
    ax1.set_aspect('equal')
    ax2.set_aspect('equal')
    
    # Manually adjust margins
    fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.1)
    
    # Set tight y-limits to remove blank space below
    y_min = -depth - 10
    y_max = height + 20
    ax1.set_ylim(y_min, y_max)
    ax2.set_ylim(y_min, y_max)

    _save_fig(fig, 'reports/stope_cross_sections.png', base_dpi=100)
    plt.close()

def create_plan_view(width, length, stope_type, inputs):
    """Create plan view showing stope layout"""
    fig, ax = plt.subplots(figsize=(12, 8))
    # Orebody thickness footprint
    ore_t = inputs.get('ore_thickness', 1)
    # Draw orebody footprint centered in width
    ax.add_patch(
        plt.Rectangle((0, (width-ore_t)/2), length, ore_t,
                     facecolor='orange', alpha=0.5, edgecolor='none',
                     label=f'Orebody ({ore_t} m)')
    )
    ax.legend(loc='upper right')

    if stope_type == "Room-and-Pillar":
        # Create room and pillar grid pattern
        pillar_size = min(width, length) * 0.25
        room_size = min(width, length) * 0.35
        
        step = room_size + pillar_size
        for i in np.arange(0, length, step):
            for j in np.arange(0, width, step):
                # Room
                if i + room_size <= length and j + room_size <= width:
                    room = plt.Rectangle((i, j), room_size, room_size,
                                       facecolor='gold', alpha=0.8, edgecolor='black')
                    ax.add_patch(room)
                    ax.text(i + room_size/2, j + room_size/2, 'ROOM',
                           ha='center', va='center', fontsize=8, weight='bold')
                
                # Pillar
                pillar_x = i + room_size
                pillar_y = j + room_size
                if pillar_x + pillar_size <= length and pillar_y + pillar_size <= width:
                    pillar = plt.Rectangle((pillar_x, pillar_y), pillar_size, pillar_size,
                                         facecolor='gray', alpha=0.9, edgecolor='black')
                    ax.add_patch(pillar)
                    ax.text(pillar_x + pillar_size/2, pillar_y + pillar_size/2, 'PILLAR',
                           ha='center', va='center', fontsize=6, weight='bold')
    else:
        # Single large stope - show actual calculated dimensions
        main_stope = plt.Rectangle((0, 0), length, width,
                                 facecolor='gold', alpha=0.7, edgecolor='black', linewidth=3)
        ax.add_patch(main_stope)
        
        # Add dimension text with formula explanation
        ax.text(length/2, width/2, f'{stope_type.upper()}\nSTOPE\n\nL = {length}m (W × 10)\nW = {width}m',
               ha='center', va='center', fontsize=12, weight='bold',
               bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.9))
        
        # Add corner reinforcement symbols
        corner_size = min(length, width) * 0.05
        corners = [(0, 0), (length-corner_size, 0), (length-corner_size, width-corner_size), (0, width-corner_size)]
        for x, y in corners:
            corner = plt.Rectangle((x, y), corner_size, corner_size,
                                 facecolor='red', alpha=0.8, edgecolor='black')
            ax.add_patch(corner)
    
    # Add access infrastructure
    # Main drift
    drift_width = min(width, length) * 0.1
    drift = plt.Rectangle((-drift_width, width/2 - drift_width/2), drift_width, drift_width,
                         facecolor='lightgray', edgecolor='black')
    ax.add_patch(drift)
    ax.text(-drift_width/2, width/2, 'ACCESS\nDRIFT', ha='center', va='center', 
           fontsize=8, weight='bold', rotation=90)
    
    # Ore pass
    orepass = plt.Circle((length*0.1, width*0.9), 1, facecolor='green', edgecolor='black')
    ax.add_patch(orepass)
    ax.text(length*0.1, width*0.9 + 3, 'ORE PASS', ha='center', fontsize=8, weight='bold')
    
    # Ventilation raise
    vent_raise = plt.Circle((length*0.9, width*0.1), 1, facecolor='blue', edgecolor='black')
    ax.add_patch(vent_raise)
    ax.text(length*0.9, width*0.1 - 3, 'VENT RAISE', ha='center', fontsize=8, weight='bold')
    
    # Add dimensions with formulas
    ax.annotate('', xy=(0, -width*0.1), xytext=(length, -width*0.1),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(length/2, -width*0.15, f'Length: {length}m (Width × 10)', ha='center', 
           fontsize=12, color='red', weight='bold',
           bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9))
    
    ax.annotate('', xy=(-length*0.1, 0), xytext=(-length*0.1, width),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(-length*0.15, width/2, f'Width: {width}m (2 × HR)', rotation=90, ha='center', va='center',
           fontsize=12, color='red', weight='bold',
           bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9))
    
    ax.set_title(f'{stope_type} - Plan View (Standard Dimensions)', fontsize=16, weight='bold', pad=20)
    ax.set_xlabel('Length (m)', fontsize=12)
    ax.set_ylabel('Width (m)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    # Set limits with margin
    ax.set_xlim(-length*0.2, length*1.1)
    ax.set_ylim(-width*0.2, width*1.1)
    
    fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    _save_fig(fig, 'reports/stope_plan_view.png')
    plt.close()

def generate_safety_factor_gauge(safety_factor):
    """Enhanced safety factor gauge visualization"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Gauge parameters
    gauge_max = 4
    danger_zone = 1.5
    warning_zone = 2.0
    safe_zone = 3.0
    
    # Create semicircle gauge
    r = 1.0
    
    # Background arcs
    danger_arc = np.linspace(0, (danger_zone/gauge_max) * np.pi, 50)
    warning_arc = np.linspace((danger_zone/gauge_max) * np.pi, (warning_zone/gauge_max) * np.pi, 25)
    ok_arc = np.linspace((warning_zone/gauge_max) * np.pi, (safe_zone/gauge_max) * np.pi, 25)
    excellent_arc = np.linspace((safe_zone/gauge_max) * np.pi, np.pi, 25)
    
    # Plot arcs with improved styling
    ax.plot(r * np.cos(danger_arc), r * np.sin(danger_arc), linewidth=25, 
           color='#FF4136', alpha=0.8, solid_capstyle='round')
    ax.plot(r * np.cos(warning_arc), r * np.sin(warning_arc), linewidth=25, 
           color='#FFDC00', alpha=0.8, solid_capstyle='round')
    ax.plot(r * np.cos(ok_arc), r * np.sin(ok_arc), linewidth=25, 
           color='#2ECC40', alpha=0.8, solid_capstyle='round')
    ax.plot(r * np.cos(excellent_arc), r * np.sin(excellent_arc), linewidth=25, 
           color='#0074D9', alpha=0.8, solid_capstyle='round')
    
    # Safety factor needle
    needle_value = min(safety_factor, gauge_max)
    needle_angle = (needle_value / gauge_max) * np.pi
    
    ax.arrow(0, 0, 0.8 * np.cos(needle_angle), 0.8 * np.sin(needle_angle),
             head_width=0.08, head_length=0.05, fc='black', ec='black', linewidth=3)
    
    # Center hub
    circle = plt.Circle((0, 0), 0.08, color='black', zorder=5)
    ax.add_patch(circle)
    
    # Labels and values
    ax.text(0, -0.3, f"Safety Factor: {safety_factor}", fontsize=16, ha='center', 
           weight='bold', bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.9))
    
    # Zone labels
    ax.text(r * np.cos(danger_arc[25]) * 1.3, r * np.sin(danger_arc[25]) * 1.3, 
           "UNSAFE\n< 1.5", fontsize=10, ha='center', va='center', weight='bold', color='#FF4136')
    ax.text(r * np.cos(warning_arc[12]) * 1.3, r * np.sin(warning_arc[12]) * 1.3, 
           "MARGINAL\n1.5-2.0", fontsize=10, ha='center', va='center', weight='bold', color='#B8860B')
    ax.text(r * np.cos(ok_arc[12]) * 1.3, r * np.sin(ok_arc[12]) * 1.3, 
           "STABLE\n2.0-3.0", fontsize=10, ha='center', va='center', weight='bold', color='#228B22')
    ax.text(r * np.cos(excellent_arc[12]) * 1.3, r * np.sin(excellent_arc[12]) * 1.3, 
           "EXCELLENT\n> 3.0", fontsize=10, ha='center', va='center', weight='bold', color='#0074D9')
    
    # DGMS minimum line
    dgms_angle = (DGMS_SAFETY_FACTOR_MIN / gauge_max) * np.pi
    ax.plot([0, 1.2 * np.cos(dgms_angle)], [0, 1.2 * np.sin(dgms_angle)], 
           'r--', linewidth=3, alpha=0.9)
    ax.text(1.3 * np.cos(dgms_angle), 1.3 * np.sin(dgms_angle), 
           f'DGMS Min\n({DGMS_SAFETY_FACTOR_MIN})', fontsize=9, color='red', 
           ha='center', va='center', weight='bold',
           bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    # Compliance status
    if safety_factor >= DGMS_SAFETY_FACTOR_MIN:
        status_text = "✓ DGMS COMPLIANT"
        status_color = '#2ECC40'
    else:
        status_text = "✗ BELOW DGMS STANDARD"
        status_color = '#FF4136'
    
    ax.text(0, -0.55, status_text, fontsize=14, ha='center', weight='bold', color=status_color,
           bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.9))
    
    # Set plot properties
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-0.7, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Stope Stability Safety Factor Analysis', fontsize=18, weight='bold', pad=30)
    
    fig.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.05)
    _save_fig(fig, 'reports/safety_factor_gauge.png')
    plt.close()

def create_stress_analysis_chart(vertical_stress, horizontal_stress, rock_strength):
    """Create enhanced stress vs strength comparison"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Bar chart comparison
    categories = ['Vertical\nStress', 'Horizontal\nStress', 'Rock\nStrength']
    values = [vertical_stress, horizontal_stress, rock_strength]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    bars = ax1.bar(categories, values, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
    
    # Add DGMS minimum requirement line
    dgms_min_strength = vertical_stress * DGMS_SAFETY_FACTOR_MIN
    ax1.axhline(y=dgms_min_strength, color='red', linestyle='--', linewidth=3, alpha=0.8,
               label=f'DGMS Min. Required ({dgms_min_strength:.2f} MPa)')
    
    # Value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.02,
                f'{value:.2f} MPa', ha='center', va='bottom', fontsize=12, weight='bold')
    
    ax1.set_title('Stress vs. Strength Comparison', fontsize=14, weight='bold')
    ax1.set_ylabel('Stress/Strength (MPa)', fontsize=12)
    ax1.legend(fontsize=10)
    ax1.grid(axis='y', alpha=0.3)
    
    # Stress distribution with depth using updated k-ratio
    depths = np.linspace(0, 1000, 50)
    v_stress = depths * IBE_STRESS_FACTOR
    # Use the actual k-ratio formula for horizontal stress
    h_stress = np.array([v_stress[i] * calculate_horizontal_k_ratio_standard(depths[i]) for i in range(len(depths))])
    
    ax2.plot(v_stress, depths, 'r-', linewidth=3, label='Vertical Stress', alpha=0.8)
    ax2.plot(h_stress, depths, 'b-', linewidth=3, label='Horizontal Stress (k-ratio)', alpha=0.8)
    ax2.axhline(y=vertical_stress/IBE_STRESS_FACTOR, color='orange', linestyle=':', 
               linewidth=3, label=f'Current Depth ({vertical_stress/IBE_STRESS_FACTOR:.0f}m)')
    
    # Add k-ratio annotation
    current_depth = vertical_stress/IBE_STRESS_FACTOR
    current_k = calculate_horizontal_k_ratio_standard(current_depth)
    ax2.text(max(v_stress)*0.7, current_depth + 50, f'k-ratio = {current_k:.2f}', 
             fontsize=10, weight='bold', 
             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8))
    
    ax2.set_title('Stress vs. Depth (Brown-Hoek k-ratio)', fontsize=14, weight='bold')
    ax2.set_xlabel('Stress (MPa)', fontsize=12)
    ax2.set_ylabel('Depth (m)', fontsize=12)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.invert_yaxis()
    
    fig.subplots_adjust(left=0.08, right=0.92, top=0.9, bottom=0.1, wspace=0.25)
    _save_fig(fig, 'reports/stress_strength_comparison.png')
    plt.close()

# Legacy function for backward compatibility
def generate_stability_visualization(safety_factor, vertical_stress, horizontal_stress, rock_strength):
    """Legacy wrapper for the enhanced visualization system"""
    generate_safety_factor_gauge(safety_factor)
    create_stress_analysis_chart(vertical_stress, horizontal_stress, rock_strength)

def plot_stability_analysis(stability_data):
    try:
        factors = [data['safety_factor'] for data in stability_data]
        depths = [data['depth'] for data in stability_data]
        fig = plt.figure(figsize=(10, 6))
        plt.plot(depths, factors, marker='o', linewidth=3, markersize=8, label='Safety Factor')
        plt.axhline(y=DGMS_SAFETY_FACTOR_MIN, color='r', linestyle='--', linewidth=2,
                   label=f'DGMS Minimum ({DGMS_SAFETY_FACTOR_MIN})')
        plt.title('Stability Analysis Over Depth (DGMS Standards)', fontsize=14, weight='bold')
        plt.xlabel('Depth (m)', fontsize=12)
        plt.ylabel('Safety Factor', fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.12)
        _save_fig(fig, 'reports/stability_analysis_plot.png')
        plt.close()
    except Exception as e:
        _viz_logger.error(f"Error generating stability analysis plot: {e}")
