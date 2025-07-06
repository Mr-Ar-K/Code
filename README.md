# Mining Stope Design Tool - Indian Standards

A comprehensive desktop application for designing mining stopes in accordance with Indian mining standards and regulations including DGMS (Directorate General of Mine Safety), MMR (Metalliferous Mines Regulations), and IBM (Indian Bureau of Mines) guidelines.

## Overview

This software is specifically designed for Indian mining operations to calculate optimal stope dimensions, assess rock stability, estimate mining costs, and generate compliance reports. The application provides a user-friendly graphical interface for mining engineers to input geological and operational parameters and receive detailed analysis results.

## Features

### Core Functionality
- **Stope Design Calculation**: Automated calculation of optimal stope dimensions based on geological parameters
- **Stability Analysis**: Comprehensive rock stability assessment using Indian and international standards
- **Cost Estimation**: Detailed mining cost calculations in Indian Rupees (INR)
- **Compliance Checking**: Automatic verification against DGMS safety regulations
- **Report Generation**: Professional PDF reports with visualizations and recommendations

### Technical Features
- **Multi-tab Interface**: Organized workflow with separate tabs for input, results, and visualizations
- **Real-time Validation**: Input validation with realistic mining parameter ranges
- **3D Visualizations**: Interactive 3D stope visualization and stability charts
- **Export Capabilities**: PDF report generation with detailed calculations and charts
- **Indian Standards Compliance**: Built-in compliance with DGMS safety factors and regulations

### Supported Ore Types
- Generic ore bodies
- Gold deposits
- Copper deposits
- Iron ore
- Zinc deposits
- Lead deposits
- Bauxite
- Chromite

## Installation

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

### Quick Setup
1. Clone or download the project to your local machine
2. Navigate to the project directory
3. Create a virtual environment:
   ```bash
   python -m venv myenv
   ```
4. Activate the virtual environment:
   - On Linux/Mac: `source myenv/bin/activate`
   - On Windows: `myenv\Scripts\activate`
5. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Manual Installation
If you prefer to install packages manually:
```bash
pip install matplotlib numpy pandas fpdf Pillow
```

## How to Use

### Starting the Application
1. Ensure your virtual environment is activated
2. Navigate to the project directory
3. Run the application:
   ```bash
   python src/main.py
   ```

### Using the Interface

#### 1. Design Input Tab
- **Ore Body Thickness**: Enter the thickness of the ore body in meters (0.3-100m)
- **Dip Angle**: Specify the dip angle in degrees (0-70°)
- **Rock Quality Designation (RQD)**: Input RQD percentage (25-100%)
- **Mining Depth**: Enter the mining depth in meters (5-2000m)
- **Ore Type**: Select from the dropdown menu of supported ore types
- **Additional Notes**: Add any specific notes or requirements

#### 2. Calculation Process
- Click "Calculate Design (DGMS Compliant)" to perform the analysis
- The system will validate all inputs and show error messages if needed
- Calculations are performed using Indian mining standards

#### 3. Results Tab
- View detailed calculation results including:
  - Recommended stope dimensions
  - Stability analysis results
  - DGMS compliance status
  - Safety factor calculations
  - Cost estimates in INR

#### 4. Visualizations Tab
- Access 3D visualizations of the proposed stope design
- View stability charts and analysis graphs
- Export visualizations as image files

#### 5. Report Generation
- Generate comprehensive PDF reports
- Include all calculations, visualizations, and recommendations
- Suitable for regulatory submissions and project documentation

### Menu Options
- **File Menu**: New design, clear inputs, exit application
- **Help Menu**: Access DGMS guidelines and application information

## Code Structure

### Main Components

#### `/src/main.py`
- Application entry point
- Error handling and initialization
- Module import management

#### `/src/gui.py`
- Main GUI application class (`MiningStopeDesignApp`)
- User interface components and layout
- Event handling and user interactions
- Tab management (Input, Results, Visualizations)

#### `/src/stope_calculations.py`
- Core calculation engine
- Input validation functions
- Stope design algorithms
- Results processing and formatting

#### `/src/stability_analysis.py`
- Rock stability assessment algorithms
- Stope type determination
- Dimension calculations
- 3D visualization generation
- Indian and international standard implementations

#### `/src/cost_estimation.py`
- Mining cost calculation functions
- Cost visualization and charting
- Indian currency (INR) formatting
- Economic analysis tools

#### `/src/input_validation.py`
- Input parameter validation
- Range checking for mining parameters
- Error message generation
- Data sanitization

#### `/src/report_generator.py`
- PDF report generation
- Chart and visualization integration
- Professional formatting
- Summary text generation

#### `/tests/`
- `test_calculations.py`: Unit tests for calculation functions
- `test_validation.py`: Input validation tests
- Test files for ensuring code reliability

### Configuration Files
- `requirements.txt`: Python package dependencies
- `README.md`: This documentation file

## Input Parameters and Ranges

### Required Parameters
- **Ore Body Thickness**: 0.3 to 100 meters
- **Dip Angle**: 0 to 70 degrees
- **Rock Quality Designation (RQD)**: 25% to 100%
- **Mining Depth**: 5 to 2000 meters

### Optional Parameters
- **Ore Type**: Selection from predefined list
- **Additional Notes**: Text field for special requirements

## Standards and Compliance

### Indian Standards
- **DGMS Regulations**: Minimum safety factor of 1.5
- **MMR Compliance**: Metalliferous Mines Regulations
- **IBM Guidelines**: Indian Bureau of Mines standards

### International Standards
- **Hoek-Brown Criterion**: Rock mass characterization
- **Barton Q-System**: Rock mass quality assessment
- **CMRI Adjustments**: Central Mining Research Institute adaptations

## Output and Reports

### Calculation Results
- Recommended stope dimensions
- Stability analysis with safety factors
- Cost estimates in Indian Rupees
- Compliance status with regulations
- Technical recommendations

### Visualizations
- 3D stope design models
- Stability analysis charts
- Cost breakdown graphs
- Compliance verification diagrams

### PDF Reports
- Professional formatting
- Complete technical documentation
- Regulatory compliance verification
- Suitable for official submissions

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all required packages are installed
2. **GUI Display Issues**: Check tkinter installation
3. **Calculation Errors**: Verify input parameter ranges
4. **Visualization Problems**: Ensure matplotlib backend is properly configured

### Error Messages
- Input validation errors provide specific guidance
- Calculation errors include detailed error descriptions
- GUI errors are displayed in popup dialogs

## Support and Documentation

### Help Resources
- Built-in DGMS guidelines reference
- Application about dialog with version information
- Comprehensive error messages and tooltips

### Technical Support
- Review error messages for specific guidance
- Check input parameter ranges
- Verify all required packages are installed

## License

MIT License

Copyright (c) 2025 Mining Stope Design Tool

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Disclaimer

This software is designed for engineering analysis purposes. Users are responsible for verifying results and ensuring compliance with local regulations. The software includes Indian mining standards but users should always consult with qualified mining engineers and regulatory authorities for final approvals.

