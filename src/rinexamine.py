# -*- coding: utf-8 -*-

__version__ = "1.0.0"
__author__ = "Daniel Adi Nugroho"
__email__ = "dnugroho@gmail.com"
__status__ = "Production"
__date__ = "2025-10-16"
__copyright__ = "Copyright (c) 2025 Daniel Adi Nugroho"
__license__ = "GNU General Public License v3.0 (GPL-3.0)"

# Version History
# --------------

# 1.0.0 (2025-02-08)
# - Initial release

"""
RINEX File Examiner - GUI Application
This tool reads RINEX observation files and extracts key metadata from the header.
RINEX (Receiver Independent Exchange Format) is a standard format for GNSS data.

Supports compressed files:
- Hatanaka compression (.crx, .##d) - requires 'hatanaka' library
- Gzip (.gz) - built-in support
- Unix compress (.Z) - requires 'hatanaka' library
- Other formats (.bz2, .zip) - requires 'hatanaka' library

"""

import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from datetime import datetime
import os
import re
import gzip
import tempfile

# Try to import hatanaka library for CRX file support
try:
    from hatanaka import decompress
    HATANAKA_AVAILABLE = True
except ImportError:
    HATANAKA_AVAILABLE = False

class RINEXExaminer:
    """
    Main class that handles the GUI and RINEX file parsing.
    This creates the window, buttons, and all the logic for reading RINEX files.
    """
    
    def __init__(self, root):
        """
        Initialize the GUI window and all its components.
        root: The main tkinter window object
        """
        self.root = root
        self.root.title("RINEX File Examiner")
        self.root.geometry("900x700")  # Width x Height in pixels
        
        # Create the GUI components
        self.create_widgets()
        
    def create_widgets(self):
        """
        Create all the buttons, labels, and text areas for the GUI.
        This is called once when the program starts.
        """
        
        # Title label at the top
        title_label = tk.Label(
            self.root, 
            text="RINEX File Examiner", 
            font=("Arial", 16, "bold"),
            pady=10
        )
        title_label.pack()
        
        # Frame to hold the file selection button (frame = container for widgets)
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=10)
        
        # Button to open file dialog and select RINEX file
        self.select_button = tk.Button(
            file_frame,
            text="Select RINEX File",
            command=self.select_file,  # When clicked, run select_file method
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10
        )
        self.select_button.pack()
        
        # Label to show which file is currently loaded
        self.file_label = tk.Label(
            self.root,
            text="No file selected",
            font=("Arial", 10),
            fg="gray"
        )
        self.file_label.pack()
        
        # Frame for the results display area
        results_frame = tk.Frame(self.root)
        results_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Label above the results area
        results_title = tk.Label(
            results_frame,
            text="File Information:",
            font=("Arial", 12, "bold")
        )
        results_title.pack(anchor='w')
        
        # Scrolled text widget - this is where we display the RINEX info
        # ScrolledText gives us a text box with automatic scrollbars
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,  # Wrap text at word boundaries
            width=100,
            height=30,
            font=("Courier", 10),  # Monospace font for better alignment
            bg="#f5f5f5"
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
    def select_file(self):
        """
        Open a file dialog to let user select a RINEX file.
        Then process the file and display results.
        """
        
        # Open file dialog - allows various RINEX extensions including compressed
        filename = filedialog.askopenfilename(
            title="Select RINEX File",
            filetypes=[
                ("RINEX Files", "*.rnx *.obs *.nav *.*o *.*n *.*O *.*N"),
                ("Compressed RINEX", "*.crx *.gz *.Z *.*d *.*D *.bz2 *.zip"),
                ("All Files", "*.*")
            ]
        )
        
        # If user selected a file (didn't cancel)
        if filename:
            self.file_label.config(text=f"File: {os.path.basename(filename)}")
            self.process_rinex_file(filename)
    
    def detect_file_type(self, filepath):
        """
        Detect if file is compressed and what type.
        Returns: (is_compressed, compression_type, needs_hatanaka)
        """
        filename = filepath.lower()
        
        # Check for Hatanaka compression (.crx or .##d format)
        if filename.endswith('.crx') or re.search(r'\.\d{2}d$', filename):
            return (True, 'hatanaka', True)
        
        # Check for gzip (can handle without hatanaka)
        if filename.endswith('.gz'):
            # Could be .crx.gz (needs hatanaka) or .rnx.gz (just gzip)
            if '.crx.gz' in filename or re.search(r'\.\d{2}d\.gz$', filename):
                return (True, 'hatanaka+gz', True)
            return (True, 'gzip', False)
        
        # Check for other compressions that need hatanaka
        if filename.endswith('.z'):
            return (True, 'compress', True)
        if filename.endswith('.bz2'):
            return (True, 'bzip2', True)
        if filename.endswith('.zip'):
            return (True, 'zip', True)
        
        return (False, 'none', False)
    
    def decompress_file(self, filepath):
        """
        Decompress a compressed RINEX file and return the lines.
        Handles various compression formats using hatanaka library or built-in gzip.
        
        Returns: List of lines from decompressed file, or None if error
        """
        is_compressed, comp_type, needs_hatanaka = self.detect_file_type(filepath)
        
        if not is_compressed:
            # Not compressed, read normally
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.readlines()
        
        # File is compressed
        if needs_hatanaka:
            if not HATANAKA_AVAILABLE:
                messagebox.showerror(
                    "Missing Library",
                    f"This file uses {comp_type} compression.\n\n"
                    "To open compressed RINEX files, you need to install the 'hatanaka' library:\n\n"
                    "pip install hatanaka\n\n"
                    "After installation, restart this application."
                )
                return None
            
            # Use hatanaka library to decompress
            try:
                # Decompress to string
                decompressed_data = decompress(filepath)
                # Split into lines
                return decompressed_data.decode('utf-8', errors='ignore').split('\n')
            except Exception as e:
                messagebox.showerror("Decompression Error", f"Failed to decompress file:\n{str(e)}")
                return None
        
        else:
            # Just gzip, can handle with built-in library
            try:
                with gzip.open(filepath, 'rt', encoding='utf-8', errors='ignore') as f:
                    return f.readlines()
            except Exception as e:
                messagebox.showerror("Decompression Error", f"Failed to decompress gzip file:\n{str(e)}")
                return None
    
    def process_rinex_file(self, filepath):
        """
        Read and parse the RINEX file to extract all requested information.
        Handles both compressed and uncompressed files.
        filepath: Full path to the RINEX file
        """
        
        try:
            # Decompress file if needed and get lines
            lines = self.decompress_file(filepath)
            
            if lines is None:
                # Error already shown in decompress_file
                return
            
            # Parse the header and observation data
            header_data = self.parse_rinex_header(lines)
            obs_data = self.parse_observation_data(lines, header_data)
            
            # Combine header and observation data
            all_data = {**header_data, **obs_data}
            
            # Display the extracted information
            self.display_results(all_data, filepath)
            
        except Exception as e:
            # If something goes wrong, show error message
            messagebox.showerror("Error", f"Error reading file:\n{str(e)}")
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Error: {str(e)}")
    
    def parse_rinex_header(self, lines):
        """
        Parse the RINEX header section to extract metadata.
        RINEX files have a header section at the top with labels ending in specific keywords.
        
        lines: List of all lines from the RINEX file
        Returns: Dictionary with extracted header information
        """
        
        data = {
            'version': 'Unknown',
            'file_type': 'Unknown',
            'satellite_system': 'Unknown',
            'observation_types': {},
            'antenna_type': 'Unknown',
            'antenna_height': 'Unknown',
            'antenna_delta': 'Unknown',
            'approx_position': 'Unknown',
            'lat_lon_elev': 'Not calculated',
            'interval': 'Unknown',
            'time_first_obs': 'Unknown',
            'time_last_obs': 'Unknown',
            'leap_seconds': 'Unknown',
            'constellations_obs': set(),
            'constellations_nav': set(),
            # Survey-critical additions
            'marker_name': 'Unknown',
            'marker_number': 'Unknown',
            'marker_type': 'Unknown',
            'observer': 'Unknown',
            'agency': 'Unknown',
            'receiver_number': 'Unknown',
            'receiver_type': 'Unknown',
            'receiver_version': 'Unknown',
            'antenna_number': 'Unknown',
        }
        
        # Iterate through lines until we reach "END OF HEADER"
        for line in lines:
            # RINEX headers are 60 chars of data + 20 chars of label = 80 chars total
            if len(line) < 60:
                continue
                
            # Extract the label (last 20 characters, typically)
            label = line[60:].strip()
            content = line[:60].strip()
            
            # Check for end of header
            if "END OF HEADER" in label:
                break
            
            # Parse different header fields based on their label
            
            # 1. RINEX VERSION - tells us format version
            if "RINEX VERSION" in label:
                parts = content.split()
                if len(parts) >= 2:
                    data['version'] = parts[0]
                    data['file_type'] = parts[1]
                    # For RINEX 3+, satellite system is in the version line
                    if len(parts) >= 3:
                        data['satellite_system'] = parts[2]
            
            # MARKER NAME - Station/point identifier (CRITICAL for surveys)
            elif "MARKER NAME" in label:
                data['marker_name'] = content
            
            # MARKER NUMBER - Official survey marker number
            elif "MARKER NUMBER" in label:
                data['marker_number'] = content
            
            # MARKER TYPE - Type of monument/marker
            elif "MARKER TYPE" in label:
                data['marker_type'] = content
            
            # OBSERVER / AGENCY - Who collected the data
            elif "OBSERVER / AGENCY" in label:
                # Format is usually: OBSERVER          AGENCY
                parts = content.split()
                if len(parts) >= 1:
                    data['observer'] = parts[0]
                if len(parts) >= 2:
                    data['agency'] = ' '.join(parts[1:])  # Agency may be multiple words
            
            # RECEIVER INFO - Type, serial number, firmware version
            elif "REC # / TYPE / VERS" in label:
                # Format: SERIAL# TYPE VERSION
                parts = content.split()
                if len(parts) >= 1:
                    data['receiver_number'] = parts[0]
                if len(parts) >= 2:
                    data['receiver_type'] = parts[1]
                if len(parts) >= 3:
                    data['receiver_version'] = parts[2]
            
            # 2. ANTENNA TYPE - make and model
            elif "ANT # / TYPE" in label or "ANTENNA TYPE" in label:
                # Format: SERIAL# TYPE or just TYPE
                parts = content.split()
                if len(parts) >= 1:
                    # Check if first part is a serial number or antenna type
                    if len(parts) >= 2 and not parts[0].isalpha():
                        data['antenna_number'] = parts[0]
                        data['antenna_type'] = ' '.join(parts[1:])
                    else:
                        data['antenna_type'] = content
            
            # 3. ANTENNA HEIGHT - height above ground
            elif "ANTENNA: DELTA H/E/N" in label or "ANTENNA DELTA" in label:
                parts = content.split()
                if len(parts) >= 1:
                    data['antenna_height'] = parts[0]  # First value is height
                if len(parts) >= 3:
                    data['antenna_delta'] = f"H:{parts[0]} E:{parts[1]} N:{parts[2]}"
            
            # 4. APPROXIMATE POSITION - XYZ coordinates in meters
            elif "APPROX POSITION XYZ" in label:
                data['approx_position'] = content
                # Try to convert XYZ to Lat/Lon/Elev
                try:
                    coords = [float(x) for x in content.split()]
                    if len(coords) == 3:
                        lat, lon, elev = self.xyz_to_latlon(coords[0], coords[1], coords[2])
                        data['lat_lon_elev'] = f"Lat: {lat:.8f}°, Lon: {lon:.8f}°, Elev: {elev:.3f}m"
                except:
                    pass
            
            # 5. OBSERVATION INTERVAL - epoch rate in seconds
            elif "INTERVAL" in label:
                data['interval'] = content
            
            # 6. TIME OF FIRST OBS - start time of observations
            elif "TIME OF FIRST OBS" in label:
                data['time_first_obs'] = content
            
            # 7. TIME OF LAST OBS - end time of observations
            elif "TIME OF LAST OBS" in label:
                data['time_last_obs'] = content
            
            # 8. LEAP SECONDS - GPS/UTC time offset
            elif "LEAP SECONDS" in label:
                data['leap_seconds'] = content
            
            # 9. SYS / # / OBS TYPES - observation types per satellite system (RINEX 3+)
            elif "SYS / # / OBS TYPES" in label:
                parts = content.split()
                if len(parts) >= 2:
                    # Check if this is a continuation line (starts with spaces, no system code)
                    # Continuation lines don't have a letter in the first position
                    if parts[0][0].isalpha() and len(parts[0]) == 1:
                        # This is a new system line
                        sys = parts[0]  # Satellite system (G=GPS, R=GLONASS, E=Galileo, etc.)
                        try:
                            num_obs = int(parts[1])
                            obs_types = parts[2:]
                            data['observation_types'][sys] = obs_types
                            data['constellations_obs'].add(sys)
                            # Store the last system for continuation lines
                            data['_last_obs_system'] = sys
                        except ValueError:
                            # Not a valid number, skip this line
                            pass
                    elif '_last_obs_system' in data:
                        # This is a continuation line - append to the last system
                        sys = data['_last_obs_system']
                        if sys in data['observation_types']:
                            data['observation_types'][sys].extend(parts)
            
            # 10. # / TYPES OF OBSERV - observation types (RINEX 2.x)
            elif "TYPES OF OBSERV" in label:
                parts = content.split()
                if len(parts) >= 1:
                    try:
                        num_obs = int(parts[0])
                        obs_types = parts[1:1+num_obs]
                        # In RINEX 2, observations apply to all systems
                        data['observation_types']['ALL'] = obs_types
                    except ValueError:
                        # Not a valid number, skip this line
                        pass
        
        # Clean up temporary variables used during parsing
        if '_last_obs_system' in data:
            del data['_last_obs_system']
        
        return data
    
    def parse_observation_data(self, lines, header_data):
        """
        Parse the observation data section to find satellite constellations,
        and calculate actual start/end times and duration.
        
        lines: All lines from the RINEX file
        header_data: Dictionary with header information (to know when header ends)
        Returns: Dictionary with observation statistics
        """
        
        data = {
            'constellations_in_data': set(),
            'actual_start': None,
            'actual_end': None,
            'duration_seconds': 0,
            'num_epochs': 0,
            'calculated_interval': None,
            'epoch_times': [],  # Store epoch times for interval calculation
            'satellites_per_epoch': [],  # Store satellite counts for quality metrics
        }
        
        # Find where header ends
        header_end = 0
        for i, line in enumerate(lines):
            if "END OF HEADER" in line:
                header_end = i + 1
                break
        
        # Process observation records
        in_epoch = False
        first_epoch_time = None
        last_epoch_time = None
        epoch_count = 0
        
        for line in lines[header_end:]:
            # In RINEX 3.x, epoch lines start with '>'
            # In RINEX 2.x, epoch lines have year/month/day in first few columns
            
            # RINEX 3.x epoch detection
            if line.startswith('>'):
                in_epoch = True
                epoch_count += 1
                
                # Parse the timestamp: > YYYY MM DD HH MM SS.SSSSSSS
                try:
                    parts = line.split()
                    if len(parts) >= 7:
                        year = int(parts[1])
                        month = int(parts[2])
                        day = int(parts[3])
                        hour = int(parts[4])
                        minute = int(parts[5])
                        second = float(parts[6])
                        
                        epoch_time = datetime(year, month, day, hour, minute, int(second))
                        
                        # Store epoch times for interval calculation (limit to first 100 to save memory)
                        if len(data['epoch_times']) < 100:
                            data['epoch_times'].append(epoch_time)
                        
                        if first_epoch_time is None:
                            first_epoch_time = epoch_time
                        last_epoch_time = epoch_time
                except:
                    pass
                    
            # RINEX 2.x epoch detection (starts with space and year in columns 1-3)
            elif len(line) > 29 and line[0] == ' ' and line[1:3].strip().isdigit():
                try:
                    # RINEX 2.x format: YY MM DD HH MM SS.SSSSSSS
                    year = int(line[1:3])
                    # Convert 2-digit year to 4-digit (80-99 = 1980-1999, 00-79 = 2000-2079)
                    year = year + 1900 if year >= 80 else year + 2000
                    month = int(line[4:6])
                    day = int(line[7:9])
                    hour = int(line[10:12])
                    minute = int(line[13:15])
                    second = float(line[16:26])
                    
                    epoch_time = datetime(year, month, day, hour, minute, int(second))
                    epoch_count += 1
                    
                    # Store epoch times for interval calculation (limit to first 100 to save memory)
                    if len(data['epoch_times']) < 100:
                        data['epoch_times'].append(epoch_time)
                    
                    if first_epoch_time is None:
                        first_epoch_time = epoch_time
                    last_epoch_time = epoch_time
                    in_epoch = True
                except:
                    pass
            
            # Extract satellite system from observation lines
            # In RINEX 3.x, satellite ID is at start of line after epoch (e.g., G01, R12, E24)
            # In RINEX 2.x, satellite numbers are in the epoch line
            elif in_epoch and len(line) > 3:
                # Try RINEX 3.x format (system letter + number)
                sat_id = line[0:3].strip()
                if len(sat_id) >= 2 and sat_id[0].isalpha():
                    system = sat_id[0]
                    data['constellations_in_data'].add(system)
        
        # Calculate duration and format times
        if first_epoch_time and last_epoch_time:
            data['actual_start'] = first_epoch_time.strftime("%Y-%m-%d %H:%M:%S")
            data['actual_end'] = last_epoch_time.strftime("%Y-%m-%d %H:%M:%S")
            duration = (last_epoch_time - first_epoch_time).total_seconds()
            data['duration_seconds'] = duration
            data['num_epochs'] = epoch_count
        
        # Calculate actual observation interval from consecutive epochs
        if len(data['epoch_times']) >= 2:
            # Calculate intervals between all consecutive epochs
            intervals = []
            for i in range(len(data['epoch_times']) - 1):
                interval = (data['epoch_times'][i + 1] - data['epoch_times'][i]).total_seconds()
                # Only include positive, reasonable intervals (0.001s to 3600s)
                # This filters out potential parsing errors or time resets
                if 0.001 <= interval <= 3600:
                    intervals.append(interval)
            
            if intervals:
                # Calculate statistics
                min_interval = min(intervals)
                max_interval = max(intervals)
                avg_interval = sum(intervals) / len(intervals)
                
                # Check if intervals are consistent (within 1% tolerance)
                if max_interval - min_interval < 0.01 * avg_interval:
                    # Consistent interval - report as single value
                    data['calculated_interval'] = f"{avg_interval:.3f}"
                    data['interval_consistent'] = True
                else:
                    # Variable interval - report range and average
                    data['calculated_interval'] = f"{avg_interval:.3f} (range: {min_interval:.3f}-{max_interval:.3f})"
                    data['interval_consistent'] = False
        
        return data
    
    def xyz_to_latlon(self, x, y, z):
        """
        Convert ECEF (Earth-Centered Earth-Fixed) XYZ coordinates to Lat/Lon/Elevation.
        Uses WGS84 ellipsoid parameters.
        
        x, y, z: Coordinates in meters
        Returns: (latitude, longitude, elevation) in degrees and meters
        """
        
        # WGS84 ellipsoid parameters
        a = 6378137.0  # Semi-major axis in meters
        f = 1/298.257223563  # Flattening
        e2 = 2*f - f*f  # Square of eccentricity
        
        # Calculate longitude (easy part)
        lon = math.atan2(y, x) * 180.0 / math.pi
        
        # Calculate latitude and elevation (iterative process)
        p = math.sqrt(x*x + y*y)
        lat = math.atan2(z, p * (1 - e2))
        
        # Iterate to refine latitude
        for _ in range(5):
            sin_lat = math.sin(lat)
            N = a / math.sqrt(1 - e2 * sin_lat * sin_lat)
            lat = math.atan2(z + e2 * N * sin_lat, p)
        
        # Calculate elevation
        sin_lat = math.sin(lat)
        N = a / math.sqrt(1 - e2 * sin_lat * sin_lat)
        elev = p / math.cos(lat) - N
        
        # Convert latitude to degrees
        lat = lat * 180.0 / math.pi
        
        return lat, lon, elev
    
    def display_results(self, data, filepath):
        """
        Display all extracted information in the text widget.
        Formats the data nicely for easy reading.
        
        data: Dictionary containing all extracted RINEX information
        filepath: Path to the original file (to show compression info)
        """
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        # Build output string with formatted information
        output = "=" * 80 + "\n"
        output += "RINEX FILE INFORMATION\n"
        output += "=" * 80 + "\n\n"
        
        # Show file info
        output += f"File: {os.path.basename(filepath)}\n"
        is_compressed, comp_type, needs_hatanaka = self.detect_file_type(filepath)
        if is_compressed:
            output += f"Compression: {comp_type}\n"
        output += "\n"
        
        # SURVEY METADATA - Critical for surveyors/geospatial analysts
        output += "=" * 80 + "\n"
        output += "SURVEY METADATA\n"
        output += "=" * 80 + "\n"
        if data['marker_name'] != 'Unknown':
            output += f"Marker Name:    {data['marker_name']}\n"
        if data['marker_number'] != 'Unknown':
            output += f"Marker Number:  {data['marker_number']}\n"
        if data['marker_type'] != 'Unknown':
            output += f"Marker Type:    {data['marker_type']}\n"
        if data['observer'] != 'Unknown':
            output += f"Observer:       {data['observer']}\n"
        if data['agency'] != 'Unknown':
            output += f"Agency:         {data['agency']}\n"
        if data['receiver_type'] != 'Unknown':
            output += f"Receiver:       {data['receiver_type']}"
            if data['receiver_version'] != 'Unknown':
                output += f" (v{data['receiver_version']})"
            if data['receiver_number'] != 'Unknown':
                output += f" S/N: {data['receiver_number']}"
            output += "\n"
        if data['antenna_number'] != 'Unknown':
            output += f"Antenna S/N:    {data['antenna_number']}\n"
        
        # Only show section if at least one field was populated
        if (data['marker_name'] == 'Unknown' and data['marker_number'] == 'Unknown' and 
            data['observer'] == 'Unknown' and data['receiver_type'] == 'Unknown'):
            output += "⚠ No survey metadata found in header\n"
        
        output += "\n"
        
        # 1. RINEX Version
        output += f"1. RINEX VERSION:\n"
        output += f"   {data['version']} ({data['file_type']})\n\n"
        
        # 2. Satellite Constellations
        output += f"2. SATELLITE CONSTELLATIONS:\n"
        
        # Observation constellations (from header)
        if data['constellations_obs']:
            const_names = self.get_constellation_names(data['constellations_obs'])
            output += f"   Observation types defined for: {', '.join(const_names)}\n"
        
        # Constellations in actual data
        if data['constellations_in_data']:
            const_names = self.get_constellation_names(data['constellations_in_data'])
            output += f"   Satellites observed in data: {', '.join(const_names)}\n"
        
        # Ephemerides (if NAV file, would be listed separately - this is obs file)
        output += f"   Note: This appears to be an observation file.\n"
        output += f"         Ephemeris data would be in a separate navigation file.\n\n"
        
        # 3. Epoch / Observation Rate
        output += f"3. OBSERVATION INTERVAL (EPOCH RATE):\n"
        
        # Show header value
        header_interval = data['interval']
        output += f"   Header value:     {header_interval} seconds\n"
        
        # Show calculated value if available
        if data.get('calculated_interval'):
            output += f"   Calculated value: {data['calculated_interval']} seconds\n"
            
            # Check for discrepancies between header and calculated
            if header_interval != 'Unknown':
                try:
                    header_float = float(header_interval)
                    calc_float = float(data['calculated_interval'].split()[0])  # Get just the number
                    
                    # Allow 1% tolerance for rounding differences
                    if abs(header_float - calc_float) > 0.01 * header_float:
                        output += f"   ⚠ WARNING: Header and calculated intervals don't match!\n"
                except:
                    pass
            
            # Flag variable intervals
            if not data.get('interval_consistent', True):
                output += f"   ⚠ NOTE: Observation interval is NOT consistent (varies between epochs)\n"
        elif header_interval == 'Unknown':
            output += f"   ⚠ No interval found in header and could not calculate from data\n"
        
        output += "\n"
        
        # 4. Observation Duration
        output += f"4. OBSERVATION DURATION:\n"
        if data['actual_start']:
            output += f"   Start Time:  {data['actual_start']}\n"
            output += f"   End Time:    {data['actual_end']}\n"
            output += f"   Duration:    {data['duration_seconds']:.1f} seconds "
            output += f"({data['duration_seconds']/3600:.2f} hours)\n"
            output += f"   Epochs:      {data['num_epochs']}\n"
        else:
            output += f"   From header: {data['time_first_obs']}\n"
            output += f"   To:          {data['time_last_obs']}\n"
            output += f"   (Could not parse observation data for exact duration)\n"
        output += "\n"
        
        # 5. Antenna Make/Model
        output += f"5. ANTENNA MAKE/MODEL:\n"
        output += f"   {data['antenna_type']}\n\n"
        
        # 6. Antenna Height
        output += f"6. ANTENNA HEIGHT:\n"
        output += f"   {data['antenna_height']} meters\n"
        if data['antenna_delta'] != 'Unknown':
            output += f"   (Full delta H/E/N: {data['antenna_delta']})\n"
        output += "\n"
        
        # 7. Antenna Position (Lat/Lon/Elev)
        output += f"7. ANTENNA POSITION:\n"
        output += f"   Approximate XYZ: {data['approx_position']}\n"
        output += f"   Converted:       {data['lat_lon_elev']}\n\n"
        
        # Additional useful information
        output += "=" * 80 + "\n"
        output += "DATA QUALITY INDICATORS\n"
        output += "=" * 80 + "\n\n"
        
        # Total epochs and satellites
        if data['num_epochs'] > 0:
            output += f"Total Epochs:      {data['num_epochs']}\n"
            
        # Unique satellites observed
        if data['constellations_in_data']:
            const_list = list(data['constellations_in_data'])
            output += f"GNSS Systems:      {len(const_list)} system(s) - {', '.join(self.get_constellation_names(const_list))}\n"
        
        output += "\n"
        
        # Additional useful information
        output += "=" * 80 + "\n"
        output += "ADDITIONAL INFORMATION\n"
        output += "=" * 80 + "\n\n"
        
        # Observation types
        if data['observation_types']:
            output += "Observation Types:\n"
            for sys, obs_types in data['observation_types'].items():
                sys_name = self.get_system_name(sys)
                output += f"   {sys_name}: {', '.join(obs_types)}\n"
            output += "\n"
        
        output += f"Satellite System: {data['satellite_system']}\n"
        output += f"Leap Seconds: {data['leap_seconds']}\n\n"
        
        # Show compression library status
        output += "=" * 80 + "\n"
        output += "COMPRESSION SUPPORT STATUS\n"
        output += "=" * 80 + "\n"
        if HATANAKA_AVAILABLE:
            output += "✓ Hatanaka library installed - CRX files supported\n"
            output += "  Supported: .crx, .##d, .gz, .Z, .bz2, .zip\n"
        else:
            output += "✗ Hatanaka library NOT installed\n"
            output += "  Limited support: only .gz files (gzip) are supported\n"
            output += "  To enable CRX support, install: pip install hatanaka\n"
        
        # Insert the formatted text into the widget
        self.results_text.insert(tk.END, output)
    
    def get_constellation_names(self, system_codes):
        """
        Convert single-letter system codes to full constellation names.
        G = GPS, R = GLONASS, E = Galileo, C = BeiDou, J = QZSS, I = IRNSS, S = SBAS
        """
        mapping = {
            'G': 'GPS',
            'R': 'GLONASS',
            'E': 'Galileo',
            'C': 'BeiDou',
            'J': 'QZSS',
            'I': 'IRNSS/NavIC',
            'S': 'SBAS',
            'ALL': 'All Systems'
        }
        return [mapping.get(code, code) for code in sorted(system_codes)]
    
    def get_system_name(self, code):
        """
        Get full name for a satellite system code.
        """
        mapping = {
            'G': 'GPS',
            'R': 'GLONASS',
            'E': 'Galileo',
            'C': 'BeiDou',
            'J': 'QZSS',
            'I': 'IRNSS/NavIC',
            'S': 'SBAS',
            'ALL': 'All Systems',
            'M': 'Mixed'
        }
        return mapping.get(code, code)


# Import math module for coordinate conversion
import math


def main():
    """
    Main function - creates the GUI window and starts the application.
    This is the entry point of the program.
    """
    root = tk.Tk()
    app = RINEXExaminer(root)
    root.mainloop()  # Start the GUI event loop (keeps window open)


# This runs only when the script is executed directly (not imported)
if __name__ == "__main__":
    main()
