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

# Indian Mining Standards constants
DGMS_SAFETY_FACTOR_MIN = 1.5
DGMS_PILLAR_WIDTH_MIN = 3.0
CMRI_RMR_ADJUSTMENT = 5
IBE_STRESS_FACTOR = 0.028

# Asynchronous rendering configuration
ENABLE_ASYNC_3D = True
_3D_EXECUTOR = ThreadPoolExecutor(max_workers=1)

# Visualization quality settings
MAX_PIXEL_WIDTH = 2000  # Maximum pixel width for any image
MAX_PIXEL_HEIGHT = 1500  # Maximum pixel height for any image
BASE_DPI = 150          # Default DPI for simple plots
LOW_DPI = 100           # DPI for complex plots or low-end systems
MAX_DPI = 300           # Maximum DPI for high-quality outputs

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
_viz_logger = logging.getLogger('visualization')

def _save_fig(fig, filepath, max_w=MAX_PIXEL_WIDTH, max_h=MAX_PIXEL_HEIGHT, base_dpi=BASE_DPI, 
             facecolor='white', edgecolor='none'):
    """
    Save a figure with adaptive DPI to control maximum pixel dimensions.
    This prevents memory issues on low-end systems while maintaining quality.
    
    Args:
        fig: matplotlib figure object
        filepath: output file path
        max_w: maximum width in pixels
        max_h: maximum height in pixels
        base_dpi: base DPI value before adjustment
        facecolor: figure face color
        edgecolor: figure edge color
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Get figure dimensions in inches
    fig_w, fig_h = fig.get_size_inches()
    
    # Calculate DPI needed to stay under pixel limits
    dpi_w = max_w / fig_w
    dpi_h = max_h / fig_h
    
    # Choose the minimum DPI that satisfies constraints
    dpi_final = min(base_dpi, dpi_w, dpi_h)
    
    # Round to integer
    dpi_final = int(max(LOW_DPI, min(dpi_final, MAX_DPI)))
    
    _viz_logger.info(f"Saving {filepath} with dimensions {fig_w:.1f}x{fig_h:.1f}in at {dpi_final} DPI")
    
    # Save with calculated DPI
    # Use tight_bbox but catch warnings about tight layout issues
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fig.savefig(filepath, dpi=dpi_final, bbox_inches='tight', 
                   facecolor=facecolor, edgecolor=edgecolor)

def _prism_faces(vertices):
    """
    Create a consistent set of faces for a rectangular prism.
    Args:
        vertices: list of 8 points in the following order:
            [0-3] bottom face corners
            [4-7] corresponding top face corners
    Returns:
        List of faces, each face is a list of vertices
    """
    return [
        [vertices[i] for i in (0, 1, 2, 3)],  # bottom face
        [vertices[i] for i in (4, 5, 6, 7)],  # top face
        [vertices[i] for i in (0, 1, 5, 4)],  # front face
        [vertices[i] for i in (1, 2, 6, 5)],  # right face
        [vertices[i] for i in (2, 3, 7, 6)],  # back face
        [vertices[i] for i in (3, 0, 4, 7)],  # left face
    ]

def determine_stope_type(inputs):
    dip = inputs['dip_angle']
    rqd = inputs['rqd']
    depth = inputs.get('mining_depth', 300)
    
    # Enhanced classification with realistic Indian mining practices
    if dip > 60 and rqd > 80 and depth < 800:
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
    rqd = max(0, min(100, inputs['rqd']))
    dip_angle = inputs['dip_angle']
    safety_factor = DGMS_SAFETY_FACTOR_MIN  # Always use minimum as per DGMS, not from user input
    ore_thickness = max(0.1, inputs.get('ore_thickness', 1))
    depth = inputs.get('mining_depth', 300)
    stope_type = determine_stope_type(inputs)

    # Calculate Rock Mass Rating with Indian CMRI adjustment
    rmr = 0.77 * rqd + 12 + CMRI_RMR_ADJUSTMENT

    # Calculate Q-value
    jn = 9
    jr = 2
    ja = 1
    jw = 1
    srf = 2.5
    q_value = (rqd/100) * (jr/ja) * (jw/srf)

    # Modified Stability Number calculation
    nirm_factor = 0.85 if depth > 500 else 1.0
    a_factor = 1.0 * nirm_factor
    b_factor = max(0.2, min(1.0, 0.3 + ((dip_angle - 20) / 70)))
    c_factor = 8 - 7 * (math.cos(math.radians(dip_angle)))
    n_prime = q_value * a_factor * b_factor * c_factor

    # Realistic dimensions based on stope type and mining standards
    if stope_type == "Sublevel Stoping":
        width = max(15, min(25, 12 + (rmr/10)))
        length = max(40, min(80, width * 2.5 + (ore_thickness * 2)))
        height = max(20, min(60, width * 1.8 + (depth/100)))
    elif stope_type == "Room-and-Pillar":
        width = max(6, min(12, 8 + (rmr/15)))
        length = max(20, min(50, width * 3 + ore_thickness))
        height = max(3, min(8, ore_thickness * 1.5 + 2))
    elif stope_type == "Cut-and-Fill":
        width = max(8, min(15, 10 + (rmr/12)))
        length = max(30, min(60, width * 2.8))
        height = max(4, min(12, 3 + ore_thickness))
    elif stope_type == "Shrinkage Stoping":
        width = max(4, min(8, 5 + (rmr/20)))
        length = max(20, min(40, width * 4))
        height = max(15, min(50, width * 3))
    elif stope_type == "Vertical Crater Retreat":
        width = max(20, min(35, 25 + (rmr/8)))
        length = max(50, min(100, width * 2.2))
        height = max(30, min(80, width * 1.6))
    else:
        width = max(DGMS_PILLAR_WIDTH_MIN, round(8 + (rmr/10), 2))
        length = round(width * 2.5, 2)
        height = round(width * 1.2, 2)

    # Apply safety factor adjustments
    width = round(width * safety_factor * 0.8, 2)
    length = round(length, 2)
    height = round(height, 2)
    volume = round(length * width * height, 2)

    return {
        'length': length,
        'width': width,
        'height': height,
        'volume': volume,
        'hydraulic_radius': round((width * height) / (2 * (width + height)), 2),
        'stability_number': round(n_prime, 2),
        'rmr': round(rmr, 2),
        'stope_type': stope_type
    }

def assess_stability(inputs, dimensions):
    mining_depth = max(0.1, inputs['mining_depth'])
    rqd = max(0, min(100, inputs['rqd']))
    ore_thickness = max(0.1, inputs.get('ore_thickness', 1))

    # Calculate in-situ stress
    vertical_stress = mining_depth * IBE_STRESS_FACTOR

    # K-ratio for Indian Shield conditions
    if mining_depth < 300:
        k_ratio = 1.5
    else:
        k_ratio = 0.5 + (1.5 / (mining_depth/100))
    
    k_ratio = min(2.0, max(0.5, k_ratio))
    horizontal_stress = vertical_stress * k_ratio

    # Rock mass strength calculation
    cimfr_factor = 0.85
    ucs = 20 + (rqd * 0.8)
    gsi = rqd * 0.8
    mi = 10
    mb = mi * math.exp((gsi - 100)/28) * cimfr_factor
    s = math.exp((gsi - 100)/9) * cimfr_factor
    
    rock_strength = ucs * math.sqrt(mb * s)
    adjusted_strength = rock_strength * (1 + 0.02 * ore_thickness)
    
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

    # Generate enhanced visualizations
    generate_enhanced_stope_visualizations(dimensions, inputs, safety_factor, vertical_stress, horizontal_stress, adjusted_strength)
    
    return {
        'safety_factor': safety_factor,
        'stability_class': stability_class,
        'vertical_stress': round(vertical_stress, 2),
        'horizontal_stress': round(horizontal_stress, 2),
        'rock_strength': round(adjusted_strength, 2),
        'dgms_compliant': safety_factor >= DGMS_SAFETY_FACTOR_MIN
    }

def generate_enhanced_stope_visualizations(dimensions, inputs, safety_factor, vertical_stress, horizontal_stress, rock_strength):
    """Generate comprehensive realistic stope visualizations"""
    os.makedirs('reports', exist_ok=True)
    
    stope_type = dimensions.get('stope_type', determine_stope_type(inputs))
    width = dimensions['width']
    height = dimensions['height'] 
    length = dimensions['length']
    depth = inputs.get('mining_depth', 300)
    
    # Generate multiple visualization views
    if ENABLE_ASYNC_3D:
        # Run 3D visualization asynchronously to avoid freezing the UI
        _viz_logger.info("Starting async 3D visualization rendering...")
        _3D_EXECUTOR.submit(_generate_3d_isometric_view, width, height, length, depth, stope_type)
    else:
        create_3d_isometric_view(width, height, length, depth, stope_type)
    
    # These views are simpler and can run in the main thread
    create_cross_section_view(width, height, length, depth, stope_type, inputs)
    create_plan_view(width, length, stope_type)
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
    """
    3-D representation of cut-and-fill stoping.
    Uses alternating ore (excavated slice) and waste (fill) colours.
    """
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
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))  # reduced size
    
    # Longitudinal section
    ax1.add_patch(plt.Rectangle((0, -depth), length, height, 
                               facecolor='gold', alpha=0.7, edgecolor='black', linewidth=2))

    # Draw at most 3 geological layers for clarity
    max_layers = min(3, inputs.get('num_layers', 4))
    for i in range(1, max_layers+1):
        layer_depth = -depth - (i * 50)
        ax1.axhline(y=layer_depth, color='brown', linestyle='--', alpha=0.6)
        if i == 1:  # Only label the first layer to reduce clutter
            ax1.text(length/2, layer_depth-10, f'Geological Layer {i}', ha='center', fontsize=9)

    # Cross section
    ax2.add_patch(plt.Rectangle((0, -depth), width, height,
                               facecolor='gold', alpha=0.7, edgecolor='black', linewidth=2))

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
    
    # Manually adjust margins to avoid excessive layout expansion
    fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.1)
    
    # Save with adaptive DPI
    _save_fig(fig, 'reports/stope_cross_sections.png', base_dpi=150)
    plt.close()

def create_plan_view(width, length, stope_type):
    """Create plan view showing stope layout"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    if stope_type == "Room-and-Pillar":
        # Create room and pillar grid pattern
        pillar_size = min(width, length) * 0.25
        room_size = min(width, length) * 0.35
        
        # Draw rooms and pillars using np.arange for precise spacing
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
        # Single large stope
        main_stope = plt.Rectangle((0, 0), length, width,
                                 facecolor='gold', alpha=0.7, edgecolor='black', linewidth=3)
        ax.add_patch(main_stope)
        ax.text(length/2, width/2, f'{stope_type.upper()}\nSTOPE',
               ha='center', va='center', fontsize=14, weight='bold')
    
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
    
    # Add dimensions
    ax.annotate('', xy=(0, -width*0.1), xytext=(length, -width*0.1),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(length/2, -width*0.15, f'Length: {length}m', ha='center', 
           fontsize=12, color='red', weight='bold')
    
    ax.annotate('', xy=(-length*0.1, 0), xytext=(-length*0.1, width),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(-length*0.15, width/2, f'Width: {width}m', rotation=90, ha='center', va='center',
           fontsize=12, color='red', weight='bold')
    
    ax.set_title(f'{stope_type} - Plan View Layout', fontsize=16, weight='bold', pad=20)
    ax.set_xlabel('Length (m)', fontsize=12)
    ax.set_ylabel('Width (m)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    # Set limits with margin
    ax.set_xlim(-length*0.2, length*1.1)
    ax.set_ylim(-width*0.2, width*1.1)
    
    # Use subplots_adjust instead of tight_layout to avoid warnings
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
    theta = np.linspace(0, np.pi, 100)
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
    
    # Use subplots_adjust instead of tight_layout to avoid warnings
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
    
    # Stress distribution with depth
    depths = np.linspace(0, 1000, 50)
    v_stress = depths * IBE_STRESS_FACTOR
    h_stress = v_stress * 1.2  # Typical k-ratio
    
    ax2.plot(v_stress, depths, 'r-', linewidth=3, label='Vertical Stress', alpha=0.8)
    ax2.plot(h_stress, depths, 'b-', linewidth=3, label='Horizontal Stress', alpha=0.8)
    ax2.axhline(y=vertical_stress/IBE_STRESS_FACTOR, color='orange', linestyle=':', 
               linewidth=3, label=f'Current Depth ({vertical_stress/IBE_STRESS_FACTOR:.0f}m)')
    
    ax2.set_title('Stress Distribution with Depth', fontsize=14, weight='bold')
    ax2.set_xlabel('Stress (MPa)', fontsize=12)
    ax2.set_ylabel('Depth (m)', fontsize=12)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.invert_yaxis()
    
    # Use subplots_adjust instead of tight_layout to avoid warnings
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
        # Use subplots_adjust instead of tight_layout to avoid warnings
        fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.12)
        _save_fig(fig, 'reports/stability_analysis_plot.png')
        plt.close()
    except Exception as e:
        _viz_logger.error(f"Error generating stability analysis plot: {e}")
