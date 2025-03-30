#!/usr/bin/env python3
"""
YouTube HD Video Downloader - SuperFast Edition
A script to download YouTube videos in HD quality with high-quality audio at maximum speed.
"""

import os
import sys
import argparse
import time
from typing import Optional, Dict, Any, List
import yt_dlp
import concurrent.futures


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Download YouTube videos in HD quality at maximum speed")
    parser.add_argument(
        "url", 
        help="YouTube video URL to download (can be single URL or comma-separated list)"
    )
    parser.add_argument(
        "-o", 
        "--output", 
        default="downloads",
        help="Output directory (default: downloads)"
    )
    parser.add_argument(
        "-q", 
        "--quality", 
        choices=["1080p", "1440p", "2160p", "best"],
        default="best",
        help="Video quality to download (default: best)"
    )
    parser.add_argument(
        "--audio-only", 
        action="store_true",
        help="Download audio only"
    )
    parser.add_argument(
        "--list-formats", 
        action="store_true",
        help="List available formats instead of downloading"
    )
    parser.add_argument(
        "--threads", 
        type=int,
        default=4,
        help="Number of download threads (default: 4)"
    )
    parser.add_argument(
        "--concurrent", 
        action="store_true",
        help="Enable concurrent downloads for multiple URLs"
    )
    parser.add_argument(
        "--limit-rate", 
        type=str,
        help="Limit download rate (e.g., 50M for 50 MB/s)"
    )
    return parser.parse_args()


def get_quality_options(quality: str) -> Dict[str, Any]:
    """Get yt-dlp options based on requested quality."""
    if quality == "1080p":
        format_str = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
    elif quality == "1440p":
        format_str = "bestvideo[height<=1440]+bestaudio/best[height<=1440]"
    elif quality == "2160p":
        format_str = "bestvideo[height<=2160]+bestaudio/best[height<=2160]"
    else:  # best
        format_str = "bestvideo+bestaudio/best"
    
    return {
        "format": format_str,
        "merge_output_format": "mp4",
    }


def download_video(url: str, output_dir: str, quality: str, audio_only: bool = False, 
                threads: int = 4, limit_rate: Optional[str] = None) -> None:
    """Download a YouTube video with specified quality at maximum speed."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Base options with speed optimizations
    ydl_opts = {
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "ignoreerrors": True,
        "noplaylist": True,
        "quiet": False,
        "no_warnings": False,
        "progress": True,
        "concurrent_fragment_downloads": threads,  # Use multiple threads for fragments
        "retries": 10,                           # Retry more times on failure
        "fragment_retries": 10,                  # Retry more times on fragment failure
        "skip_unavailable_fragments": True,       # Skip unavailable fragments
        "buffersize": 1024*1024*16,              # 16MB buffer size
        "http_chunk_size": 1024*1024*10,         # 10MB chunks
    }
    
    # Add rate limit if specified
    if limit_rate:
        ydl_opts["ratelimit"] = limit_rate
    
    # Handle audio-only case
    if audio_only:
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
        ydl_opts.update(get_quality_options(quality))
    
    print(f"Downloading video from: {url}")
    print(f"Quality setting: {'Audio only' if audio_only else quality}")
    print(f"Output directory: {output_dir}")
    print(f"Using {threads} download threads for maximum speed")
    
    start_time = time.time()
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"\nDownload completed successfully in {duration:.2f} seconds!")
    except Exception as e:
        print(f"\nError downloading video: {e}")
        sys.exit(1)


def list_available_formats(url: str) -> None:
    """List all available formats for a video without downloading."""
    ydl_opts = {
        "listformats": True,
        "quiet": False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"Error listing formats: {e}")
        sys.exit(1)


def download_multiple_videos(urls: List[str], output_dir: str, quality: str, 
                           audio_only: bool = False, threads: int = 4, 
                           concurrent: bool = False, limit_rate: Optional[str] = None) -> None:
    """Download multiple videos concurrently for maximum speed."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"Preparing to download {len(urls)} videos")
    print(f"Output directory: {output_dir}")
    print(f"Using {threads} download threads per video")
    
    if concurrent:
        print("Using concurrent downloads for multiple videos")
        start_time = time.time()
        
        # Use ThreadPoolExecutor to download videos concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(urls), 4)) as executor:
            futures = []
            for url in urls:
                future = executor.submit(
                    download_video, url, output_dir, quality, audio_only, threads, limit_rate
                )
                futures.append(future)
            
            # Wait for all downloads to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error in concurrent download: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"\nAll downloads completed in {duration:.2f} seconds!")
    else:
        # Download videos sequentially
        start_time = time.time()
        for url in urls:
            download_video(url, output_dir, quality, audio_only, threads, limit_rate)
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"\nAll downloads completed in {duration:.2f} seconds!")


def main() -> None:
    """Main function."""
    args = parse_arguments()
    
    # Check if multiple URLs are provided
    if ',' in args.url:
        urls = [url.strip() for url in args.url.split(',')]
        if args.list_formats:
            # Only list formats for the first URL if multiple are provided
            list_available_formats(urls[0])
        else:
            download_multiple_videos(
                urls, args.output, args.quality, args.audio_only, 
                args.threads, args.concurrent, args.limit_rate
            )
    else:
        if args.list_formats:
            list_available_formats(args.url)
        else:
            download_video(
                args.url, args.output, args.quality, args.audio_only, 
                args.threads, args.limit_rate
            )


if __name__ == "__main__":
    main()
