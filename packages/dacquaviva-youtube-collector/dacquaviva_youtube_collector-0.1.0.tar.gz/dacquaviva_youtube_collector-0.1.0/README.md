# youtube_collector

A clean, production-ready Python library for collecting YouTube video data and downloading thumbnails using the YouTube Data API v3.

## Features

- 🎯 **Simple API** - One unified client for all operations
- 🔐 **Flexible Auth** - Environment variables or direct API key
- 📊 **Structured Data** - Clean dictionary output with all video metadata
- 🖼️ **Bulk Downloads** - Download multiple thumbnails efficiently
- ⚙️ **Configurable** - Customize categories, regions, and result limits
- 🪵 **Proper Logging** - Built-in logging support
- ✅ **Well Tested** - Comprehensive test coverage

## Installation

```bash
pip install youtube-collector
```

Or install in development mode:

```bash
pip install -e .
```

## Quick Start

```python
from youtube_collector import YouTubeClient

# Initialize (uses YOUTUBE_API_KEY environment variable)
client = YouTubeClient()

# Fetch videos from 7 days ago
videos = client.fetch_videos_by_publish_date(days_ago=7)

print(f"Found {len(videos)} videos")
for video in videos:
    print(f"- {video['title']} ({video['views']:,} views)")

# Download thumbnails
paths = client.download_thumbnails_bulk(videos)
print(f"Downloaded {len(paths)} thumbnails")

# Save metadata to CSV
client.save_to_csv(videos, "dataset.csv")
```

## API Reference

### YouTubeClient

#### Initialize

```python
# Using environment variable
client = YouTubeClient()

# Or pass directly
client = YouTubeClient(api_key="AIzaSy...")
```

#### Fetch Videos

```python
videos = client.fetch_videos_by_publish_date(
    days_ago=30,                      # Days ago to search
    max_results_per_category=10,      # Max per category
    categories=['10', '20'],          # Optional: custom categories
    region_code='US',                 # Region code
    order='viewCount'                 # Sort order (see below)
)
```

**Order options:**
- `'viewCount'` - High to low views (successful thumbnails)
- `'date'` - Chronological order (mixed performance)
- `'rating'` - By rating
- `'relevance'` - By relevance
- `'title'` - Alphabetical

Returns list of dictionaries:
```python
{
    'video_id': 'abc123',
    'title': 'Video Title',
    'description': 'Video description explaining what the video is about...',
    'category': '10',
    'views': 1000000,
    'likes': 50000,
    'published_date': '2024-01-01T00:00:00Z',
    'days_since_publish': 30,
    'video_url': 'https://youtube.com/watch?v=abc123',
    'thumbnail_url': 'https://i.ytimg.com/vi/abc123/hqdefault.jpg',
    'channel_id': 'UCxxxxxx',
    'channel_title': 'Channel Name',
    'channel_subscribers': 500000
}
```

#### Download Thumbnails

```python
# Single download
path = client.download_thumbnail(
    thumbnail_url='https://i.ytimg.com/...',
    video_id='abc123',
    output_dir='./thumbnails'  # Optional
)

# Bulk download
paths = client.download_thumbnails_bulk(
    videos,
    output_dir='./thumbnails'  # Optional
)
```

#### Save to CSV

```python
# Save metadata to CSV
client.save_to_csv(videos, "dataset.csv")

# Overwrite instead of append
client.save_to_csv(videos, "dataset.csv", append=False)
```

## Configuration

### API Key

```bash
export YOUTUBE_API_KEY=your_api_key
```

Or in `.env` file:
```
YOUTUBE_API_KEY=your_api_key
```

### Output Directory

Default: `./data/thumbnails`

Override:
```bash
export OUTPUT_DIR=/custom/path
```

## Building a Balanced Dataset for ML

For training a thumbnail prediction model, you need both successful and unsuccessful examples:

```python
import logging
from youtube_collector import YouTubeClient

logging.basicConfig(level=logging.INFO)
client = YouTubeClient()

# Collect HIGH-VIEW videos (successful thumbnails)
high_view_videos = client.fetch_videos_by_publish_date(
    days_ago=30,
    max_results_per_category=20,
    order='viewCount'  # Sorted by views (high to low)
)

# Collect MIXED videos (by upload date - includes low-view videos)
mixed_videos = client.fetch_videos_by_publish_date(
    days_ago=30,
    max_results_per_category=20,
    order='date'  # Chronological order
)

# Combine for balanced dataset
all_videos = high_view_videos + mixed_videos

# Remove duplicates
seen_ids = set()
unique_videos = []
for video in all_videos:
    if video['video_id'] not in seen_ids:
        seen_ids.add(video['video_id'])
        unique_videos.append(video)

print(f"Collected {len(unique_videos)} unique videos")
print(f"Channel subscriber range: {min(v['channel_subscribers'] for v in unique_videos):,} - {max(v['channel_subscribers'] for v in unique_videos):,}")

# Download thumbnails
paths = client.download_thumbnails_bulk(unique_videos)
print(f"Downloaded {len(paths)} thumbnails")

# Save to CSV
client.save_to_csv(unique_videos, "balanced_dataset.csv", append=False)
```

## Complete Example

```python
import logging
from youtube_collector import YouTubeClient

# Enable logging
logging.basicConfig(level=logging.INFO)

# Initialize
client = YouTubeClient()

# Fetch videos
videos = client.fetch_videos_by_publish_date(
    days_ago=30,
    max_results_per_category=20
)

print(f"Found {len(videos)} videos")

# Sort by views
videos.sort(key=lambda v: v['views'], reverse=True)

# Show top 10
for i, video in enumerate(videos[:10], 1):
    print(f"{i}. {video['title']} - {video['views']:,} views")

# Download all thumbnails
paths = client.download_thumbnails_bulk(videos)
print(f"Downloaded {len(paths)} thumbnails")

# Save to CSV
client.save_to_csv(videos, "dataset.csv")
```

## Default Categories

- `10` - Music
- `17` - Sports
- `20` - Gaming
- `22` - People & Blogs
- `23` - Comedy
- `24` - Entertainment
- `25` - News & Politics
- `26` - How-to & Style
- `27` - Education
- `28` - Science & Technology

## Getting a YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **YouTube Data API v3**
4. Create Credentials → API Key
5. Copy and set as `YOUTUBE_API_KEY`

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=youtube_collector

# Build package
python -m build
```

## License

MIT License - see LICENSE file for details.
