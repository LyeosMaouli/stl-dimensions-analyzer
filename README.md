# STL Dimensions Analyzer

A user-friendly tool with modern GUI to analyze STL files and extract their dimensions (width, height, depth) with detailed logging and CSV export functionality. Now supports recursive folder scanning!

## ✨ Features

- **Modern GUI Interface**: Intuitive graphical interface with real-time progress tracking
- **Recursive Folder Search**: Toggle to include/exclude subfolders in analysis
- **Batch Processing**: Analyze multiple STL files at once across multiple directories
- **Detailed Measurements**: Extract width (X), depth (Y), height (Z), volume, and triangle count
- **CSV Export**: Generate spreadsheet-compatible data files with folder organization
- **Real-time Progress**: Visual progress bar and status updates during processing
- **Results Viewer**: Integrated table view with sortable columns and color coding
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Standalone Executable**: Can be compiled to run without Python installation
- **Automatic Naming**: Timestamped output files to avoid conflicts

## 🎯 Use Cases

Perfect for:

- 3D printing enthusiasts managing organized figurine collections
- Engineers analyzing CAD models in structured directories
- Quality control processes across project folders
- Batch measurement of 3D models with hierarchical organization
- Documentation and cataloging of STL files in complex folder structures

## 📋 Requirements

### For Python Script

- Python 3.6+
- `numpy-stl` library
- `tkinter` (usually included with Python)

### For Standalone Executable

- No requirements - runs independently

## 🚀 Installation

### Option 1: Run as Python Script

1. **Clone the repository:**

   ```bash
   git clone https://github.com/LyeosMaouli/stl-dimensions-analyzer.git
   cd stl-dimensions-analyzer
   ```

2. **Install dependencies:**

   ```bash
   pip install numpy-stl
   ```

3. **Run the GUI version:**
   ```bash
   python stl_analyzer_gui.py
   ```

### Option 2: Create Standalone Executable

1. **Install PyInstaller:**

   ```bash
   pip install pyinstaller numpy-stl
   ```

2. **Build GUI executable:**

   ```bash
   pyinstaller --onefile --windowed --name="STL-Analyzer-GUI" stl_analyzer_gui.py
   ```

3. **Find executable in `dist/` folder**

## 📖 Usage

### GUI Version (Recommended)

1. **Launch the application**

   - Double-click the executable, or
   - Run `python stl_analyzer_gui.py`

2. **Select STL folder**

   - Click "Browse..." button
   - Navigate to your folder containing STL files
   - Choose whether to include subfolders with the checkbox

3. **Configure search options**

   - ✅ **Include subfolders**: Search recursively through all subdirectories
   - ❌ **Main folder only**: Search only in the selected folder

4. **Start analysis**

   - Click "Analyze STL Files"
   - Watch real-time progress and file-by-file updates
   - View results in the integrated table

5. **Export and access results**
   - Results are automatically exported to CSV
   - Use "Export Results" for custom filename/location
   - Click "Open Output Folder" to access files

## 🔍 Recursive Search Feature

The tool now supports scanning subfolders, perfect for organized collections:

```
📁 MySTLCollection/
├── 📁 Characters/
│   ├── hero.stl
│   ├── villain.stl
│   └── 📁 NPCs/
│       ├── guard.stl
│       └── merchant.stl
├── 📁 Vehicles/
│   ├── tank.stl
│   └── spaceship.stl
└── base_terrain.stl
```

**With recursive search enabled**: Finds all 7 STL files across all folders  
**With recursive search disabled**: Finds only `base_terrain.stl` in the main folder

## 📊 Output Files

The tool generates CSV files in your selected folder:

### CSV File (`stl_dimensions_YYYYMMDD_HHMMSS.csv`)

Contains columns:

- `folder`: Relative folder path (shows subfolder organization)
- `file`: STL filename
- `width_x`: Width in mm
- `depth_y`: Depth in mm
- `height_z`: Height in mm
- `volume`: Volume in mm³
- `triangle_count`: Number of triangles in mesh
- `unit`: Measurement unit (mm)
- `status`: Processing status (OK or error message)

## 📁 Example Output

### Folder Structure

```
MyModels/
├── Characters/
│   ├── warrior.stl
│   └── mage.stl
├── Props/
│   └── sword.stl
├── terrain.stl
└── stl_dimensions_20241230_143052.csv    ← Generated
```

### CSV Content Example

```csv
folder,file,width_x,depth_y,height_z,volume,triangle_count,unit,status
.,terrain.stl,100.5,150.2,5.8,45234.7,12432,mm,OK
Characters,warrior.stl,25.4,30.2,45.8,12543.7,8432,mm,OK
Characters,mage.stl,23.1,28.9,42.3,11765.2,7876,mm,OK
Props,sword.stl,2.7,35.4,8.1,234.8,1654,mm,OK
```

## 🖥️ GUI Interface Features

### Main Interface

- **Folder Selection**: Browse button with path display
- **Recursive Toggle**: Checkbox to include/exclude subfolders
- **File Counter**: Shows number of STL files found
- **Progress Tracking**: Real-time progress bar and status updates

### Results Table

- **Sortable Columns**: Click headers to sort by any column
- **Color Coding**: Green for successful analysis, red for errors
- **Folder Organization**: See which subfolder each file came from
- **Auto-scroll**: Follows progress during analysis

### Action Buttons

- **Analyze STL Files**: Start the analysis process
- **Export Results**: Save results with custom filename
- **Open Output Folder**: Quick access to results location

## 🔧 Technical Details

### Supported File Formats

- `.stl` and `.STL` files
- Both ASCII and binary STL formats

### Search Capabilities

- **Non-recursive**: Scans only the selected folder
- **Recursive**: Scans all subfolders using Python's `rglob()`
- **Duplicate Handling**: Uses full path to distinguish same filenames in different folders

### Measurement Method

- Calculates bounding box dimensions (min/max coordinates)
- Uses numpy-stl library for reliable STL parsing
- Handles complex geometries and meshes

### Performance

- **Background Processing**: GUI remains responsive during analysis
- **Progress Updates**: Real-time feedback on processing status
- **Memory Efficient**: Processes files one at a time

## 🐛 Troubleshooting

### "numpy-stl not found" Error

```bash
pip install numpy-stl
```

### No GUI Dialog Appears

- Check if dialog is behind other windows
- Ensure tkinter is installed (usually bundled with Python)
- Try running from command line to see error messages

### "No STL files found"

- Verify files have `.stl` extension (case insensitive)
- Try toggling the "Include subfolders" option
- Check if files are corrupted or in use by other applications

### Performance Issues with Large Collections

- Consider processing smaller batches
- Ensure sufficient disk space for output files
- Close other applications if memory is limited

### Permission Errors

- Run as administrator (Windows) or with sudo (Linux/Mac)
- Check folder write permissions
- Choose a different output location

## 🆕 Version History

### v1.1.0 - GUI with Recursive Search

- Added modern GUI interface
- Implemented recursive folder scanning
- Real-time progress tracking
- Integrated results viewer
- Background processing with threading

### v1.0.0 - Initial Release

- Command-line interface
- Basic STL dimension analysis
- CSV export functionality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👏 Acknowledgments

- Built with [numpy-stl](https://github.com/WoLpH/numpy-stl) library
- Uses tkinter for cross-platform GUI
- Threading for responsive user interface
- Inspired by the 3D printing and maker community

## 📞 Support

- 🐛 Report bugs: [GitHub Issues](https://github.com/LyeosMaouli/stl-dimensions-analyzer/issues)

---

**Made with ❤️ for the 3D printing community**
