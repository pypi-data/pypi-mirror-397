# dacquaviva-youtube-collector

Python library for collecting YouTube video data and downloading thumbnails.

## Installation

```bash
pip install dacquaviva-youtube-collector
```

## Quick Start

```python
from youtube_collector import YouTubeClient

# Initialize (uses YOUTUBE_API_KEY environment variable)
client = YouTubeClient()

# Fetch videos from 7 days ago
videos = client.fetch_videos_by_publish_date(days_ago=7)

# Download thumbnails
paths = client.download_thumbnails_bulk(videos)

# Save metadata to CSV
client.save_to_csv(videos, "dataset.csv")
```

## API Key Setup

```bash
export YOUTUBE_API_KEY=your_api_key
```

Get your key at [Google Cloud Console](https://console.cloud.google.com/)

## License

MIT
