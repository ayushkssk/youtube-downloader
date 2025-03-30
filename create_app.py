#!/usr/bin/env python3
"""
Create a macOS application bundle for YouTube Downloader with custom icon
"""

import os
import sys
import shutil
import subprocess
import plistlib
from pathlib import Path
import tempfile

def create_macos_app():
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths
    app_name = "YouTube Downloader"
    app_path = os.path.expanduser(f"~/Desktop/{app_name}.app")
    contents_path = os.path.join(app_path, "Contents")
    macos_path = os.path.join(contents_path, "MacOS")
    resources_path = os.path.join(contents_path, "Resources")
    
    # Create directory structure
    os.makedirs(macos_path, exist_ok=True)
    os.makedirs(resources_path, exist_ok=True)
    
    # Create launcher script
    launcher_path = os.path.join(macos_path, "launcher")
    with open(launcher_path, "w") as f:
        f.write(f"""#!/bin/bash
cd "{current_dir}"
source venv/bin/activate
python youtube_downloader_gui.py
""")
    
    # Make launcher executable
    os.chmod(launcher_path, 0o755)
    
    # Create Info.plist
    info_plist = {
        'CFBundleName': app_name,
        'CFBundleDisplayName': app_name,
        'CFBundleIdentifier': 'com.youtubedownloader.app',
        'CFBundleVersion': '1.0',
        'CFBundleExecutable': 'launcher',
        'CFBundleIconFile': 'AppIcon',
        'CFBundlePackageType': 'APPL',
        'NSHighResolutionCapable': True,
    }
    
    with open(os.path.join(contents_path, 'Info.plist'), 'wb') as f:
        plistlib.dump(info_plist, f)
    
    # Convert the JPG to ICNS format for the app icon
    logo_path = os.path.join(current_dir, 'logo.JPG')
    icon_path = os.path.join(resources_path, 'AppIcon.icns')
    
    # Create iconset from the JPG
    with tempfile.TemporaryDirectory() as tmp_dir:
        iconset_path = os.path.join(tmp_dir, 'AppIcon.iconset')
        os.makedirs(iconset_path, exist_ok=True)
        
        # Copy the JPG to the iconset directory with different sizes
        shutil.copy(logo_path, os.path.join(iconset_path, 'icon_512x512.jpg'))
        
        # Use sips to convert JPG to PNG and resize for different icon sizes
        sizes = [16, 32, 64, 128, 256, 512]
        for size in sizes:
            output_path = os.path.join(iconset_path, f'icon_{size}x{size}.png')
            subprocess.run([
                'sips', 
                '-s', 'format', 'png', 
                '-z', str(size), str(size), 
                os.path.join(iconset_path, 'icon_512x512.jpg'), 
                '--out', output_path
            ])
            
            # Create 2x versions
            if size < 512:
                output_path = os.path.join(iconset_path, f'icon_{size}x{size}@2x.png')
                subprocess.run([
                    'sips', 
                    '-s', 'format', 'png', 
                    '-z', str(size*2), str(size*2), 
                    os.path.join(iconset_path, 'icon_512x512.jpg'), 
                    '--out', output_path
                ])
        
        # Convert iconset to icns
        subprocess.run(['iconutil', '-c', 'icns', iconset_path, '-o', icon_path])
    
    print(f"Created macOS application at: {app_path}")
    print("You can now launch the YouTube Downloader by double-clicking the icon on your Desktop.")

if __name__ == "__main__":
    create_macos_app()
