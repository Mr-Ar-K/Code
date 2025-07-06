# Mining Stope Design Tool - Indian Standards

A comprehensive desktop application for designing mining stopes in accordance with Indian mining standards and regulations including DGMS (Directorate General of Mine Safety), MMR (Metalliferous Mines Regulations), and IBM (Indian Bureau of Mines) guidelines.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
  - [Core Functionality](#core-functionality)
  - [Technical Features](#technical-features)
  - [Supported Ore Types](#supported-ore-types)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Quick Setup](#quick-setup)
  - [Manual Installation](#manual-installation)
- [How to Use](#how-to-use)
  - [Starting the Application](#starting-the-application)
  - [Using the Interface](#using-the-interface)
  - [Menu Options](#menu-options)
- [Code Structure](#code-structure)
  - [Main Components](#main-components)
  - [Configuration Files](#configuration-files)
- [Input Parameters and Ranges](#input-parameters-and-ranges)
- [Standards and Compliance](#standards-and-compliance)
- [Technical Implementation](#technical-implementation)
  - [Mathematical Formulas](#mathematical-formulas)
  - [Backend Architecture](#backend-architecture)
  - [Algorithm Workflow](#algorithm-workflow)
  - [Data Processing](#data-processing)
- [Output and Reports](#output-and-reports)
- [System Requirements](#system-requirements)
- [Performance Considerations](#performance-considerations)
- [Troubleshooting](#troubleshooting)
- [Support and Documentation](#support-and-documentation)
- [Contributing](#contributing)
- [Version History](#version-history)
- [License](#license)
- [Disclaimer](#disclaimer)

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

## Technical Implementation

### Mathematical Formulas

#### 1. Rock Mass Rating (RMR) Calculation
```
RMR = RQD_rating + UCS_rating + Spacing_rating + Condition_rating + Groundwater_rating + Orientation_rating
```

**Where:**
- `RQD_rating`: Rock Quality Designation rating (0-20 points)
- `UCS_rating`: Uniaxial Compressive Strength rating (0-15 points)
- `Spacing_rating`: Joint spacing rating (0-20 points)
- `Condition_rating`: Joint condition rating (0-30 points)
- `Groundwater_rating`: Groundwater condition rating (0-15 points)
- `Orientation_rating`: Joint orientation rating (0-12 points)

#### 2. Barton Q-System
```
Q = (RQD/Jn) × (Jr/Ja) × (Jw/SRF)
```

**Where:**
- `RQD`: Rock Quality Designation (%)
- `Jn`: Joint set number (0.5-20)
- `Jr`: Joint roughness number (0.5-4)
- `Ja`: Joint alteration number (0.75-20)
- `Jw`: Joint water reduction factor (0.05-1.0)
- `SRF`: Stress reduction factor (0.5-20)

#### 3. Stope Stability Analysis
```
Stability_Number = Q × σc / (σ1 × ESR)
```

**Where:**
- `Q`: Barton Q-value
- `σc`: Uniaxial compressive strength (MPa)
- `σ1`: Maximum principal stress (MPa)
- `ESR`: Excavation support ratio

#### 4. Safety Factor Calculation (DGMS Compliant)
```
Safety_Factor = (Rock_Strength × Geological_Factor) / (Applied_Stress × Load_Factor)
```

**Minimum Safety Factor (DGMS)**: 1.5

#### 5. Stope Dimension Calculations

**Maximum Unsupported Span:**
```
L_max = 2 × ESR × √(Q / 100)
```

**Optimal Stope Height:**
```
H_optimal = L_max × (1 + 0.1 × Dip_Angle / 45)
```

**Pillar Width (DGMS Minimum):**
```
W_pillar = max(3.0, 0.5 × H_stope × √(Depth_factor))
```

#### 6. Cost Estimation Formulas

**Development Cost:**
```
Development_Cost = Length × Cross_Section × Unit_Rate_INR
```

**Production Cost:**
```
Production_Cost = Volume × Tonnage_Factor × Mining_Rate_INR
```

**Total Mining Cost:**
```
Total_Cost = Development_Cost + Production_Cost + Support_Cost + Ventilation_Cost
```

#### 7. Hoek-Brown Criterion
```
σ1 = σ3 + σci × (mb × σ3/σci + s)^a
```

**Where:**
- `σ1`: Major principal stress at failure
- `σ3`: Minor principal stress
- `σci`: Uniaxial compressive strength of intact rock
- `mb`: Hoek-Brown material constant
- `s`: Hoek-Brown material constant
- `a`: Hoek-Brown material constant

### Backend Architecture

#### 1. Input Processing Pipeline
```
User Input → Validation → Sanitization → Parameter Extraction → Calculation Engine
```

**Input Validation Steps:**
1. **Range Checking**: Verify all parameters are within realistic mining ranges
2. **Type Validation**: Ensure numerical inputs are valid numbers
3. **Consistency Checking**: Verify geological parameters are consistent
4. **DGMS Compliance**: Check inputs meet Indian mining standards

#### 2. Calculation Engine Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Input Data    │ → │  Stope Analysis  │ → │    Results      │
│                 │    │                  │    │                 │
│ • Ore Thickness │    │ • Stability Calc │    │ • Dimensions    │
│ • Dip Angle     │    │ • Safety Factor  │    │ • Safety Status │
│ • RQD Value     │    │ • Cost Analysis  │    │ • Cost Estimate │
│ • Mining Depth  │    │ • Compliance     │    │ • Compliance    │
│ • Ore Type      │    │   Check          │    │   Report        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

#### 3. Core Processing Modules

**Module 1: Stability Analysis (`stability_analysis.py`)**
- Rock mass characterization using RMR and Q-system
- Stope type determination based on geological conditions
- 3D stress analysis using finite element principles
- Safety factor calculation with DGMS compliance

**Module 2: Stope Calculations (`stope_calculations.py`)**
- Dimensional optimization algorithms
- Pillar design calculations
- Excavation sequence planning
- Production scheduling estimates

**Module 3: Cost Estimation (`cost_estimation.py`)**
- Real-time cost calculations in INR
- Equipment cost modeling
- Labor cost estimation
- Material and support cost analysis

### Algorithm Workflow

#### 1. Main Calculation Sequence
```
START
├── Input Validation
│   ├── Check parameter ranges
│   ├── Validate data types
│   └── Ensure DGMS compliance
├── Geological Analysis
│   ├── Calculate RMR score
│   ├── Determine Q-value
│   └── Assess rock mass quality
├── Stability Assessment
│   ├── Determine stope type
│   ├── Calculate safety factors
│   └── Check DGMS requirements
├── Dimension Optimization
│   ├── Calculate optimal dimensions
│   ├── Design pillar systems
│   └── Verify structural integrity
├── Cost Analysis
│   ├── Estimate development costs
│   ├── Calculate production costs
│   └── Generate cost breakdown
└── Report Generation
    ├── Compile results
    ├── Generate visualizations
    └── Create PDF report
END
```

#### 2. Stope Type Determination Logic

**Decision Matrix for Stope Type Selection:**

1. **Room and Pillar Mining**:
   - Condition: RQD ≥ 75% AND Dip Angle ≤ 30°
   - Application: Stable, horizontal to shallow-dipping ore bodies
   - Pillar design based on tributary area theory

2. **Sublevel Stoping**:
   - Condition: RQD ≥ 50% AND Dip Angle ≤ 45°
   - Application: Moderate to good rock conditions
   - Requires systematic drilling and blasting pattern

3. **Cut and Fill Mining**:
   - Condition: Dip Angle > 45°
   - Application: Steep-dipping ore bodies
   - Sequential mining with backfill support

4. **Supported Stoping**:
   - Condition: RQD < 50% OR complex geological conditions
   - Application: Poor rock conditions requiring artificial support
   - Timber, steel, or concrete support systems

#### 3. Safety Factor Validation Logic

**DGMS Compliance Algorithm:**
- Minimum Required Safety Factor: 1.5
- Compliance Status: COMPLIANT if Safety Factor ≥ 1.5
- Compliance Status: NON_COMPLIANT if Safety Factor < 1.5
- Additional safety margins applied for:
  - Water presence: +0.2 factor
  - Seismic activity: +0.3 factor
  - Depth > 300m: +0.1 factor per 100m

### Data Processing

#### 1. Input Data Structure

**Required Input Parameters:**
- Ore Thickness: Floating point value in meters (range: 0.3-100)
- Dip Angle: Floating point value in degrees (range: 0-70)
- RQD: Floating point percentage value (range: 25-100)
- Mining Depth: Floating point value in meters (range: 5-2000)
- Ore Type: String enumeration from predefined ore types
- Additional Notes: Optional text string for special requirements

**Data Validation Rules:**
- All numerical inputs must be within specified ranges
- Ore type must match predefined enumeration values
- Geological consistency checks between parameters
- DGMS compliance verification for all inputs

#### 2. Calculation Results Structure

**Stope Dimensions Output:**
- Length: Optimized stope length in meters
- Width: Optimized stope width in meters
- Height: Optimized stope height in meters
- Volume: Total excavation volume in cubic meters

**Stability Analysis Output:**
- RMR Score: Rock Mass Rating (0-100 scale)
- Q-Value: Barton Q-system value (0.001-1000 range)
- Safety Factor: Calculated safety factor (>1.0 required)
- DGMS Compliance: Boolean compliance status

**Cost Estimation Output:**
- Development Cost: Calculated in Indian Rupees (INR)
- Production Cost: Calculated in Indian Rupees (INR)
- Support Cost: Calculated in Indian Rupees (INR)
- Total Cost: Sum of all cost components in INR

**Recommendations Output:**
- Stope Type: Recommended mining method
- Support Requirements: List of required support systems
- Mining Sequence: Recommended excavation sequence

#### 3. Visualization Data Processing

**3D Model Generation:**
- Vertices: Three-dimensional coordinate arrays for stope geometry
- Faces: Triangle face definitions for 3D mesh rendering
- Colors: RGB color values for visual differentiation

**Stability Chart Data:**
- X-Values: Depth progression arrays
- Y-Values: Stability factor arrays
- Threshold Line: DGMS minimum safety factor reference

**Cost Breakdown Visualization:**
- Categories: Cost component categories
- Values: Cost values in Indian Rupees
- Percentages: Relative percentage breakdown of costs

#### 4. Report Generation Pipeline

**Report Assembly Process:**
Data Collection → Template Selection → Content Assembly → Formatting → PDF Export

**Report Content Structure:**

1. **Executive Summary**: 
   - Key findings and engineering recommendations
   - Compliance status summary
   - Critical safety factors

2. **Input Parameters**: 
   - Complete parameter listing with validation status
   - Geological condition summary
   - Mining constraints and assumptions

3. **Geological Analysis**: 
   - RMR calculation breakdown
   - Q-system assessment results
   - Rock mass characterization

4. **Stability Assessment**: 
   - Safety factor calculations
   - DGMS compliance verification
   - Structural integrity analysis

5. **Stope Design**: 
   - Optimal dimension specifications
   - Pillar design parameters
   - Excavation sequence recommendations

6. **Cost Analysis**: 
   - Detailed cost breakdown in INR
   - Cost comparison between mining methods
   - Economic feasibility assessment

7. **Compliance Verification**: 
   - DGMS regulation adherence checklist
   - MMR compliance status
   - IBM guideline conformity

8. **Engineering Recommendations**: 
   - Preferred mining method selection
   - Support system requirements
   - Risk mitigation strategies

9. **Technical Appendices**: 
   - Supporting calculation details
   - Reference standards and codes
   - Assumption justifications

**Quality Assurance Process:**
- Automatic calculation verification
- Cross-reference checking between sections
- Compliance validation against Indian standards
- Professional formatting and presentation standards

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

## System Requirements

### Hardware Requirements
- **Processor**: Intel i3 or AMD equivalent (minimum), Intel i5 or higher (recommended)
- **RAM**: 4GB minimum, 8GB recommended for large calculations
- **Storage**: 500MB free disk space for installation, additional space for reports and data
- **Display**: 1024x768 minimum resolution, 1920x1080 recommended
- **Graphics**: Basic graphics card with OpenGL support for 3D visualizations

### Software Requirements
- **Operating System**: Windows 7/8/10/11, macOS 10.12+, or Linux (Ubuntu 16.04+)
- **Python**: Version 3.8 or higher
- **Internet Connection**: Required for initial package installation only

### Dependencies
- **matplotlib**: For generating charts and visualizations
- **numpy**: For numerical calculations
- **pandas**: For data manipulation and analysis
- **fpdf**: For PDF report generation
- **Pillow**: For image processing
- **tkinter**: For GUI interface (usually included with Python)

## Performance Considerations

### Optimization Features
- **Adaptive DPI**: Automatically adjusts image quality based on system capabilities
- **Memory Management**: Efficient handling of large datasets and visualizations
- **Background Processing**: Non-blocking calculations for better user experience
- **File Caching**: Temporary storage for improved performance

### Large Project Handling
- **Batch Processing**: Support for multiple stope designs
- **Export Optimization**: Efficient PDF generation for large reports
- **3D Rendering**: Optimized for different hardware configurations
- **Data Validation**: Real-time input checking to prevent errors

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

## Contributing

We welcome contributions to improve the Mining Stope Design Tool. Here's how you can contribute:

### Development Setup
1. Fork the repository
2. Create a new branch for your feature
3. Set up the development environment following the installation instructions
4. Run tests to ensure everything works: `python -m pytest tests/`

### Code Standards
- Follow PEP 8 style guidelines
- Add docstrings to all functions and classes
- Include unit tests for new functionality
- Ensure compatibility with Indian mining standards

### Reporting Issues
- Use the issue tracker for bug reports
- Include system information and error messages
- Provide steps to reproduce the issue
- Suggest improvements or new features

### Pull Requests
- Ensure all tests pass
- Update documentation as needed
- Follow the existing code style
- Provide clear commit messages

## Version History

### Version 1.0.0 (Current)
- Initial release with core functionality
- DGMS compliance checking
- 3D stope visualization
- PDF report generation
- Support for 8 ore types
- Indian standards implementation

### Planned Features
- **Version 1.1.0**: Enhanced visualization options, additional ore types
- **Version 1.2.0**: Advanced stability analysis, improved cost estimation
- **Version 2.0.0**: Web-based interface, cloud storage integration

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

---

**Important Notes:**
- This tool is designed to assist mining engineers in preliminary design calculations
- All results should be verified by qualified professionals before implementation
- The software follows Indian mining standards but local regulations may vary
- Regular updates ensure compliance with evolving mining regulations

**Contact Information:**
- For technical support: Check the troubleshooting section first
- For regulatory questions: Consult with local DGMS authorities
- For feature requests: Use the contributing guidelines above

**Acknowledgments:**
- DGMS (Directorate General of Mine Safety) for regulatory guidelines
- CMRI (Central Mining Research Institute) for technical standards
- IBM (Indian Bureau of Mines) for compliance frameworks
- The mining engineering community for continuous feedback and improvement

---

*Last Updated: July 2025*  
*Version: 3.0.0*  
*Compatible with Python 3.8+ and Indian Mining Standards*  
*Tested on Windows, macOS, and Linux platforms*

