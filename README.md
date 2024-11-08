# LoDCalculator

## Overview
LoDCalculator is a Blender add-on designed to analyze the level of detail (LoD) of 3D models. It evaluates geometric and radiometric fidelity, providing scores and raw data that help assess the quality of your models. Blender version 2.8 or higher is required to install LoDCalculator. You can download the latest version of Blender from the following link: https://www.blender.org/download/
The examples.blend file contains a series of 3D models with which to test this add-on.

## Installation

1. **Download** the `LoDCalculator.py` file from this repository.
2. **Open Blender** and navigate to the Preferences menu.
3. Go to the **Add-ons** section.
4. Click on **Install from local disk** and select the downloaded `.py` file.
5. The add-on is now installed and a new section called **LoDCalculator** will appear in the Scene Properties panel.

## Usage

1. **Select a 3D Model**: Choose the model you want to analyze in the Blender viewport.
2. **Analyze the Model**: Click the **Calculate Result** button in the LoDCalculator panel.
3. **Review Results**: The results will display the LoD score and analysis data. If there are issues (e.g., no model selected, non-mesh object, or model without textures), an error notification will appear, and the analysis will receive the lowest possible score.

### Scoring System
- **LoD Score**: Ranges from 1 to 5, with half-point divisions, evaluating the overall model quality.
- **Partial Scores**:
  - **Geometric Fidelity**: Ranges from 1 to 3, assessing the geometric detail of the model.
  - **Radiometric Fidelity**: Ranges from 1 to 3, evaluating textures and materials.

### Analysis Data
When an analysis is executed, you can view:
- **Raw Data**: Including the last interquartile range and average angles of the model's faces.
- **Model Statistics**: Number of faces and meshes, average faces per mesh, number of textures and materials, average resolution of textures, and percentage of tiled faces.

### Relative Data Comparison
LoDCalculator can compare models of different scales, whether they consist of a single mesh or multiple complex meshes.

## Uninstallation
To uninstall LoDCalculator:
1. Go back to Blender's Preferences.
2. Navigate to the Add-ons section.
3. Click on **Uninstall** for LoDCalculator.

## Contributing
If you would like to contribute to LoDCalculator, feel free to fork the repository and submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
