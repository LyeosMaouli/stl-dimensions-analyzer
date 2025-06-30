# STL Dimensions Analyzer

A user-friendly tool to analyze STL files and extract their dimensions (width, height, depth) with detailed logging and CSV export functionality.

## ✨ Features

- **GUI Folder Selection**: Easy folder selection using system file explorer
- **Batch Processing**: Analyze multiple STL files at once
- **Detailed Measurements**: Extract width (X), depth (Y), height (Z), volume, and triangle count
- **CSV Export**: Generate spreadsheet-compatible data files
- **Comprehensive Logging**: Detailed log files for tracking analysis progress
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Standalone Executable**: Can be compiled to run without Python installation
- **Automatic Naming**: Timestamped output files to avoid conflicts

## 🎯 Use Cases

Perfect for:

- 3D printing enthusiasts managing figurine collections
- Engineers analyzing CAD models
- Quality control processes
- Batch measurement of 3D models
- Documentation and cataloging of STL files

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

3. **Run the script:**
   ```bash
   python stl_analyzer.py
   ```

### Option 2: Create Standalone Executable

1. **Install PyInstaller:**

   ```bash
   pip install pyinstaller numpy-stl
   ```

2. **Build executable:**

   ```bash
   pyinstaller --onefile --windowed --name="STL-Analyzer" stl_analyzer.py
   ```

3. **Find executable in `dist/` folder**

## 📖 Usage

1. **Launch the application**

   - Double-click the executable, or
   - Run `python stl_analyzer.py`

2. **Select STL folder**

   - A file dialog will open
   - Navigate to your folder containing STL files
   - Click "Select Folder"

3. **Wait for processing**

   - The tool will automatically:
     - Scan for STL files
     - Analyze each file's dimensions
     - Generate CSV and log files
     - Display progress and results

4. **View results**
   - CSV file: Spreadsheet with all measurements
   - Log file: Detailed processing information

## 📊 Output Files

The tool generates two files in your selected folder:

### CSV File (`stl_dimensions_YYYYMMDD_HHMMSS.csv`)

Contains columns:

- `file`: STL filename
- `width_x`: Width in mm
- `depth_y`: Depth in mm
- `height_z`: Height in mm
- `volume`: Volume in mm³
- `triangle_count`: Number of triangles in mesh
- `unit`: Measurement unit (mm)
- `status`: Processing status (OK or error message)

### Log File (`stl_dimensions_YYYYMMDD_HHMMSS.log`)

Contains:

- Processing timestamp
- File-by-file progress
- Error messages (if any)
- Summary statistics
- Full execution log

## 📁 Example Output

```
Selected Folder/
├── figurine1.stl
├── figurine2.stl
├── character.stl
├── stl_dimensions_20241230_143052.csv    ← Generated
└── stl_dimensions_20241230_143052.log    ← Generated
```

**CSV Content Example:**

```csv
file,width_x,depth_y,height_z,volume,triangle_count,unit,status
figurine1.stl,25.4,30.2,45.8,12543.7,8432,mm,OK
figurine2.stl,32.1,28.9,52.3,18765.2,9876,mm,OK
character.stl,28.7,35.4,48.1,15234.8,7654,mm,OK
```

## 🔧 Technical Details

### Supported File Formats

- `.stl` and `.STL` files
- Both ASCII and binary STL formats

### Measurement Method

- Calculates bounding box dimensions (min/max coordinates)
- Uses numpy-stl library for reliable STL parsing
- Handles complex geometries and meshes

### Error Handling

- Graceful handling of corrupted STL files
- Detailed error messages in log files
- Continues processing other files if one fails

## 🐛 Troubleshooting

### "numpy-stl not found" Error

```bash
pip install numpy-stl
```

### No GUI Dialog Appears

- Check if dialog is behind other windows
- Fallback text input will be available
- Ensure tkinter is installed (usually bundled with Python)

### "No STL files found"

- Verify files have `.stl` extension
- Check if files are corrupted
- Ensure you selected the correct folder

### Permission Errors

- Run as administrator (Windows) or with sudo (Linux/Mac)
- Check folder write permissions
- Choose a different output location

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
- Uses tkinter for cross-platform GUI dialogs
- Inspired by the 3D printing and maker community

## 📞 Support

- 🐛 Report bugs: [GitHub Issues](https://github.com/LyeosMaouli/stl-dimensions-analyzer/issues)
- 💡 Feature requests: [GitHub Discussions](https://github.com/LyeosMaouli/stl-dimensions-analyzer/discussions)

---

**Made with ❤️ for the 3D printing community**
