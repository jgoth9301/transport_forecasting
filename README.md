# Geospatial Energy Data Visualization Dashboard

This project presents an interactive dashboard designed to visualize global energy data with a focus on geospatial representation. The dashboard aims to assist policymakers and analysts in understanding energy dependencies and risks across different countries through intuitive visualizations.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Data Sources](#data-sources)
- [Customization](#customization)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Project Overview

In light of increasing geopolitical tensions and the strategic importance of energy security, this project delivers a dashboard that provides a comprehensive, data-driven overview of the current global energy landscape. By leveraging geospatial data visualization techniques, the dashboard enables users to explore and analyze energy production, consumption, and risk indicators at the country level.

## Features

- **Interactive World Map**: Visualizes countries color-coded based on an aggregated risk indicator (`risk_sum`), allowing users to identify regions with higher energy vulnerabilities.
- **Dynamic Country Profile**: Displays key information about the selected country, including population and energy-related metrics.
- **Electricity Generation vs. Demand Chart**: Compares the electricity demand and generation of the selected country, highlighting potential imbalances.
- **Energy Mix Breakdown**: Provides a detailed view of the country's electricity generation sources, categorized into fossil fuels, nuclear, and renewables.
- **Automated Zoom and Highlighting**: Upon selecting a country, the map zooms in and dims non-selected countries to emphasize the focus area.
- **Reset Functionality**: Allows users to revert to the initial view, facilitating seamless exploration of different countries.

## Installation

To set up the dashboard locally, follow these steps:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/jgoth9301/geo_spatial_data_visualization.git
   ```

2. **Navigate to the Project Directory**:

   ```bash
   cd geo_spatial_data_visualization
   ```

3. **Set Up a Virtual Environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'
   ```

4. **Install Required Packages**:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

After installation, launch the dashboard with:

```bash
python app.py
```

Then, open your web browser and go to `http://127.0.0.1:8050/` to interact with the dashboard.

## Project Structure

- `data_input/`: Contains scripts and data related to data extraction and preparation.
- `data_visualization/`: Houses the main dashboard application and related visualization scripts.
- `requirements.txt`: Lists the Python packages required to run the project.
- `README.md`: Provides an overview and instructions for the project.

## Data Sources

The dashboard utilizes publicly available geospatial energy data from [Our World in Data](https://github.com/owid/energy-data). This dataset offers comprehensive information on energy production, consumption, and trade at a global level, disaggregated by energy source and country.

## Customization

Users can customize various aspects of the dashboard:

- **Color Schemes**: Adjust the color coding for risk indicators and energy sources by modifying the visualization scripts in `data_visualization/`.
- **Risk Indicator Calculation**: The `risk_sum` metric can be tailored by altering the data preparation scripts in `data_input/` to reflect different weighting or additional factors.
- **Layout Adjustments**: Modify the dashboard's layout components to suit specific presentation needs by editing the `app.py` file.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

Please ensure your code adheres to the project's coding standards and includes appropriate documentation.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Acknowledgements

Special thanks to [Our World in Data](https://ourworldindata.org/) for providing the comprehensive energy dataset that underpins this dashboard.
