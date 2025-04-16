import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

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
    """Calculate labor costs based on dimensions"""
    base_rate = 1100  # INR/hour
    productivity = 2.5  # m³/hour
    hours = dimensions['volume'] / productivity
    return hours * base_rate

def _calculate_support_cost(inputs, dimensions):
    """Calculate rock support costs based on inputs and dimensions"""
    # Base support cost per cubic meter
    base_support_cost = 120  # INR per cubic meter
    
    # Adjust based on RQD (poorer rock quality = higher support costs)
    rqd = inputs.get('rqd', 75)
    rqd_factor = 2 - (rqd / 100)  # RQD of 100 = factor of 1, RQD of 0 = factor of 2
    
    # Adjust based on depth (deeper = higher support costs)
    depth = inputs.get('mining_depth', 300)
    depth_factor = 1 + (depth / 1000)  # Each 1000m adds 100% to cost
    
    # Calculate total support cost
    support_cost = base_support_cost * dimensions['volume'] * rqd_factor * depth_factor
    
    return support_cost

def _calculate_ventilation_cost(dimensions):
    """Calculate ventilation costs based on dimensions"""
    # Base ventilation cost per cubic meter
    base_ventilation_cost = 75  # INR per cubic meter
    
    # Calculate based on volume
    ventilation_cost = base_ventilation_cost * dimensions['volume']
    
    return ventilation_cost

def _generate_cost_visualizations(labor, equipment, support, ventilation):
    """Generate visualizations for cost breakdown"""
    os.makedirs('reports', exist_ok=True)
    
    # Create breakdown pie chart
    plt.figure(figsize=(10, 6))
    labels = ['Labor', 'Equipment', 'Support', 'Ventilation']
    costs = [labor, equipment, support, ventilation]
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
    
    plt.pie(costs, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Cost Breakdown by Category (INR)')
    plt.savefig('reports/cost_breakdown_chart.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    # Create bar chart for cost components
    plt.figure(figsize=(10, 6))
    x = np.arange(len(labels))
    plt.bar(x, costs, color=colors)
    plt.xlabel('Cost Components')
    plt.ylabel('Cost (INR)')
    plt.title('Mining Cost Components')
    plt.xticks(x, labels)
    
    # Add value labels on top of each bar
    for i, v in enumerate(costs):
        plt.text(i, v + 0.05, f'INR{v:,.0f}', ha='center')
    
    plt.tight_layout()
    plt.savefig('reports/cost_components_chart.png', bbox_inches='tight', dpi=300)
    plt.close()
