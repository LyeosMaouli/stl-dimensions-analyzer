#!/usr/bin/env python3
"""
STL Dimensions Analyzer - GUI Version
A complete graphical interface for analyzing STL files and extracting dimensions

Features:
- Modern GUI with progress tracking
- Drag & drop folder selection
- Real-time progress updates
- Integrated results viewer
- Export options

Dependencies:
- tkinter (built-in)
- numpy-stl
- threading (built-in)
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import csv
from datetime import datetime
import threading
import queue
import webbrowser

# Handle numpy-stl import
try:
    from stl import mesh
    import numpy as np
    STL_AVAILABLE = True
except ImportError:
    STL_AVAILABLE = False

class STLAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("STL Dimensions Analyzer v1.1.0")
        self.root.geometry("800x600")
        self.root.minsize(600, 500)
        
        # Variables
        self.selected_folder = tk.StringVar()
        self.recursive_search = tk.BooleanVar(value=False)  # Toggle for recursive search
        self.processing = False
        self.stop_requested = False  # Flag for stopping analysis
        self.results = []
        self.output_queue = queue.Queue()
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        self.center_window()
        
        # Check dependencies
        if not STL_AVAILABLE:
            self.show_dependency_warning()
    
    def setup_styles(self):
        """Configure ttk styles for modern appearance"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 10))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Big.TButton', font=('Arial', 10, 'bold'))
    
    def create_widgets(self):
        """Create and layout all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="STL Dimensions Analyzer", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Folder selection section
        folder_frame = ttk.LabelFrame(main_frame, text="Select STL Folder", padding="10")
        folder_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        folder_frame.columnconfigure(1, weight=1)
        
        ttk.Label(folder_frame, text="Folder:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.selected_folder, 
                                     state='readonly', width=50)
        self.folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.browse_button = ttk.Button(folder_frame, text="Browse...", 
                                       command=self.browse_folder)
        self.browse_button.grid(row=0, column=2)
        
        # Recursive search option
        self.recursive_checkbox = ttk.Checkbutton(
            folder_frame, 
            text="Include subfolders (recursive search)", 
            variable=self.recursive_search,
            command=self.on_recursive_toggle
        )
        self.recursive_checkbox.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # File count display
        self.file_count_label = ttk.Label(folder_frame, text="No folder selected")
        self.file_count_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.analyze_button = ttk.Button(button_frame, text="Analyze STL Files", 
                                        command=self.start_analysis, 
                                        style='Big.TButton', state='disabled')
        self.analyze_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Analysis", 
                                     command=self.stop_analysis, 
                                     state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_button = ttk.Button(button_frame, text="Export Results", 
                                       command=self.export_results, state='disabled')
        self.export_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.open_folder_button = ttk.Button(button_frame, text="Open Output Folder", 
                                            command=self.open_output_folder, state='disabled')
        self.open_folder_button.pack(side=tk.LEFT)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.progress_label = ttk.Label(progress_frame, text="Ready to analyze files")
        self.progress_label.grid(row=1, column=0, sticky=tk.W)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Create Treeview for results
        columns = ('Folder', 'File', 'Width (mm)', 'Depth (mm)', 'Height (mm)', 'Volume (mm³)', 'Triangles', 'Status')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=10)
        
        # Configure columns
        column_widths = {'Folder': 150, 'File': 200, 'Width (mm)': 80, 'Depth (mm)': 80, 
                        'Height (mm)': 80, 'Volume (mm³)': 100, 'Triangles': 80, 'Status': 80}
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=column_widths.get(col, 100), minwidth=50)
        
        # Scrollbars for treeview
        v_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid treeview and scrollbars
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_dependency_warning(self):
        """Show warning dialog for missing dependencies"""
        message = ("numpy-stl library not found!\n\n"
                  "To install it, run:\n"
                  "pip install numpy-stl\n\n"
                  "The application will continue but STL analysis will fail.")
        messagebox.showwarning("Missing Dependency", message)
    
    def on_recursive_toggle(self):
        """Handle recursive search toggle"""
        if self.selected_folder.get():
            self.scan_folder()
    
    def find_stl_files(self, folder_path, recursive=False):
        """
        Find STL files in folder, optionally including subfolders
        
        Args:
            folder_path (str): Path to search
            recursive (bool): Whether to search subfolders
            
        Returns:
            list: List of Path objects for STL files
        """
        stl_files = []
        folder = Path(folder_path)
        
        if recursive:
            # Recursive search using rglob
            for ext in ['**/*.stl', '**/*.STL']:
                stl_files.extend(folder.rglob(ext.split('/')[-1]))
        else:
            # Non-recursive search using glob
            for ext in ['*.stl', '*.STL']:
                stl_files.extend(folder.glob(ext))
        
        # Filter and deduplicate
        unique_files = {}
        for stl_file in stl_files:
            if stl_file.name.lower().endswith('.stl') and stl_file.is_file():
                # Use full path as key to allow same filenames in different folders
                file_key = str(stl_file)
                unique_files[file_key] = stl_file
        
        return list(unique_files.values())
        """Open folder selection dialog"""
        folder = filedialog.askdirectory(title="Select folder containing STL files")
        if folder:
            self.selected_folder.set(folder)
            self.scan_folder()
    
    def browse_folder(self):
        """Open folder selection dialog"""
        folder = filedialog.askdirectory(title="Select folder containing STL files")
        if folder:
            self.selected_folder.set(folder)
            self.scan_folder()
    
    def scan_folder(self):
        """Scan selected folder for STL files"""
        folder = self.selected_folder.get()
        if not folder:
            return
        
        try:
            # Find STL files based on recursive setting
            recursive = self.recursive_search.get()
            stl_files = self.find_stl_files(folder, recursive)
            count = len(stl_files)
            
            if count > 0:
                # Show folder distribution if recursive
                if recursive:
                    folder_count = len(set(str(f.parent) for f in stl_files))
                    if folder_count > 1:
                        count_text = f"✅ Found {count} STL file(s) in {folder_count} folder(s)"
                    else:
                        count_text = f"✅ Found {count} STL file(s)"
                else:
                    count_text = f"✅ Found {count} STL file(s)"
                
                self.file_count_label.config(text=count_text, style='Success.TLabel')
                self.analyze_button.config(state='normal')
                self.status_var.set(f"Found {count} STL files - Ready to analyze")
            else:
                search_type = "recursively" if recursive else "in main folder"
                self.file_count_label.config(text=f"❌ No STL files found {search_type}", 
                                           style='Error.TLabel')
                self.analyze_button.config(state='disabled')
                self.status_var.set(f"No STL files found {search_type}")
                
        except Exception as e:
            self.file_count_label.config(text=f"❌ Error scanning folder: {e}", 
                                       style='Error.TLabel')
            self.analyze_button.config(state='disabled')
    
    def start_analysis(self):
        """Start STL analysis in background thread"""
        if self.processing:
            return
        
        self.processing = True
        self.stop_requested = False
        self.analyze_button.config(state='disabled', text="Analyzing...")
        self.stop_button.config(state='normal')
        self.export_button.config(state='disabled')
        self.browse_button.config(state='disabled')
        self.recursive_checkbox.config(state='disabled')
        
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.results = []
        
        # Start background thread
        thread = threading.Thread(target=self.analyze_files_thread)
        thread.daemon = True
        thread.start()
        
        # Start checking for updates
        self.check_queue()
    
    def stop_analysis(self):
        """Request to stop the current analysis"""
        if self.processing:
            self.stop_requested = True
            self.stop_button.config(state='disabled', text="Stopping...")
            self.progress_label.config(text="Stop requested - finishing current file...")
            self.status_var.set("Stop requested - finishing current file...")
    
    def analyze_files_thread(self):
        """Background thread for file analysis"""
        try:
            folder = self.selected_folder.get()
            recursive = self.recursive_search.get()
            
            # Find STL files
            stl_files = self.find_stl_files(folder, recursive)
            total_files = len(stl_files)
            
            search_type = "recursively" if recursive else "in main folder"
            self.output_queue.put(('status', f"Analyzing {total_files} files {search_type}..."))
            
            # Process each file
            processed_count = 0
            for i, stl_file in enumerate(stl_files):
                # Check if stop was requested
                if self.stop_requested:
                    self.output_queue.put(('status', f"Analysis stopped by user after {processed_count}/{total_files} files"))
                    self.output_queue.put(('stopped', processed_count))
                    return
                
                progress = (i / total_files) * 100
                self.output_queue.put(('progress', progress))
                
                # Show relative path for better context
                relative_path = os.path.relpath(str(stl_file), folder)
                self.output_queue.put(('status', f"Processing ({i+1}/{total_files}): {relative_path}"))
                
                # Analyze file
                result = self.get_stl_dimensions(str(stl_file), folder)
                self.results.append(result)
                self.output_queue.put(('result', result))
                processed_count += 1
            
            # Complete (only if not stopped)
            if not self.stop_requested:
                self.output_queue.put(('progress', 100))
                search_info = f" {search_type}" if recursive else ""
                self.output_queue.put(('status', f"Analysis complete! {total_files} files processed{search_info}"))
                self.output_queue.put(('complete', None))
            
        except Exception as e:
            self.output_queue.put(('error', str(e)))
    
    def check_queue(self):
        """Check for updates from background thread"""
        try:
            while True:
                msg_type, data = self.output_queue.get_nowait()
                
                if msg_type == 'progress':
                    self.progress_var.set(data)
                elif msg_type == 'status':
                    self.progress_label.config(text=data)
                    self.status_var.set(data)
                elif msg_type == 'result':
                    self.add_result_to_tree(data)
                elif msg_type == 'complete':
                    self.analysis_complete()
                elif msg_type == 'stopped':
                    self.analysis_stopped(data)
                elif msg_type == 'error':
                    self.analysis_error(data)
                    
        except queue.Empty:
            pass
        
        if self.processing:
            self.root.after(100, self.check_queue)
    
    def add_result_to_tree(self, result):
        """Add analysis result to the treeview"""
        values = (
            result['folder'],
            result['file'],
            result['width_x'],
            result['depth_y'], 
            result['height_z'],
            result['volume'],
            result['triangle_count'],
            result['status']
        )
        
        # Color code based on status
        tags = ('success',) if result['status'] == 'OK' else ('error',)
        self.results_tree.insert('', tk.END, values=values, tags=tags)
        
        # Configure tags
        self.results_tree.tag_configure('success', foreground='black')
        self.results_tree.tag_configure('error', foreground='red')
        
        # Auto-scroll to bottom
        children = self.results_tree.get_children()
        if children:
            self.results_tree.see(children[-1])
    
    def analysis_complete(self):
        """Handle analysis completion"""
        self.processing = False
        self.stop_requested = False
        self.analyze_button.config(state='normal', text="Analyze STL Files")
        self.stop_button.config(state='disabled', text="Stop Analysis")
        self.export_button.config(state='normal')
        self.open_folder_button.config(state='normal')
        self.browse_button.config(state='normal')
        self.recursive_checkbox.config(state='normal')
        
        # Show summary
        successful = len([r for r in self.results if r['status'] == 'OK'])
        total = len(self.results)
        failed = total - successful
        
        summary = f"✅ Analysis Complete: {successful}/{total} files successful"
        if failed > 0:
            summary += f", {failed} failed"
        
        self.progress_label.config(text=summary)
        self.status_var.set(summary)
        
        # Auto-export results
        self.auto_export_results()
    
    def analysis_stopped(self, processed_count):
        """Handle analysis stop"""
        self.processing = False
        self.stop_requested = False
        self.analyze_button.config(state='normal', text="Analyze STL Files")
        self.stop_button.config(state='disabled', text="Stop Analysis")
        self.browse_button.config(state='normal')
        self.recursive_checkbox.config(state='normal')
        
        # Show summary
        successful = len([r for r in self.results if r['status'] == 'OK'])
        failed = len(self.results) - successful
        
        summary = f"⏹️ Analysis Stopped: {processed_count} files processed"
        if successful > 0:
            summary += f" ({successful} successful"
            if failed > 0:
                summary += f", {failed} failed"
            summary += ")"
        
        self.progress_label.config(text=summary)
        self.status_var.set(summary)
        
        # Enable export if we have some results
        if self.results:
            self.export_button.config(state='normal')
            self.open_folder_button.config(state='normal')
            # Auto-export partial results
            self.auto_export_results()
        
        # Show info dialog
        if successful > 0:
            messagebox.showinfo("Analysis Stopped", 
                              f"Analysis was stopped by user.\n\n"
                              f"Processed: {processed_count} files\n"
                              f"Successful: {successful} files\n"
                              f"Failed: {failed} files\n\n"
                              f"Partial results have been exported.")
        else:
            messagebox.showinfo("Analysis Stopped", 
                              "Analysis was stopped before any files could be processed.")
    
    def analysis_error(self, error_msg):
        """Handle analysis error"""
        self.processing = False
        self.stop_requested = False
        self.analyze_button.config(state='normal', text="Analyze STL Files")
        self.stop_button.config(state='disabled', text="Stop Analysis")
        self.browse_button.config(state='normal')
        self.recursive_checkbox.config(state='normal')
        
        error_text = f"❌ Analysis failed: {error_msg}"
        self.progress_label.config(text=error_text)
        self.status_var.set(error_text)
        
        messagebox.showerror("Analysis Error", f"An error occurred during analysis:\n\n{error_msg}")
    
    def get_stl_dimensions(self, stl_file_path, base_folder=None):
        """Analyze a single STL file"""
        if not STL_AVAILABLE:
            return {
                'folder': self.get_relative_folder(stl_file_path, base_folder),
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
            stl_mesh = mesh.Mesh.from_file(stl_file_path)
            points = stl_mesh.points.reshape(-1, 3)
            min_coords = np.min(points, axis=0)
            max_coords = np.max(points, axis=0)
            dimensions = max_coords - min_coords
            
            try:
                volume = stl_mesh.get_mass_properties()[0]
            except:
                volume = 0
            
            return {
                'folder': self.get_relative_folder(stl_file_path, base_folder),
                'file': os.path.basename(stl_file_path),
                'width_x': round(dimensions[0], 3),
                'depth_y': round(dimensions[1], 3),
                'height_z': round(dimensions[2], 3),
                'volume': round(volume, 3),
                'triangle_count': len(stl_mesh.vectors),
                'unit': 'mm',
                'status': 'OK'
            }
            
        except Exception as e:
            return {
                'folder': self.get_relative_folder(stl_file_path, base_folder),
                'file': os.path.basename(stl_file_path),
                'width_x': 0,
                'depth_y': 0,
                'height_z': 0,
                'volume': 0,
                'triangle_count': 0,
                'unit': 'mm',
                'status': f'Error: {str(e)}'
            }
    
    def get_relative_folder(self, file_path, base_folder):
        """Get relative folder path for display"""
        if base_folder:
            try:
                parent_folder = os.path.dirname(file_path)
                if parent_folder == base_folder:
                    return "."  # Root folder
                else:
                    return os.path.relpath(parent_folder, base_folder)
            except:
                return os.path.dirname(file_path)
        return os.path.dirname(file_path)
    
    def auto_export_results(self):
        """Automatically export results to CSV"""
        if not self.results:
            return
        
        try:
            folder = self.selected_folder.get()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = os.path.join(folder, f"stl_dimensions_{timestamp}.csv")
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = self.results[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.results)
            
            self.last_export_path = csv_path
            self.status_var.set(f"Results exported to: {os.path.basename(csv_path)}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results:\n\n{e}")
    
    def export_results(self):
        """Manual export with file dialog"""
        if not self.results:
            messagebox.showwarning("No Results", "No analysis results to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Results"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = self.results[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.results)
                
                messagebox.showinfo("Export Complete", f"Results exported successfully to:\n{file_path}")
                self.status_var.set(f"Results exported to: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results:\n\n{e}")
    
    def open_output_folder(self):
        """Open the folder containing the results"""
        folder = self.selected_folder.get()
        if folder and os.path.exists(folder):
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                os.system(f"open '{folder}'")
            else:
                os.system(f"xdg-open '{folder}'")

def main():
    """Main function to start the GUI application"""
    try:
        root = tk.Tk()
        app = STLAnalyzerGUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Application Error", f"An unexpected error occurred:\n\n{e}")

if __name__ == "__main__":
    main()