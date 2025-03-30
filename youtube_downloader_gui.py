#!/usr/bin/env python3
"""
YouTube HD Downloader - SuperFast Edition (GUI Version)
A graphical interface to download YouTube videos in HD quality with maximum speed.
"""

import os
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Dict, Any, List
import yt_dlp


class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube SuperFast Downloader")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Set style
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12))
        self.style.configure("TLabel", font=("Arial", 12))
        self.style.configure("TRadiobutton", font=("Arial", 11))
        self.style.configure("TCheckbutton", font=("Arial", 11))
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL Entry
        ttk.Label(self.main_frame, text="YouTube URL:", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        self.url_frame = ttk.Frame(self.main_frame)
        self.url_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.url_entry = ttk.Entry(self.url_frame, font=("Arial", 12))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.paste_button = ttk.Button(self.url_frame, text="Paste", command=self.paste_url)
        self.paste_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Settings Frame
        self.settings_frame = ttk.LabelFrame(self.main_frame, text="Download Settings", padding=10)
        self.settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Quality Options
        ttk.Label(self.settings_frame, text="Video Quality:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.quality_var = tk.StringVar(value="best")
        quality_options = [
            ("Best Quality", "best"),
            ("1080p", "1080p"),
            ("1440p", "1440p"),
            ("4K (2160p)", "2160p"),
            ("Audio Only", "audio")
        ]
        
        for i, (text, value) in enumerate(quality_options):
            ttk.Radiobutton(
                self.settings_frame, 
                text=text, 
                value=value, 
                variable=self.quality_var
            ).grid(row=i, column=1, sticky=tk.W, pady=2)
        
        # Threads
        ttk.Label(self.settings_frame, text="Download Threads:").grid(row=0, column=2, sticky=tk.W, padx=(30, 10), pady=5)
        
        self.threads_var = tk.IntVar(value=8)
        self.threads_spinbox = ttk.Spinbox(
            self.settings_frame, 
            from_=1, 
            to=16, 
            textvariable=self.threads_var, 
            width=5
        )
        self.threads_spinbox.grid(row=0, column=3, sticky=tk.W, pady=5)
        
        # Output Directory
        ttk.Label(self.settings_frame, text="Output Directory:").grid(row=6, column=0, sticky=tk.W, pady=10)
        
        self.output_frame = ttk.Frame(self.settings_frame)
        self.output_frame.grid(row=6, column=1, columnspan=3, sticky=tk.EW, pady=10)
        
        self.output_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.output_entry = ttk.Entry(self.output_frame, textvariable=self.output_var)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.browse_button = ttk.Button(self.output_frame, text="Browse", command=self.browse_output)
        self.browse_button.pack(side=tk.RIGHT, padx=(10, 0))
        
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
        self.log_text = tk.Text(self.progress_frame, height=10, font=("Courier", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for Log
        self.scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=self.scrollbar.set)
        
        # Button Frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Download Button
        self.download_button = ttk.Button(
            self.button_frame, 
            text="Download", 
            command=self.start_download,
            style="TButton"
        )
        self.download_button.pack(side=tk.RIGHT)
        
        # Cancel Button
        self.cancel_button = ttk.Button(
            self.button_frame, 
            text="Cancel", 
            command=self.cancel_download,
            style="TButton",
            state=tk.DISABLED
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Initialize variables
        self.download_thread = None
        self.is_downloading = False
        self.ydl = None

    def paste_url(self):
        """Paste URL from clipboard"""
        try:
            clipboard_text = self.root.clipboard_get()
            if "youtube.com" in clipboard_text or "youtu.be" in clipboard_text:
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, clipboard_text)
            else:
                messagebox.showwarning("Invalid URL", "Clipboard content is not a valid YouTube URL")
        except Exception:
            messagebox.showwarning("Clipboard Error", "Could not access clipboard content")

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

    def download_video(self, url, output_dir, quality, threads):
        """Download YouTube video with specified settings"""
        try:
            self.root.after(10, lambda: self.log_message(f"Starting download: {url}"))
            self.root.after(10, lambda: self.log_message(f"Quality: {quality}, Threads: {threads}"))
            self.root.after(10, lambda: self.log_message(f"Output directory: {output_dir}"))
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Base options with speed optimizations
            ydl_opts = {
                "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
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
            
            # Handle audio-only case
            if quality == "audio":
                ydl_opts.update({
                    "format": "bestaudio/best",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }],
                })
            else:
                # Add quality options
                if quality == "1080p":
                    format_str = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
                elif quality == "1440p":
                    format_str = "bestvideo[height<=1440]+bestaudio/best[height<=1440]"
                elif quality == "2160p":
                    format_str = "bestvideo[height<=2160]+bestaudio/best[height<=2160]"
                else:  # best
                    format_str = "bestvideo+bestaudio/best"
                
                ydl_opts.update({
                    "format": format_str,
                    "merge_output_format": "mp4",
                })
            
            start_time = time.time()
            
            self.ydl = yt_dlp.YoutubeDL(ydl_opts)
            self.ydl.download([url])
            
            end_time = time.time()
            duration = end_time - start_time
            
            self.root.after(10, lambda: self.update_progress(100))
            self.root.after(10, lambda: self.update_status(f"Download completed in {duration:.2f} seconds!"))
            self.root.after(10, lambda: self.log_message(f"Download completed in {duration:.2f} seconds!"))
            
            # Show success message
            self.root.after(10, lambda: messagebox.showinfo("Download Complete", 
                                                      f"Video downloaded successfully in {duration:.2f} seconds!"))
            
        except Exception as e:
            error_message = str(e)
            self.root.after(10, lambda: self.log_message(f"Error: {error_message}"))
            self.root.after(10, lambda: self.update_status(f"Error: {error_message}"))
            self.root.after(10, lambda: messagebox.showerror("Download Error", f"Error downloading video: {error_message}"))
        
        finally:
            self.is_downloading = False
            self.ydl = None
            self.root.after(10, lambda: self.download_button.config(state=tk.NORMAL))
            self.root.after(10, lambda: self.cancel_button.config(state=tk.DISABLED))

    def start_download(self):
        """Start the download process in a separate thread"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        if not ("youtube.com" in url or "youtu.be" in url):
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            return
        
        output_dir = self.output_var.get()
        quality = self.quality_var.get()
        threads = self.threads_var.get()
        
        # Disable download button and enable cancel button
        self.download_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        
        # Reset progress
        self.update_progress(0)
        self.update_status("Starting download...")
        self.log_text.delete(1.0, tk.END)
        
        # Start download in a separate thread
        self.is_downloading = True
        self.download_thread = threading.Thread(
            target=self.download_video,
            args=(url, output_dir, quality, threads)
        )
        self.download_thread.daemon = True
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
    app = YouTubeDownloaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
