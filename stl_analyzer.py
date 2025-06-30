#!/usr/bin/env python3
"""
STL Dimensions Analyzer - Executable Version with GUI Folder Selection
Analyzes STL files in a user-selected folder and generates CSV and log files
Can be compiled to executable using PyInstaller

Features:
- GUI folder selection dialog (with fallback to manual input)
- Automatic STL file detection and validation
- CSV export with dimensions data
- Detailed logging
- Cross-platform compatibility

Usage:
  python stl_analyzer.py
  
To create executable:
  pip install pyinstaller numpy-stl
  pyinstaller --onefile --windowed --name="STL-Analyzer" stl_analyzer.py
  
Dependencies:
  - numpy-stl (for STL file processing)
  - tkinter (built-in with Python, for GUI dialogs)
"""

import os
import sys
from pathlib import Path
import csv
from datetime import datetime
import traceback
import re

# Handle file dialog import for both development and executable
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

# Handle numpy-stl import for both development and executable
try:
    from stl import mesh
    import numpy as np
    STL_AVAILABLE = True
except ImportError:
    STL_AVAILABLE = False
    print("Warning: numpy-stl not found. Please install with: pip install numpy-stl")

class Logger:
    """Class to manage logs both in terminal and log file"""
    
    def __init__(self, log_file_path):
        self.log_file = log_file_path
        self.terminal = sys.stdout
        
        # Create log file
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"=== STL ANALYSIS LOG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
        except Exception as e:
            print(f"Warning: Could not create log file: {e}")
            self.log_file = None
    
    def print(self, *args, **kwargs):
        """Print both to terminal and log file"""
        # Display in terminal
        print(*args, **kwargs)
        
        # Write to log file
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    print(*args, **kwargs, file=f)
            except Exception:
                pass  # Silently ignore log file errors
    
    def print_separator(self, char="=", length=60):
        """Display separator line"""
        self.print(char * length)

def get_stl_dimensions(stl_file_path):
    """
    Calculate dimensions of an STL file
    
    Args:
        stl_file_path (str): Path to STL file
        
    Returns:
        dict: Dictionary containing model dimensions and information
    """
    if not STL_AVAILABLE:
        return {
            'file': os.path.basename(stl_file_path),
            'width_x': 0,
            'depth_y': 0,
            'height_z': 0,
            'volume': 0,
            'triangle_count': 0,
            'unit': 'mm',
            'status': 'Error: numpy-stl not installed'
        }
    
    try:
        # Load STL mesh
        stl_mesh = mesh.Mesh.from_file(stl_file_path)
        
        # Extract all points from mesh
        points = stl_mesh.points.reshape(-1, 3)
        
        # Calculate dimensions by finding min/max for each axis
        min_coords = np.min(points, axis=0)
        max_coords = np.max(points, axis=0)
        
        dimensions = max_coords - min_coords
        
        # Approximate volume of mesh
        try:
            volume = stl_mesh.get_mass_properties()[0]
        except:
            volume = 0  # Fallback if volume calculation fails
        
        return {
            'file': os.path.basename(stl_file_path),
            'width_x': round(dimensions[0], 3),
            'depth_y': round(dimensions[1], 3),
            'height_z': round(dimensions[2], 3),
            'volume': round(volume, 3),
            'triangle_count': len(stl_mesh.vectors),
            'unit': 'mm',  # STL files are typically in mm
            'status': 'OK'
        }
        
    except Exception as e:
        return {
            'file': os.path.basename(stl_file_path),
            'width_x': 0,
            'depth_y': 0,
            'height_z': 0,
            'volume': 0,
            'triangle_count': 0,
            'unit': 'mm',
            'status': f'Error: {str(e)}'
        }

def analyze_stl_directory(directory_path, output_csv=None, logger=None):
    """
    Analyze all STL files in a directory
    
    Args:
        directory_path (str): Path to directory containing STL files
        output_csv (str): Optional path to save CSV
        logger (Logger): Logger instance for messages
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        logger.print(f"Error: Directory {directory_path} does not exist")
        return
    
    # Find all STL files (exclude CSV, log, and text files)
    all_files = list(directory.glob("*.stl")) + list(directory.glob("*.STL"))
    stl_files = [f for f in all_files if not f.name.lower().endswith(('.csv', '.log', '.txt'))]
    
    if not stl_files:
        logger.print(f"No STL files found in {directory_path}")
        return
    
    # Remove duplicates based on filename (case insensitive)
    unique_files = {}
    for stl_file in stl_files:
        file_key = stl_file.name.lower()
        if file_key not in unique_files:
            unique_files[file_key] = stl_file
    
    stl_files = list(unique_files.values())
    
    logger.print(f"Analyzing {len(stl_files)} unique STL file(s)...")
    logger.print_separator("-", 80)
    
    results = []
    
    for i, stl_file in enumerate(stl_files, 1):
        logger.print(f"[{i}/{len(stl_files)}] Processing: {stl_file.name}", end=" ... ")
        dimensions = get_stl_dimensions(str(stl_file))
        results.append(dimensions)
        
        # Condensed status display
        if dimensions['status'] == 'OK':
            logger.print(f"✅ {dimensions['width_x']}×{dimensions['depth_y']}×{dimensions['height_z']} mm")
        else:
            logger.print(f"❌ {dimensions['status']}")
    
    # Save to CSV
    if output_csv:
        save_to_csv(results, output_csv, logger)
    
    return results

def save_to_csv(results, csv_file_path, logger=None):
    """
    Save results to CSV file
    
    Args:
        results (list): List of result dictionaries
        csv_file_path (str): Path to output CSV file
        logger (Logger): Logger instance for messages
    """
    if not results:
        return
    
    try:
        fieldnames = results[0].keys()
        
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        if logger:
            logger.print(f"CSV file saved successfully: {os.path.basename(csv_file_path)}")
            
    except Exception as e:
        if logger:
            logger.print(f"Error saving CSV file: {e}")

def get_stl_directory():
    """
    Get STL directory using file dialog or fallback to text input
    Returns the validated directory path
    """
    print("STL Dimensions Analyzer")
    print("=" * 50)
    
    if TKINTER_AVAILABLE:
        print("Opening folder selection dialog...")
        print("(If no dialog appears, check if it's behind other windows)")
        
        # Create root window but keep it hidden
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        root.lift()      # Bring to front
        root.attributes('-topmost', True)  # Keep on top
        
        try:
            # Open folder selection dialog
            directory_path = filedialog.askdirectory(
                title="Select folder containing STL files",
                mustexist=True
            )
            
            # Clean up tkinter
            root.destroy()
            
            # Check if user cancelled
            if not directory_path:
                print("No folder selected. Exiting...")
                sys.exit(0)
            
            directory_path = os.path.abspath(directory_path)
            
            # Check for STL files
            stl_files = []
            for ext in ['*.stl', '*.STL']:
                stl_files.extend(Path(directory_path).glob(ext))
            
            # Filter out non-STL files
            stl_files = [f for f in stl_files if f.name.lower().endswith(('.stl',))]
            
            if not stl_files:
                if TKINTER_AVAILABLE:
                    root = tk.Tk()
                    root.withdraw()
                    messagebox.showwarning("No STL Files", 
                                         f"No STL files found in the selected folder:\n{directory_path}\n\n"
                                         "Please select a folder containing STL files.")
                    root.destroy()
                
                print(f"⚠️  No STL files found in: {directory_path}")
                print("Please make sure the folder contains .stl files.")
                input("Press Enter to exit...")
                sys.exit(0)
            
            print(f"✅ Selected folder: {directory_path}")
            print(f"✅ Found {len(stl_files)} STL file(s)")
            return directory_path
            
        except Exception as e:
            print(f"Error with file dialog: {e}")
            print("Falling back to manual input...")
            # Clean up tkinter if needed
            try:
                root.destroy()
            except:
                pass
            # Fall through to manual input
    
    # Fallback to manual input if tkinter not available or dialog failed
    if not TKINTER_AVAILABLE:
        print("File dialog not available. Please enter the path manually.")
    
    print("\nPlease specify the directory containing your STL files.")
    print("Examples:")
    print("  Windows: C:\\Users\\YourName\\Desktop\\STL_Files")
    print("  Mac/Linux: /home/username/stl_files or ~/Desktop/stl_files")
    print()
    
    while True:
        # Get user input
        user_input = input("Enter the path to your STL directory (or 'q' to quit): ").strip()
        
        # Check if user wants to quit
        if user_input.lower() in ['q', 'quit', 'exit']:
            print("Exiting...")
            sys.exit(0)
        
        # Handle empty input
        if not user_input:
            print("❌ Please enter a valid directory path.")
            continue
        
        # Expand user path (handles ~ and relative paths)
        directory_path = os.path.expanduser(user_input)
        directory_path = os.path.abspath(directory_path)
        
        # Check if directory exists
        if not os.path.exists(directory_path):
            print(f"❌ Directory does not exist: {directory_path}")
            continue
        
        if not os.path.isdir(directory_path):
            print(f"❌ Path is not a directory: {directory_path}")
            continue
        
        # Check for STL files
        stl_files = []
        for ext in ['*.stl', '*.STL']:
            stl_files.extend(Path(directory_path).glob(ext))
        
        # Filter out non-STL files
        stl_files = [f for f in stl_files if f.name.lower().endswith(('.stl',))]
        
        if not stl_files:
            print(f"⚠️  No STL files found in: {directory_path}")
            retry = input("Do you want to try another directory? (y/n): ").strip().lower()
            if retry in ['n', 'no']:
                print("Exiting...")
                sys.exit(0)
            continue
        
        # Success - directory found with STL files
        print(f"✅ Found {len(stl_files)} STL file(s) in: {directory_path}")
        print()
        return directory_path

def get_output_filename():
    """
    Generate automatic filename with timestamp
    Returns the base filename (without extension)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"stl_dimensions_{timestamp}"

def main():
    """Main function"""
    try:
        # Get STL directory from user
        stl_directory = get_stl_directory()
        
        # Get output filename (automatic with timestamp)
        base_filename = get_output_filename()
        
        print(f"Output files will be named: {base_filename}.csv / {base_filename}.log")
        print()
        
        # Create full paths for output files
        output_csv = os.path.join(stl_directory, f"{base_filename}.csv")
        log_file = os.path.join(stl_directory, f"{base_filename}.log")
        
        # Initialize logger
        logger = Logger(log_file)
        
        # Display startup information
        logger.print("STL Dimensions Analyzer - Processing Started")
        logger.print_separator()
        logger.print(f"Source directory: {stl_directory}")
        logger.print(f"Output CSV file: {os.path.basename(output_csv)}")
        logger.print(f"Log file: {os.path.basename(log_file)}")
        logger.print_separator()
        
        # Check if numpy-stl is available
        if not STL_AVAILABLE:
            logger.print("❌ ERROR: numpy-stl library not found!")
            logger.print("Please install it with: pip install numpy-stl")
            logger.print("The program will continue but STL analysis will fail.")
            logger.print_separator()
        
        # Analyze STL directory and generate CSV
        results = analyze_stl_directory(stl_directory, output_csv, logger)
        
        if results:
            logger.print_separator()
            logger.print(f"✅ Analysis completed! {len(results)} unique file(s) processed")
            
            # Display summary
            successful = len([r for r in results if r['status'] == 'OK'])
            failed = len(results) - successful
            
            logger.print(f"✅ Successful: {successful} file(s)")
            if failed > 0:
                logger.print(f"❌ Errors: {failed} file(s)")
            
            logger.print(f"\n📁 Output directory: {os.path.abspath(stl_directory)}")
            logger.print(f"📋 Generated files:")
            logger.print(f"   - {os.path.basename(output_csv)} (data)")
            logger.print(f"   - {os.path.basename(log_file)} (log)")
            
            # Show first few results as preview
            if successful > 0:
                logger.print(f"\n📊 Preview of results:")
                for i, result in enumerate([r for r in results if r['status'] == 'OK'][:3]):
                    logger.print(f"   {result['file']}: {result['width_x']}×{result['depth_y']}×{result['height_z']} mm")
                if successful > 3:
                    logger.print(f"   ... and {successful - 3} more files")
        else:
            logger.print("❌ No STL files found or processed")
        
        # Wait for user input
        logger.print("\nAnalysis complete!")
        input("Press Enter to exit...")
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        input("Press Enter to exit...")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Error details:")
        print(traceback.format_exc())
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()