import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import logging
import math

# Visualization quality settings
MAX_PIXEL_WIDTH = 2000  # Maximum pixel width for any image
MAX_PIXEL_HEIGHT = 1500  # Maximum pixel height for any image
BASE_DPI = 150          # Default DPI for simple plots
LOW_DPI = 100           # DPI for complex plots or low-end systems
MAX_DPI = 300           # Maximum DPI for high-quality outputs

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
_viz_logger = logging.getLogger('cost_visualization')

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

def estimate_mining_costs(inputs, dimensions):
    """
    Estimate mining costs based on inputs and stope dimensions.
    All costs are in INR (Indian Rupees).
    """
    # Calculate base costs in INR
    labor_cost = _calculate_labor_cost(dimensions)
    equipment_cost = dimensions['volume'] * 62  # INR per cubic meter
    support_cost = _calculate_support_cost(inputs, dimensions)
    ventilation_cost = _calculate_ventilation_cost(dimensions)
    
    # Calculate total cost
    total_cost = labor_cost + equipment_cost + support_cost + ventilation_cost
    
    # Generate cost visualization
    _generate_cost_visualizations(labor_cost, equipment_cost, support_cost, ventilation_cost)
    
    return {
        'labor': round(labor_cost, 2),
        'equipment': round(equipment_cost, 2),
        'support': round(support_cost, 2),
        'ventilation': round(ventilation_cost, 2),
        'total': round(total_cost, 2)
    }

def _calculate_labor_cost(dimensions):
    """Calculate labor cost based on stope dimensions and Indian mining labor rates"""
    volume = dimensions['volume']
    productivity = 0.8  # cubic meters per person-day
    labor_rate = 1200  # INR per person-day (average skilled mining labor in India)
    
    # Labor adjustments based on stope type
    stope_type = dimensions.get('stope_type', 'Room-and-Pillar')
    if stope_type == "Sublevel Stoping":
        productivity = 1.2
    elif stope_type == "Cut-and-Fill":
        productivity = 0.6
    elif stope_type == "Shrinkage Stoping":
        productivity = 0.7
    elif stope_type == "Vertical Crater Retreat":
        productivity = 1.4
    
    # Labor estimate
    labor_person_days = volume / productivity
    labor_cost = labor_person_days * labor_rate
    return labor_cost

def _calculate_support_cost(inputs, dimensions):
    """Calculate support costs based on stope dimensions and ground conditions"""
    volume = dimensions['volume']
    rqd = inputs['rqd']
    stope_type = dimensions.get('stope_type', 'Room-and-Pillar')
    
    # Base cost per cubic meter
    if rqd < 50:
        base_cost = 480  # INR/m³ for poor rock conditions
    elif rqd < 75:
        base_cost = 320  # INR/m³ for fair rock conditions
    else:
        base_cost = 180  # INR/m³ for good rock conditions
    
    # Adjust for stope type
    if stope_type == "Room-and-Pillar":
        factor = 1.5  # Higher support requirements
    elif stope_type == "Cut-and-Fill":
        factor = 0.8  # Moderate support requirements
    else:
        factor = 0.6  # Lower support requirements
        
    return volume * base_cost * factor

def _calculate_ventilation_cost(dimensions):
    """Calculate ventilation costs based on stope dimensions"""
    volume = dimensions['volume']
    # Base ventilation cost per cubic meter (includes power, equipment)
    base_cost = 120  # INR per cubic meter
    
    # Apply depth factor
    depth_factor = 1 + (dimensions.get('mining_depth', 300) / 1000)
    
    return volume * base_cost * depth_factor

def _generate_cost_visualizations(labor, equipment, support, ventilation):
    """Generate visualizations for cost breakdown"""
    os.makedirs('reports', exist_ok=True)
    
    # Create breakdown pie chart
    fig = plt.figure(figsize=(10, 6))
    labels = ['Labor', 'Equipment', 'Support', 'Ventilation']
    costs = [labor, equipment, support, ventilation]
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
    
    plt.pie(costs, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Cost Breakdown by Category (INR)')
    _save_fig(fig, 'reports/cost_breakdown_chart.png')
    plt.close()
    
    # Create bar chart for cost components
    fig = plt.figure(figsize=(10, 6))
    x = np.arange(len(labels))
    plt.bar(x, costs, color=colors)
    plt.xlabel('Cost Components')
    plt.ylabel('Cost (INR)')
    plt.title('Mining Cost Components')
    plt.xticks(x, labels)
    
    # Add value labels on top of each bar
    for i, v in enumerate(costs):
        plt.text(i, v + 0.05, f'INR{v:,.0f}', ha='center')
    
    # Use subplots_adjust instead of tight_layout to avoid warnings
    fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)
    _save_fig(fig, 'reports/cost_components_chart.png')
    plt.close()

def estimate_cost_per_ton(inputs, dimensions, costs):
    """
    Estimate mining cost per ton of ore, based on Indian mining conditions.
    Returns the cost in INR per ton.
    """
    # Calculate ore tonnage
    volume = dimensions['volume']
    ore_density = inputs.get('ore_density', 2.7)  # Default to 2.7 tons/m³ if not provided
    tonnage = volume * ore_density
    
    # Calculate cost per ton
    cost_per_ton = costs['total'] / tonnage
    
    # Generate enhanced cost report
    _generate_enhanced_cost_report(inputs, dimensions, costs, tonnage, cost_per_ton)
    
    return {
        'tonnage': round(tonnage, 2),
        'cost_per_ton': round(cost_per_ton, 2)
    }

def _generate_enhanced_cost_report(inputs, dimensions, costs, tonnage, cost_per_ton):
    """Generate comprehensive cost analysis report"""
    os.makedirs('reports', exist_ok=True)
    
    # Create enhanced cost breakdown chart with INR values
    fig = plt.figure(figsize=(12, 8))
    
    # Cost breakdown pie chart
    labels = ['Labor', 'Equipment', 'Support', 'Ventilation']
    costs_values = [costs['labor'], costs['equipment'], costs['support'], costs['ventilation']]
    colors = ['#FF9999', '#66B3FF', '#99FF99', '#FFCC99']
    
    plt.pie(costs_values, labels=labels, colors=colors, autopct=lambda p: f'{p:.1f}%\n(₹{p*costs["total"]/100:.1f}L)', 
            startangle=90, wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    plt.axis('equal')
    
    plt.title('Mining Cost Distribution\n' + 
              f'Total: ₹{costs["total"]/100000:.2f}L | Per Ton: ₹{cost_per_ton:.2f}\n' +
              f'Ore Volume: {dimensions["volume"]}m³ | Tonnage: {tonnage:.1f}t', 
              fontsize=14, fontweight='bold')
    
    _save_fig(fig, 'reports/cost_breakdown_chart.png')
    plt.close()
    
    # Create cost components chart
    fig = plt.figure(figsize=(12, 6))
    x = np.arange(len(labels))
    
    plt.bar(x, costs_values, color=colors, width=0.6, edgecolor='black', linewidth=1.5)
    plt.xlabel('Cost Components', fontsize=12)
    plt.ylabel('Cost (₹)', fontsize=12)
    plt.title('Mining Cost Components Breakdown', fontsize=14, fontweight='bold')
    plt.xticks(x, labels, fontsize=10)
    plt.grid(axis='y', alpha=0.3)
    
    # Add value labels on top of each bar
    for i, v in enumerate(costs_values):
        plt.text(i, v + max(costs_values)*0.02, f'₹{v/100000:.2f}L\n({v/costs["total"]*100:.1f}%)', 
                ha='center', fontsize=10, fontweight='bold')
    
    # Use subplots_adjust instead of tight_layout to avoid warnings
    fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)
    _save_fig(fig, 'reports/cost_components_chart.png')
    plt.close()

# Legacy function for backward compatibility
def generate_cost_breakdown(costs):
    """Legacy wrapper for the cost visualization system"""
    _generate_cost_visualizations(costs['labor'], costs['equipment'], costs['support'], costs['ventilation'])
