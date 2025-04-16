import os
import matplotlib
matplotlib.use('Agg')
from datetime import datetime
from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np

# Indian Mining Standards references
DGMS_REFERENCES = {
    'safety_factor': 'DGMS Tech. Circular No. 3 of 2019',
    'ventilation': 'DGMS Circular No. 01 of 2011 & Reg. 130/157 of MMR',
    'strata_control': 'MMR 2011 Regulation 111, DGMS Circular No. 3 of 2017',
    'pillar_design': 'DGMS (Tech)(SCR) Circular No. 01 of 2019'
}

def generate_summary_text(results, filename='reports/stope_summary.txt', notes=None):
    """
    Generate a text summary of stope design results and save it to a file
    
    Args:
        results (dict): The stope design calculation results
        filename (str): Path to save the text summary file
        notes (str, optional): Additional notes to include in the summary
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Get data from results
    stability = results.get('stability', {})
    dimensions = results.get('dimensions', {})
    costs = results.get('costs', {})
    dgms_warnings = results.get('dgms_warnings', [])
    
    # Create summary text
    summary = []
    summary.append("=============================================")
    summary.append("           MINING STOPE DESIGN SUMMARY       ")
    summary.append("=============================================")
    summary.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    summary.append("")
    
    # Mine configuration
    summary.append("STOPE CONFIGURATION")
    summary.append("-------------------")
    for key, value in dimensions.items():
        summary.append(f"{key.replace('_', ' ').title()}: {value}")
    summary.append("")
    
    # Stability Analysis
    summary.append("STABILITY ANALYSIS")
    summary.append("-----------------")
    
    # Safety factor with compliance indicator
    safety_factor = stability.get('safety_factor', 'N/A')
    dgms_compliant = stability.get('dgms_compliant', False)
    compliance_text = "[COMPLIANT] DGMS Compliant" if dgms_compliant else "[WARNING] Below DGMS Minimum"
    
    summary.append(f"Safety Factor: {safety_factor} ({compliance_text})")
    
    # Display other stability parameters
    for key, value in stability.items():
        if key not in ['safety_factor', 'dgms_compliant']:
            summary.append(f"{key.replace('_', ' ').title()}: {value}")
    summary.append("")
    
    # Indian Mining References
    summary.append("APPLICABLE INDIAN MINING REGULATIONS")
    summary.append("------------------------------------")
    for key, reference in DGMS_REFERENCES.items():
        summary.append(f"- {key.replace('_', ' ').title()}: {reference}")
    summary.append("")
    
    # Cost Analysis
    if costs:
        summary.append("COST ANALYSIS (IBM STANDARDS)")
        summary.append("-----------------------------")
        
        # Display total costs prominently
        if 'total' in costs:
            summary.append(f"Total Cost: INR {costs['total']}")
        
        summary.append("Cost Breakdown:")
        
        # Exclude totals from the breakdown listing
        exclude_keys = ['total']
        for key, value in costs.items():
            if key not in exclude_keys:
                summary.append(f"  - {key.replace('_', ' ').title()}: INR {value}")
        summary.append("")
    
    # DGMS Warnings & Notes
    if dgms_warnings:
        summary.append("DGMS SAFETY ALERTS & COMPLIANCE NOTES")
        summary.append("------------------------------------")
        for warning in dgms_warnings:
            summary.append(f"- {warning}")
        summary.append("")
    
    # Additional Notes
    if notes:
        summary.append("ADDITIONAL NOTES")
        summary.append("----------------")
        summary.append(notes)
    
    # Save summary to file
    with open(filename, 'w') as f:
        f.write('\n'.join(summary))
    
    return filename

def generate_pdf_report(results, filename='reports/stope_report.pdf', notes=None):
    """
    Generate a comprehensive PDF report with DGMS/MMR compliance notes and visualizations
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Get data from results
    stability = results.get('stability', {})
    dimensions = results.get('dimensions', {})
    costs = results.get('costs', {})
    dgms_warnings = results.get('dgms_warnings', [])
    
    # Create safety factor visualization
    _create_safety_factor_viz(stability)
    
    # Create stope geometry visualization
    _create_stope_geometry_viz(dimensions)
    
    # Initialize PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Mining Stope Design Report', ln=True, align='C')
    
    # Report metadata
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    
    # Mine configuration
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Stope Configuration', ln=True)
    pdf.set_font('Arial', '', 10)
    
    for key, value in dimensions.items():
        pdf.cell(0, 6, f"{key.replace('_', ' ').title()}: {value}", ln=True)
    
    # Stability Analysis
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Stability Analysis', ln=True)
    pdf.set_font('Arial', '', 10)
    
    # Safety factor with compliance indicator
    safety_factor = stability.get('safety_factor', 'N/A')
    dgms_compliant = stability.get('dgms_compliant', False)
    compliance_text = "COMPLIANT with DGMS" if dgms_compliant else "BELOW DGMS Minimum"
    
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, f"Safety Factor: {safety_factor} ({compliance_text})", ln=True)
    pdf.set_font('Arial', '', 10)
    
    # Display other stability parameters
    for key, value in stability.items():
        if key not in ['safety_factor', 'dgms_compliant']:
            pdf.cell(0, 6, f"{key.replace('_', ' ').title()}: {value}", ln=True)
    
    # Add safety factor visualization
    if os.path.exists('reports/safety_factor_viz.png'):
        pdf.ln(5)
        pdf.image('reports/safety_factor_viz.png', x=10, w=180)
    
    # Add stope geometry visualization
    if os.path.exists('reports/stope_geometry.png'):
        pdf.ln(5)
        pdf.image('reports/stope_geometry.png', x=10, w=180)
    
    # Indian Mining References
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Applicable Indian Mining Regulations', ln=True)
    pdf.set_font('Arial', '', 10)
    for key, reference in DGMS_REFERENCES.items():
        pdf.cell(0, 6, f"- {key.replace('_', ' ').title()}: {reference}", ln=True)
    
    # Cost Analysis
    if costs:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Cost Analysis (IBM Standards)', ln=True)
        pdf.set_font('Arial', '', 11)
        
        # Display total costs prominently
        if 'total' in costs:
            pdf.cell(0, 8, f"Total Cost: INR {costs['total']}", ln=True)
        
        pdf.ln(2)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, "Cost Breakdown:", ln=True)
        pdf.set_font('Arial', '', 10)
        
        # Exclude totals from the breakdown listing
        exclude_keys = ['total']
        for key, value in costs.items():
            if key not in exclude_keys:
                pdf.cell(10, 6, "", ln=0)
                pdf.cell(0, 6, f"- {key.replace('_', ' ').title()}: INR {value}", ln=True)
        
        # Add cost visualization charts
        if os.path.exists('reports/cost_breakdown_chart.png'):
            pdf.ln(5)
            pdf.image('reports/cost_breakdown_chart.png', x=10, w=180)
        
        if os.path.exists('reports/cost_components_chart.png'):
            pdf.ln(5)
            pdf.image('reports/cost_components_chart.png', x=10, w=180)
    
    # DGMS Warnings & Notes
    if dgms_warnings:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'DGMS Safety Alerts & Compliance Notes', ln=True)
        pdf.set_font('Arial', '', 11)
        for warning in dgms_warnings:
            pdf.multi_cell(0, 8, f"- {warning}")
    
    # Additional Notes
    if notes:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Additional Notes', ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 6, notes)
    
    # Save PDF
    pdf.output(filename)
    
    return filename

def _create_safety_factor_viz(stability):
    """Create a visualization for safety factor"""
    safety_factor = stability.get('safety_factor', 1.5)
    dgms_min = stability.get('dgms_minimum', 1.5)
    
    plt.figure(figsize=(10, 6))
    
    # Create a gauge chart for safety factor
    categories = ['Critical', 'Warning', 'Acceptable', 'Excellent']
    colors = ['#FF4136', '#FF851B', '#FFDC00', '#2ECC40']
    
    # Define gauge thresholds
    thresholds = [0, 1.3, dgms_min, 2.0, 3.0]
    
    # Create gauge segments
    for i in range(len(categories)):
        plt.barh(0, thresholds[i+1] - thresholds[i], left=thresholds[i], height=0.5, 
                color=colors[i], alpha=0.6)
        
    # Add safety factor indicator
    plt.scatter(safety_factor, 0, s=400, color='blue', zorder=5)
    plt.annotate(f'SF = {safety_factor}', (safety_factor, 0), 
                xytext=(0, 20), textcoords='offset points',
                ha='center', va='bottom', fontsize=14, 
                bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.7))
    
    # Add DGMS minimum line
    plt.axvline(x=dgms_min, color='red', linestyle='--', linewidth=2)
    plt.text(dgms_min + 0.05, 0.25, f'DGMS Min ({dgms_min})', 
             rotation=90, color='red', fontsize=10)
    
    # Set plot properties
    plt.xlim(0, 3.0)
    plt.ylim(-0.5, 0.5)
    plt.title('Stope Safety Factor Analysis', fontsize=16)
    
    # Remove y-axis ticks and labels
    plt.yticks([])
    
    # Add category labels
    for i, category in enumerate(categories):
        plt.text((thresholds[i] + thresholds[i+1])/2, -0.2, category, 
                ha='center', fontsize=12, color='black')
    
    plt.tight_layout()
    plt.savefig('reports/safety_factor_viz.png', bbox_inches='tight', dpi=300)
    plt.close()

def _create_stope_geometry_viz(dimensions):
    """Create a visualization of stope geometry"""
    width = dimensions.get('width', 5)
    height = dimensions.get('height', 4)
    length = dimensions.get('length', 10)
    
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    # Define the vertices of the stope (rectangular prism)
    vertices = [
        [0, 0, 0],
        [length, 0, 0],
        [length, width, 0],
        [0, width, 0],
        [0, 0, height],
        [length, 0, height],
        [length, width, height],
        [0, width, height]
    ]
    
    # Create arrays to store face coordinates
    X = [[vertices[0][0], vertices[1][0], vertices[2][0], vertices[3][0]],  # Bottom face
         [vertices[4][0], vertices[5][0], vertices[6][0], vertices[7][0]],  # Top face
         [vertices[0][0], vertices[1][0], vertices[5][0], vertices[4][0]],  # Front face
         [vertices[2][0], vertices[3][0], vertices[7][0], vertices[6][0]],  # Back face
         [vertices[1][0], vertices[2][0], vertices[6][0], vertices[5][0]],  # Right face
         [vertices[0][0], vertices[3][0], vertices[7][0], vertices[4][0]]]  # Left face
    
    Y = [[vertices[0][1], vertices[1][1], vertices[2][1], vertices[3][1]],  # Bottom face
         [vertices[4][1], vertices[5][1], vertices[6][1], vertices[7][1]],  # Top face
         [vertices[0][1], vertices[1][1], vertices[5][1], vertices[4][1]],  # Front face
         [vertices[2][1], vertices[3][1], vertices[7][1], vertices[6][1]],  # Back face
         [vertices[1][1], vertices[2][1], vertices[6][1], vertices[5][1]],  # Right face
         [vertices[0][1], vertices[3][1], vertices[7][1], vertices[4][1]]]  # Left face
    
    Z = [[vertices[0][2], vertices[1][2], vertices[2][2], vertices[3][2]],  # Bottom face
         [vertices[4][2], vertices[5][2], vertices[6][2], vertices[7][2]],  # Top face
         [vertices[0][2], vertices[1][2], vertices[5][2], vertices[4][2]],  # Front face
         [vertices[2][2], vertices[3][2], vertices[7][2], vertices[6][2]],  # Back face
         [vertices[1][2], vertices[2][2], vertices[6][2], vertices[5][2]],  # Right face
         [vertices[0][2], vertices[3][2], vertices[7][2], vertices[4][2]]]  # Left face
    
    # Plot each face as a surface
    colors = ['lightblue', 'lightblue', 'lightgreen', 'lightgreen', 'lightcoral', 'lightcoral']
    
    for i in range(6):
        ax.plot_surface(np.array([X[i]]), np.array([Y[i]]), np.array([Z[i]]), 
                       color=colors[i], alpha=0.6, edgecolor='black')
    
    # Draw wireframe for edges
    for i, j in [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)]:
        ax.plot([vertices[i][0], vertices[j][0]], 
                [vertices[i][1], vertices[j][1]], 
                [vertices[i][2], vertices[j][2]], 'k-', linewidth=2)
    
    # Set labels
    ax.set_xlabel('Length (m)')
    ax.set_ylabel('Width (m)')
    ax.set_zlabel('Height (m)')
    ax.set_title('Stope Geometry Visualization')
    
    # Set the axis bounds
    ax.set_xlim(0, length)
    ax.set_ylim(0, width)
    ax.set_zlim(0, height)
    
    # Add dimensions as text
    ax.text(length/2, -1, 0, f'Length: {length}m', ha='center')
    ax.text(length+1, width/2, 0, f'Width: {width}m', ha='center')
    ax.text(0, width/2, height/2, f'Height: {height}m', ha='center', va='center')
    
    plt.tight_layout()
    plt.savefig('reports/stope_geometry.png', bbox_inches='tight', dpi=300)
    plt.close()
