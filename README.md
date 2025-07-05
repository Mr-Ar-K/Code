# Mining Stope Design Tool

A comprehensive tool for designing and analyzing mine stope designs with optimized visualizations compliant with Indian mining standards.

## Project Structure

```
project-root/
│
├── src/
│   ├── main.py                 # Main application entry point
│   ├── gui.py                  # GUI implementation
│   ├── stope_calculations.py   # Core stope calculation logic
│   ├── cost_estimation.py      # Cost analysis module
│   ├── stability_analysis.py   # Stability assessment functions
│   ├── ml_models.py            # Machine learning models
│   ├── data_loader.py          # Data loading and preprocessing
│   ├── report_generator.py     # PDF report generation
│   └── input_validation.py     # Input validation utilities
│
├── data/
│   ├── historical_mine_data.csv  # Training dataset
│   └── rock_properties.json    # Rock classification data
│
├── models/
│   └── failure_prediction_model.pkl  # Trained ML model
│
├── reports/                   # Generated PDF reports
│
└── tests/                     # Unit tests
    ├── test_calculations.py
    ├── test_validation.py
    └── test_ml_models.py
```

## Features

- **Realistic Stope Design**: Generates compliant designs for various stope types (Sublevel Stoping, Room-and-Pillar, Cut-and-Fill, Shrinkage Stoping, Vertical Crater Retreat)
- **Stability Analysis**: Calculates safety factors and stability assessment based on Indian DGMS standards
- **Cost Estimation**: Provides detailed mining cost analysis and breakdown 
- **Optimized Visualizations**: Generates multi-view stope visualizations with performance optimization for low-end systems
- **Report Generation**: Creates comprehensive PDF reports

## Performance Optimizations

The visualization system includes the following optimizations for low-end PCs:

1. **Asynchronous 3D Rendering**: Uses ThreadPoolExecutor to render 3D visualizations in a background thread
2. **Adaptive DPI**: Automatically adjusts DPI settings based on image size to prevent memory issues
3. **Pixel Size Capping**: Enforces maximum pixel dimensions to avoid excessive memory consumption
4. **Reduced Complexity**: Minimized geological layers in cross-section views
5. **Memory Management**: Careful figure closing and resource management

These optimizations ensure the tool runs smoothly even on machines with limited resources.

## Requirements

All dependencies are listed in `requirements.txt`. Install using:

```bash
pip install -r requirements.txt
```

## Usage

Run the application with:

```bash
python src/main.py
```

### Input Parameters

- **RQD Value**: Rock Quality Designation (0-100)
- **Dip Angle**: Orebody dip in degrees
- **Mining Depth**: Depth below surface in meters
- **Ore Thickness**: Thickness of the ore body in meters

### Output

- Recommended stope design with dimensions
- Stability analysis with safety factor (auto-calculated per DGMS standards)
- Cost estimation
- Multiple visualization views (3D isometric, plan view, cross-section)
- PDF report with all analyses and visualizations

## Indian Mining Standards Compliance

This tool follows the Directorate General of Mine Safety (DGMS) standards, including:
- Minimum safety factor of 1.5
- Minimum pillar width of 3.0m
- CMRI RMR adjustment for Indian rock conditions
- IBE stress factor calculations

## License

[MIT License]
