#!/usr/bin/env python3
"""
Video Downloader - SuperFast Edition (GUI Version)
A graphical interface to download videos from various platforms in HD quality with maximum speed.
"""

import os
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Dict, Any, List
import yt_dlp
import subprocess
from pathlib import Path


class VideoDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video SuperFast Downloader")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Set style
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12))
        self.style.configure("TLabel", font=("Arial", 12))
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL Entry and Download Section
        url_section = ttk.Frame(self.main_frame)
        url_section.pack(fill=tk.X, pady=(0, 15))
        
        # URL Entry with buttons in same frame
        ttk.Label(url_section, text="Enter Video URL:", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        self.url_frame = ttk.Frame(url_section)
        self.url_frame.pack(fill=tk.X)
        
        self.url_entry = ttk.Entry(self.url_frame, font=("Arial", 12))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Download Button next to URL
        self.download_button = ttk.Button(
            self.url_frame, 
            text="⬇️ Download Best Quality", 
            command=self.start_download,
            style="TButton",
            width=25
        )
        self.download_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Paste button
        self.paste_button = ttk.Button(self.url_frame, text="📋 Paste", command=self.paste_url)
        self.paste_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Supported platforms info
        supported_text = "Supported: YouTube, Facebook, Instagram, Twitter, TikTok, Vimeo, and more"
        ttk.Label(url_section, text=supported_text, font=("Arial", 10, "italic")).pack(anchor=tk.W, pady=(5, 0))
        
        # Video Info Frame
        self.info_frame = ttk.LabelFrame(self.main_frame, text="Video Information", padding=10)
        self.info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Video Title
        self.title_var = tk.StringVar(value="Paste a video URL to see details")
        ttk.Label(self.info_frame, text="Title:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(self.info_frame, textvariable=self.title_var, wraplength=600).grid(row=0, column=1, sticky=tk.W)
        
        # File Size
        self.size_var = tk.StringVar(value="")
        ttk.Label(self.info_frame, text="Size:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(self.info_frame, textvariable=self.size_var).grid(row=1, column=1, sticky=tk.W)
        
        # Format Info
        self.format_var = tk.StringVar(value="")
        ttk.Label(self.info_frame, text="Quality:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(self.info_frame, textvariable=self.format_var).grid(row=2, column=1, sticky=tk.W)
        
        # Platform Info
        self.platform_var = tk.StringVar(value="")
        ttk.Label(self.info_frame, text="Platform:", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(self.info_frame, textvariable=self.platform_var).grid(row=3, column=1, sticky=tk.W)
        
        # Save Location
        self.output_frame = ttk.Frame(self.info_frame)
        self.output_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(10, 0))
        
        ttk.Label(self.output_frame, text="Save to:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        self.output_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        ttk.Entry(self.output_frame, textvariable=self.output_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(self.output_frame, text="Browse", command=self.browse_output).pack(side=tk.RIGHT)
        
        # Progress Frame
        self.progress_frame = ttk.LabelFrame(self.main_frame, text="Download Progress", padding=10)
        self.progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Progress Bar
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, 
            orient=tk.HORIZONTAL, 
            length=100, 
            mode='determinate', 
            variable=self.progress_var
        )
        self.progress_bar.pack(fill=tk.X, pady=(10, 5))
        
        # Status Label
        self.status_var = tk.StringVar(value="Ready to download")
        self.status_label = ttk.Label(
            self.progress_frame, 
            textvariable=self.status_var, 
            font=("Arial", 11)
        )
        self.status_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Log Text
        self.log_text = tk.Text(self.progress_frame, height=8, font=("Courier", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for Log
        self.scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=self.scrollbar.set)
        
        # Control Buttons Frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Play Button (initially disabled)
        self.play_button = ttk.Button(
            self.button_frame,
            text="▶️ Play Video",
            command=self.play_video,
            state=tk.DISABLED,
            width=15
        )
        self.play_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Cancel Button
        self.cancel_button = ttk.Button(
            self.button_frame, 
            text="⏹️ Cancel", 
            command=self.cancel_download,
            style="TButton",
            state=tk.DISABLED,
            width=15
        )
        self.cancel_button.pack(side=tk.RIGHT)
        
        # Initialize variables
        self.download_thread = None
        self.is_downloading = False
        self.ydl = None
        self.last_downloaded_file = None
        self.video_info = None
        
        # Bind URL entry to auto-fetch info
        self.url_entry.bind('<KeyRelease>', self.on_url_change)

    def on_url_change(self, event=None):
        """Called when URL entry content changes"""
        url = self.url_entry.get().strip()
        if url and (any(domain in url.lower() for domain in [
            "youtube.com", "youtu.be", "facebook.com", "fb.watch", "instagram.com",
            "twitter.com", "tiktok.com", "vimeo.com", "dailymotion.com"
        ])):
            self.get_video_info(url)

    def paste_url(self):
        """Paste URL from clipboard and fetch video info"""
        try:
            clipboard_text = self.root.clipboard_get()
            if any(domain in clipboard_text.lower() for domain in [
                "youtube.com", "youtu.be", "facebook.com", "fb.watch", "instagram.com",
                "twitter.com", "tiktok.com", "vimeo.com", "dailymotion.com"
            ]):
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, clipboard_text)
                # Fetch video info immediately
                self.get_video_info(clipboard_text)
            else:
                messagebox.showwarning("Invalid URL", "Please paste a supported video URL")
        except Exception:
            messagebox.showwarning("Error", "Could not access clipboard")

    def browse_output(self):
        """Open file dialog to select output directory"""
        output_dir = filedialog.askdirectory(initialdir=self.output_var.get())
        if output_dir:
            self.output_var.set(output_dir)

    def log_message(self, message):
        """Add message to log text widget"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def update_progress(self, progress):
        """Update progress bar"""
        self.progress_var.set(progress)

    def update_status(self, status):
        """Update status label"""
        self.status_var.set(status)

    def download_progress_hook(self, d):
        """Progress hook for yt-dlp"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes'] > 0:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.root.after(10, lambda: self.update_progress(percent))
                
                # Calculate speed and ETA
                speed = d.get('speed', 0)
                if speed:
                    speed_mb = speed / (1024 * 1024)
                    eta = d.get('eta', 0)
                    status = f"Downloading: {percent:.1f}% - {speed_mb:.2f} MB/s - ETA: {eta} seconds"
                    self.root.after(10, lambda s=status: self.update_status(s))
        
        elif d['status'] == 'finished':
            self.root.after(10, lambda: self.update_status("Download finished, now processing..."))
            self.root.after(10, lambda: self.log_message("Download finished, now processing..."))

    def get_video_info(self, url):
        """Get video information before download"""
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
                "format": "best",  # Request best format to get all format info
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.video_info = ydl.extract_info(url, download=False)
                
                # Update video information
                self.title_var.set(self.video_info.get('title', 'Unknown Title'))
                
                # Set platform info
                platform = self.video_info.get('extractor', 'Unknown Platform').title()
                self.platform_var.set(f"📺 {platform}")
                
                # Get format info
                formats = self.video_info.get('formats', [])
                has_video = False
                has_audio = False
                max_height = 0
                max_fps = 0
                is_hdr = False
                dynamic_range = ""
                
                # Debug log all formats
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, "Available formats:\n")
                
                # First pass: find the best quality available
                for f in formats:
                    # Debug log format details
                    format_note = f.get('format_note', '')
                    height = f.get('height', 0)
                    fps = f.get('fps', 0)
                    vcodec = f.get('vcodec', 'none')
                    acodec = f.get('acodec', 'none')
                    
                    self.log_text.insert(tk.END, 
                        f"Format: {format_note}, Height: {height}, "
                        f"FPS: {fps}, Video: {vcodec}, Audio: {acodec}\n"
                    )
                    
                    if vcodec != 'none':
                        has_video = True
                        # Check for HDR
                        if any(x in str(vcodec).lower() for x in ['vp9.2', 'hdr', 'av01']):
                            is_hdr = True
                        # Check dynamic range from format note
                        if 'HDR' in format_note:
                            dynamic_range = "HDR"
                        elif 'Dolby Vision' in format_note:
                            dynamic_range = "Dolby Vision"
                        # Update max values
                        if height > max_height:
                            max_height = height
                        if fps > max_fps:
                            max_fps = fps
                    if acodec != 'none':
                        has_audio = True
                
                # Set format information
                format_text = ""
                if has_video and has_audio:
                    # Determine quality label
                    quality_label = ""
                    if max_height >= 15000:
                        quality_label = "16K"
                    elif max_height >= 8000:
                        quality_label = "8K"
                    elif max_height >= 4000:
                        quality_label = "4K"
                    elif max_height >= 2000:
                        quality_label = "2K"
                    elif max_height >= 1080:
                        quality_label = f"{max_height}p"
                    else:
                        quality_label = f"{max_height}p"
                    
                    # Add dynamic range indicator
                    if dynamic_range:
                        quality_label += f" {dynamic_range}"
                    elif is_hdr:
                        quality_label += " HDR"
                    
                    # Always show FPS
                    fps_text = f" {max_fps}FPS"
                    
                    format_text = f"🎥+🔊 Video+Audio ({quality_label}{fps_text})"
                elif has_video:
                    quality_label = ""
                    if max_height >= 15000:
                        quality_label = "16K"
                    elif max_height >= 8000:
                        quality_label = "8K"
                    elif max_height >= 4000:
                        quality_label = "4K"
                    elif max_height >= 2000:
                        quality_label = "2K"
                    else:
                        quality_label = f"{max_height}p"
                    
                    if dynamic_range:
                        quality_label += f" {dynamic_range}"
                    elif is_hdr:
                        quality_label += " HDR"
                        
                    fps_text = f" {max_fps}FPS"
                    
                    format_text = f"🎥 Video Only ({quality_label}{fps_text})"
                elif has_audio:
                    format_text = "🔊 Audio Only"
                else:
                    format_text = "Unknown Format"
                
                self.format_var.set(format_text)
                
                # Calculate and set size information
                if has_video:
                    # Adjust size estimation based on resolution, FPS, and HDR
                    base_size = max_height * 0.5  # Base size for 30fps SDR
                    fps_multiplier = max_fps / 30 if max_fps > 30 else 1
                    hdr_multiplier = 1.5 if (is_hdr or dynamic_range) else 1
                    video_size = base_size * fps_multiplier * hdr_multiplier
                    audio_size = 10 if has_audio else 0
                    total_size = video_size + audio_size
                    
                    size_text = f"💾 ~{total_size:.1f} MB"
                    if has_video and has_audio:
                        size_text += " (Video+Audio)"
                    elif has_video:
                        size_text += " (Video Only)"
                elif has_audio:
                    size_text = "💾 ~10-20 MB (Audio Only)"
                else:
                    size_text = "💾 Size unknown"
                
                self.size_var.set(size_text)
                
        except Exception as e:
            self.title_var.set("Could not fetch video information")
            self.size_var.set("")
            self.format_var.set("")
            self.platform_var.set("")
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, f"Error: {str(e)}\n")

    def play_video(self):
        """Play the downloaded video using the system's default video player"""
        if self.last_downloaded_file and os.path.exists(self.last_downloaded_file):
            try:
                if sys.platform == "darwin":  # macOS
                    subprocess.run(["open", self.last_downloaded_file])
                elif sys.platform == "win32":  # Windows
                    os.startfile(self.last_downloaded_file)
                else:  # Linux and others
                    subprocess.run(["xdg-open", self.last_downloaded_file])
            except Exception as e:
                messagebox.showerror("Error", f"Could not play video: {str(e)}")
        else:
            messagebox.showwarning("Warning", "No video file found to play")

    def download_video(self, url, output_dir, threads):
        """Download video with best quality"""
        try:
            self.root.after(10, lambda: self.log_message(f"Starting download: {url}"))
            self.root.after(10, lambda: self.log_message(f"Output directory: {output_dir}"))
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Base options with speed optimizations
            ydl_opts = {
                "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
                "format": "bestvideo+bestaudio/best",
                "ignoreerrors": True,
                "noplaylist": True,
                "quiet": True,
                "no_warnings": False,
                "progress_hooks": [self.download_progress_hook],
                "concurrent_fragment_downloads": threads,
                "retries": 10,
                "fragment_retries": 10,
                "skip_unavailable_fragments": True,
                "buffersize": 1024*1024*16,
                "http_chunk_size": 1024*1024*10,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                self.last_downloaded_file = ydl.prepare_filename(info)
                
                # Enable play button after successful download
                self.root.after(0, lambda: self.play_button.config(state=tk.NORMAL))
                
                # Update status
                self.root.after(0, lambda: self.update_status("Download completed successfully!"))
                self.root.after(0, lambda: self.log_message("Download completed successfully!"))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed: {str(e)}"))
            self.root.after(0, lambda: self.log_message(f"Error: {str(e)}"))
        finally:
            self.is_downloading = False
            self.root.after(0, lambda: self.download_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.cancel_button.config(state=tk.DISABLED))

    def start_download(self):
        """Start the download process"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a video URL")
            return
            
        if not any(domain in url.lower() for domain in [
            "youtube.com", "youtu.be", "facebook.com", "fb.watch", "instagram.com",
            "twitter.com", "tiktok.com", "vimeo.com", "dailymotion.com"
        ]):
            messagebox.showwarning("Warning", "Please enter a supported video URL")
            return
        
        # Disable download button and enable cancel button
        self.download_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.play_button.config(state=tk.DISABLED)
        
        # Reset progress
        self.progress_var.set(0.0)
        self.status_var.set("Starting download...")
        self.log_text.delete(1.0, tk.END)
        
        # Start download in a separate thread
        self.is_downloading = True
        self.download_thread = threading.Thread(
            target=self.download_video,
            args=(url, self.output_var.get(), 8)  # Using fixed 8 threads
        )
        self.download_thread.start()

    def cancel_download(self):
        """Cancel the current download"""
        if self.is_downloading and self.ydl:
            self.ydl.interrupt()
            self.update_status("Download cancelled")
            self.log_message("Download cancelled by user")
            self.download_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)
            self.is_downloading = False


def main():
    root = tk.Tk()
    app = VideoDownloaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
