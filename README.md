# YouTube HD Downloader - SuperFast Edition

YouTube videos ko HD quality (1080p, 1440p, 2160p/4K) mein maximum speed se download karne ke liye ek powerful tool.

## Features

- SuperFast download with multi-threading
- HD video download (1080p, 1440p, 2160p/4K)
- High quality audio
- Audio-only download option
- Available formats listing
- Multiple video concurrent downloads
- Download speed optimization

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/youtube-downloader.git
cd youtube-downloader
```

2. Install dependencies:
```
pip install -r requirements.txt
```

## Usage

### Basic Usage

Video ko best quality mein maximum speed se download karne ke liye:

```
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --threads 8
```

### Specific Quality

Video ko specific quality mein download karne ke liye:

```
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --quality 1080p
```

Quality options: `1080p`, `1440p`, `2160p`, `best`

### Custom Output Directory

Output directory specify karne ke liye:

```
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" -o "my_videos"
```

### Audio Only

Sirf audio download karne ke liye:

```
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --audio-only
```

### List Available Formats

Video ke available formats list karne ke liye:

```
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --list-formats
```

### SuperFast Download Options

#### Multi-threading

Download speed ko increase karne ke liye threads ka number specify karein:

```
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --threads 8
```

#### Multiple Videos Concurrent Download

Multiple videos ko comma-separated list ke through concurrent download karein:

```
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID1,https://www.youtube.com/watch?v=VIDEO_ID2" --concurrent
```

#### Download Speed Control

Download speed ko limit karne ke liye (network congestion avoid karne ke liye):

```
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --limit-rate 50M
```

## Requirements

- Python 3.6+
- yt-dlp

## License

MIT License
