RINEX FILE EXAMINER
===================

Quick RINEX observation file metadata extractor with GUI.

Reads RINEX v2.x and v3.x files and shows you what's inside without needing full processing software.


WHAT IT EXTRACTS
----------------

Survey metadata (marker, observer, agency)
Equipment info (receiver, antenna models and serial numbers)
Station coordinates (XYZ and Lat/Lon/Elev)
Observation timing (start, end, duration, epoch rate)
GNSS constellations used (GPS, GLONASS, Galileo, BeiDou, etc.)
Data quality checks (interval consistency, epoch counts)


INSTALLATION
------------

Requirements:
- Python 3.6+
- tkinter (usually included)
- psutil

Install:
    pip install psutil

For compressed RINEX support (highly recommended):
    pip install hatanaka

Without hatanaka, you can only read .gz files. Most real-world GNSS data uses Hatanaka compression (.crx, .##d), so you'll be limited without it.


USAGE
-----

Run:
    python rinexamine.py

Click "Select RINEX File", choose your file, read the results.

Supported formats:
- RINEX 2.x/3.x (.rnx, .obs, .*o, .*O)
- Gzip (.gz) - works without hatanaka
- Hatanaka (.crx, .##d) - needs hatanaka library
- Unix compress (.Z) - needs hatanaka library
- Other (.bz2, .zip) - needs hatanaka library


WHAT THIS IS NOT
----------------

This is NOT a RINEX processor. It does NOT:
- Compute positions or baselines
- Do post-processing or PPP
- Analyze data quality (multipath, cycle slips, SNR)
- Edit or fix RINEX files

For actual GNSS processing, use RTKLIB, Bernese, CSRS-PPP, or similar.

This tool is for quickly checking "what's in this file?" before you process it.


TROUBLESHOOTING
---------------

Error: "This file uses hatanaka compression"
Fix: pip install hatanaka

Application won't start (Linux/Mac):
Fix: sudo apt-get install python3-tk (Ubuntu/Debian)
     brew install python-tk (macOS)

"Header and calculated intervals don't match":
This is normal. Trust the calculated value.


TECHNICAL NOTES
---------------

Coordinate conversion uses WGS84 ellipsoid (approximate positioning only)
Interval calculation checks first 100 epochs and warns about inconsistencies
Handles both RINEX 2.x and 3.x epoch formats
Read-only - no file modification


LICENSE
-------

Copyright (c) 2025 Daniel Adi Nugroho
GNU General Public License v3.0 (GPL-3.0)
See https://www.gnu.org/licenses/gpl-3.0.html


AUTHOR
------

Daniel Adi Nugroho
dnugroho@gmail.com


VERSION
-------

1.0.0 (2025-10-16)