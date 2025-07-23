import os
import matplotlib
matplotlib.use('Agg')
from datetime import datetime
from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
_report_logger = logging.getLogger('report_generator')

# Indian Mining Standards references
DGMS_REFERENCES = {
    'safety_factor': 'DGMS Tech. Circular No. 3 of 2019',
    'ventilation': 'DGMS Circular No. 01 of 2011 & Reg. 130/157 of MMR',
    'strata_control': 'MMR 2011 Regulation 111, DGMS Circular No. 3 of 2017',
    'pillar_design': 'DGMS (Tech)(SCR) Circular No. 01 of 2019'
}

def generate_summary_text(results, filename='reports/stope_summary.txt', notes=None):
    """Generate comprehensive text summary with enhanced stope information"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    stability = results.get('stability', {})
    dimensions = results.get('dimensions', {})
    costs = results.get('costs', {})
    dgms_warnings = results.get('dgms_warnings', [])
    stope_type = results.get('stope_type', 'Unknown')
    
    summary = []
    summary.append("=" * 60)
    summary.append("         ADVANCED MINING STOPE DESIGN ANALYSIS")
    summary.append("=" * 60)
    summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    summary.append(f"Compliant with: DGMS, MMR & IBM Standards")
    summary.append("")
    
    # Enhanced stope configuration
    summary.append("STOPE CONFIGURATION & SPECIFICATIONS")
    summary.append("-" * 40)
    summary.append(f"Mining Method: {stope_type}")
    summary.append(f"Length: {dimensions.get('length', 'N/A')} meters")
    summary.append(f"Width: {dimensions.get('width', 'N/A')} meters") 
    summary.append(f"Height: {dimensions.get('height', 'N/A')} meters")
    summary.append(f"Volume: {dimensions.get('volume', 'N/A')} cubic meters")
    summary.append(f"Hydraulic Radius: {dimensions.get('hydraulic_radius', 'N/A')} meters")
    summary.append(f"Rock Mass Rating (RMR): {dimensions.get('rmr', 'N/A')}")
    summary.append(f"Q Value: {dimensions.get('q_value', 'N/A')}")
    summary.append(f"Stability Number: {dimensions.get('stability_number', 'N/A')}")
    summary.append("")
    
    # Detailed stability analysis
    summary.append("GEOTECHNICAL STABILITY ANALYSIS")
    summary.append("-" * 35)
    safety_factor = stability.get('safety_factor', 'N/A')
    dgms_compliant = stability.get('dgms_compliant', False)
    compliance_text = "[✓ COMPLIANT]" if dgms_compliant else "[✗ NON-COMPLIANT]"
    
    summary.append(f"Safety Factor: {safety_factor} {compliance_text}")
    summary.append(f"Stability Class: {stability.get('stability_class', 'N/A')}")
    summary.append(f"Vertical Stress: {stability.get('vertical_stress', 'N/A')} MPa")
    summary.append(f"Horizontal Stress: {stability.get('horizontal_stress', 'N/A')} MPa")
    summary.append(f"Rock Strength: {stability.get('rock_strength', 'N/A')} MPa")
    summary.append("")
    
    # Indian regulations compliance
    summary.append("INDIAN MINING REGULATIONS COMPLIANCE")
    summary.append("-" * 38)
    for key, reference in DGMS_REFERENCES.items():
        summary.append(f"• {key.replace('_', ' ').title()}: {reference}")
    summary.append("")
    
    # Enhanced cost analysis
    if costs:
        summary.append("COMPREHENSIVE COST ANALYSIS (INR)")
        summary.append("-" * 33)
        total_cost = costs.get('total', 0)
        summary.append(f"Total Project Cost: ₹{total_cost:,.2f}")
        summary.append("")
        summary.append("Detailed Cost Breakdown:")
        
        cost_items = ['labor', 'equipment', 'support', 'ventilation']
        for item in cost_items:
            if item in costs:
                summary.append(f"  • {item.title()} Costs: ₹{costs[item]:,.2f}")
        
        if total_cost > 0:
            summary.append("")
            summary.append("Cost Distribution:")
            for item in cost_items:
                if item in costs:
                    percentage = (costs[item] / total_cost) * 100
                    summary.append(f"  • {item.title()}: {percentage:.1f}%")
        summary.append("")
    
    # Safety alerts and warnings
    if dgms_warnings:
        summary.append("DGMS SAFETY ALERTS & COMPLIANCE NOTES")
        summary.append("-" * 40)
        for i, warning in enumerate(dgms_warnings, 1):
            summary.append(f"{i}. {warning}")
        summary.append("")
    
    # Additional technical notes
    if notes:
        summary.append("ADDITIONAL TECHNICAL NOTES")
        summary.append("-" * 28)
        summary.append(notes)
        summary.append("")
    
    # Generated visualizations
    summary.append("GENERATED VISUALIZATION FILES")
    summary.append("-" * 30)
    viz_files = [
        "stope_3d_isometric.png - Realistic 3D stope visualization",
        "stope_cross_sections.png - Longitudinal and cross-sectional views", 
        "stope_plan_view.png - Plan view layout with infrastructure",
        "safety_factor_gauge.png - DGMS compliance gauge",
        "stress_strength_comparison.png - Geotechnical analysis"
    ]
    for viz_file in viz_files:
        summary.append(f"• {viz_file}")
    
    # Save summary
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary))
    
    return filename

def generate_pdf_report(results, filename='reports/stope_report.pdf', notes=None):
    """Generate comprehensive PDF report with enhanced visualizations and PowerShell compatibility"""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        _report_logger.info(f"Generating PDF report: {filename}")
        
        stability = results.get('stability', {})
        dimensions = results.get('dimensions', {})
        costs = results.get('costs', {})
        dgms_warnings = results.get('dgms_warnings', [])
        stope_type = results.get('stope_type', 'Unknown')
        
        # Initialize PDF with enhanced formatting and safe font handling
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Use built-in fonts to avoid substitution issues
        # Set up page margins for better text rendering
        pdf.set_margins(20, 20, 20)
        
        # Enhanced header with safe font handling
        try:
            pdf.set_font('Helvetica', 'B', 18)  # Use Helvetica instead of Arial
        except:
            pdf.set_font('Arial', 'B', 18)  # Fallback to Arial
            
        pdf.set_text_color(25, 25, 112)  # Navy blue
        pdf.cell(0, 15, 'MINING STOPE DESIGN REPORT', ln=True, align='C')
        
        try:
            pdf.set_font('Helvetica', 'I', 11)
        except:
            pdf.set_font('Arial', 'I', 11)
            
        pdf.set_text_color(128, 128, 128)  # Gray
        pdf.cell(0, 8, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M IST")}', ln=True, align='C')
        pdf.cell(0, 8, 'DGMS, MMR & IBM Compliant', ln=True, align='C')
        pdf.ln(10)
        
        # Reset text color
        pdf.set_text_color(0, 0, 0)
        
        # Executive Summary with safe text handling
        try:
            pdf.set_font('Helvetica', 'B', 14)
        except:
            pdf.set_font('Arial', 'B', 14)
            
        pdf.set_fill_color(230, 230, 250)  # Lavender
        pdf.cell(0, 10, 'EXECUTIVE SUMMARY', ln=True, fill=True)
        pdf.ln(5)

        try:
            pdf.set_font('Helvetica', '', 10)
        except:
            pdf.set_font('Arial', '', 10)
            
        safety_factor = stability.get('safety_factor', 'N/A')
        dgms_compliant = stability.get('dgms_compliant', False)
        total_cost = costs.get('total', 0)

        # Create shorter, safer text blocks
        length_val = dimensions.get('length', 'N/A')
        width_val = dimensions.get('width', 'N/A')
        height_val = dimensions.get('height', 'N/A')
        
        summary_lines = [
            f"Stope Type: {stope_type}",
            f"Dimensions: {length_val}m x {width_val}m x {height_val}m",
            f"Safety Factor: {safety_factor}",
            f"DGMS Status: {'Compliant' if dgms_compliant else 'Non-Compliant'}",
            f"Estimated Cost: INR {total_cost:,.0f}"
        ]
        
        for line in summary_lines:
            # Ensure line fits on page with safe width calculation
            try:
                line_width = pdf.get_string_width(line)
                if line_width > 170:  # Max safe width
                    pdf.multi_cell(0, 6, line)
                else:
                    pdf.cell(0, 6, line, ln=True)
            except:
                # Fallback: always use multi_cell for safety
                pdf.multi_cell(0, 6, line)
        
        pdf.ln(5)
        # Technical Specifications with safe formatting
        try:
            pdf.set_font('Helvetica', 'B', 14)
        except:
            pdf.set_font('Arial', 'B', 14)
            
        pdf.set_fill_color(230, 230, 250)
        pdf.cell(0, 10, 'TECHNICAL SPECIFICATIONS', ln=True, fill=True)
        pdf.ln(5)
        
        try:
            pdf.set_font('Helvetica', 'B', 12)
        except:
            pdf.set_font('Arial', 'B', 12)
            
        pdf.cell(0, 8, 'Stope Configuration:', ln=True)
        
        try:
            pdf.set_font('Helvetica', '', 10)
        except:
            pdf.set_font('Arial', '', 10)
        
        spec_data = [
            ('Mining Method', stope_type),
            ('Length', f"{dimensions.get('length', 'N/A')} m"),
            ('Width', f"{dimensions.get('width', 'N/A')} m"),
            ('Height', f"{dimensions.get('height', 'N/A')} m"),
            ('Volume', f"{dimensions.get('volume', 'N/A')} m3"),
            ('Hydraulic Radius', f"{dimensions.get('hydraulic_radius', 'N/A')} m"),
            ('Rock Mass Rating', f"{dimensions.get('rmr', 'N/A')}"),
            ('Q Value', f"{dimensions.get('q_value', 'N/A')}"),
            ('Stability Number', f"{dimensions.get('stability_number', 'N/A')}")
        ]
        
        for label, value in spec_data:
            try:
                # Use safe cell widths to prevent overflow
                pdf.cell(70, 6, f'{label}:', ln=0)
                pdf.cell(100, 6, str(value), ln=True)
            except:
                # Fallback to multi_cell for problematic content
                pdf.multi_cell(0, 6, f'{label}: {value}')
        
        pdf.ln(5)
        # Stability Analysis with improved formatting
        try:
            pdf.set_font('Helvetica', 'B', 12)
        except:
            pdf.set_font('Arial', 'B', 12)
            
        pdf.cell(0, 8, 'Geotechnical Analysis:', ln=True)
        
        try:
            pdf.set_font('Helvetica', '', 10)
        except:
            pdf.set_font('Arial', '', 10)
        
        compliance_text = "COMPLIANT" if dgms_compliant else "NON-COMPLIANT"
        stability_data = [
            ('Safety Factor', f"{safety_factor} ({compliance_text})"),
            ('Stability Class', stability.get('stability_class', 'N/A')),
            ('Vertical Stress', f"{stability.get('vertical_stress', 'N/A')} MPa"),
            ('Horizontal Stress', f"{stability.get('horizontal_stress', 'N/A')} MPa"),
            ('Rock Strength', f"{stability.get('rock_strength', 'N/A')} MPa")
        ]
        
        for label, value in stability_data:
            try:
                pdf.cell(70, 6, f'{label}:', ln=0)
                if 'NON-COMPLIANT' in str(value):
                    pdf.set_text_color(255, 0, 0)  # Red
                elif 'COMPLIANT' in str(value):
                    pdf.set_text_color(0, 128, 0)  # Green
                pdf.cell(100, 6, str(value), ln=True)
                pdf.set_text_color(0, 0, 0)  # Reset to black
            except:
                # Fallback for problematic content
                pdf.multi_cell(0, 6, f'{label}: {value}')
        
        pdf.ln(10)
    
        # Add enhanced visualizations with better error handling
        visualization_files = [
            ('reports/stope_3d_isometric.png', 'Realistic 3D Stope Visualization'),
            ('reports/stope_cross_sections.png', 'Cross-Sectional Views'),
            ('reports/stope_plan_view.png', 'Plan View Layout'),
            ('reports/safety_factor_gauge.png', 'Safety Factor Analysis'),
            ('reports/stress_strength_comparison.png', 'Stress vs Strength Analysis')
        ]
        
        for viz_file, caption in visualization_files:
            pdf.add_page()
            try:
                pdf.set_font('Helvetica', 'B', 14)
            except:
                pdf.set_font('Arial', 'B', 14)
                
            pdf.cell(0, 10, caption, ln=True, align='C')
            pdf.ln(5)
            
            if os.path.exists(viz_file):
                try:
                    _report_logger.info(f"Embedding visualization: {viz_file}")
                    # Use smaller width to ensure fit
                    pdf.image(viz_file, x=15, w=170)
                except Exception as e:
                    try:
                        pdf.set_font('Helvetica', '', 10)
                    except:
                        pdf.set_font('Arial', '', 10)
                    pdf.multi_cell(0, 6, f'[Error loading {caption}: {str(e)}]')
                    _report_logger.error(f"Failed to embed image {viz_file} in PDF: {str(e)}")
            else:
                try:
                    pdf.set_font('Helvetica', '', 10)
                except:
                    pdf.set_font('Arial', '', 10)
                pdf.multi_cell(0, 6, f'[Missing visualization: {caption}]')
                _report_logger.warning(f"Missing visualization file: {viz_file}")
            pdf.ln(10)
            
        # Cost Analysis with improved formatting
        if costs:
            pdf.add_page()
            try:
                pdf.set_font('Helvetica', 'B', 14)
            except:
                pdf.set_font('Arial', 'B', 14)
                
            pdf.set_fill_color(230, 230, 250)
            pdf.cell(0, 10, 'COST ANALYSIS (INR)', ln=True, fill=True)
            pdf.ln(5)
            
            try:
                pdf.set_font('Helvetica', 'B', 12)
            except:
                pdf.set_font('Arial', 'B', 12)
                
            pdf.set_text_color(0, 0, 139)  # Dark blue
            pdf.cell(0, 8, f'Total Project Cost: INR {total_cost:,.0f}', ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(5)
            
            try:
                pdf.set_font('Helvetica', 'B', 11)
            except:
                pdf.set_font('Arial', 'B', 11)
                
            pdf.cell(0, 8, 'Detailed Cost Breakdown:', ln=True)
            
            try:
                pdf.set_font('Helvetica', '', 10)
            except:
                pdf.set_font('Arial', '', 10)
                
            cost_items = ['labor', 'equipment', 'support', 'ventilation']
            for item in cost_items:
                if item in costs:
                    percentage = (costs[item] / total_cost * 100) if total_cost > 0 else 0
                    cost_line = f'  - {item.title()}: INR {costs[item]:,.0f} ({percentage:.1f}%)'
                    try:
                        pdf.cell(0, 6, cost_line, ln=True)
                    except:
                        pdf.multi_cell(0, 6, cost_line)
        
        # Save PDF with error handling
        try:
            pdf.output(filename)
            _report_logger.info(f"PDF report successfully generated: {filename}")
            return filename
        except Exception as e:
            _report_logger.error(f"Failed to save PDF: {e}")
            raise
            
    except Exception as e:
        _report_logger.error(f"Error generating PDF report: {e}")
        # Create a simplified fallback report
        try:
            return _create_fallback_pdf_report(results, filename)
        except:
            _report_logger.error("Even fallback PDF generation failed")
            return None

def _create_fallback_pdf_report(results, filename):
    """Create a simplified PDF report when the main generation fails"""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_margins(20, 20, 20)
        
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 15, 'MINING STOPE ANALYSIS REPORT', ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font('Arial', '', 12)
        
        # Basic information
        stability = results.get('stability', {})
        dimensions = results.get('dimensions', {})
        
        basic_info = [
            f"Stope Type: {results.get('stope_type', 'N/A')}",
            f"Safety Factor: {stability.get('safety_factor', 'N/A')}",
            f"DGMS Compliant: {stability.get('dgms_compliant', 'N/A')}",
            f"Dimensions: {dimensions.get('length', 'N/A')} x {dimensions.get('width', 'N/A')} x {dimensions.get('height', 'N/A')} m",
            f"Volume: {dimensions.get('volume', 'N/A')} m3"
        ]
        
        for info in basic_info:
            pdf.multi_cell(0, 8, info)
        
        pdf.output(filename)
        _report_logger.info(f"Fallback PDF report created: {filename}")
        return filename
        
    except Exception as e:
        _report_logger.error(f"Fallback PDF creation failed: {e}")
        return None
        for warning in dgms_warnings:
            pdf.multi_cell(0, 6, f'- {warning}')
    
    if notes:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'ADDITIONAL NOTES:', ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 6, notes)
    
    # Save PDF
    try:
        pdf.output(filename)
        _report_logger.info(f"Successfully generated PDF report: {filename}")
    except Exception as e:
        _report_logger.error(f"Failed to generate PDF report: {str(e)}")
    
    return filename

# Enhanced 3D visualization functions remain the same as in stability_analysis.py
# to avoid duplication while maintaining functionality
