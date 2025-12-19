"""
YouTube API client for fetching video data and downloading thumbnails.
Includes normalization and labeling for ML training.
"""

import csv
import logging
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import requests
from googleapiclient.discovery import build

from .config import get_api_key, get_output_dir

# Set up logging
logger = logging.getLogger(__name__)


class YouTubeClient:
    """
    Unified YouTube API client for fetching video data and thumbnails.

    This client handles:
    - Fetching videos by publish date across multiple categories
    - Downloading video thumbnails
    - Normalizing view counts by subscriber count
    - Labeling videos 1-5 for ML training
    - Proper error handling and logging
    - Structured data output

    Args:
        api_key: Optional YouTube Data API v3 key. If not provided,
                will use YOUTUBE_API_KEY environment variable.

    Raises:
        ConfigError: If no valid API key is provided

    Example:
        >>> client = YouTubeClient()
        >>> videos = client.fetch_balanced_dataset(days_ago=30)
        >>> print(f"Found {len(videos)} videos")
        >>> # Labels are automatically assigned 1-5
        >>> for v in videos[:5]:
        ...     print(f"{v['label']}: {v['view_subscriber_ratio']:.2f}")
    """

    # Default categories to search
    DEFAULT_CATEGORIES = {
        '10': 'Music',
        '17': 'Sports',
        '20': 'Gaming',
        '22': 'People & Blogs',
        '23': 'Comedy',
        '24': 'Entertainment',
        '25': 'News & Politics',
        '26': 'Howto & Style',
        '27': 'Education',
        '28': 'Science & Technology',
    }

    # Category-specific baseline ratios (views/subscribers expected in 30 days)
    # These help normalize across categories with different engagement patterns
    CATEGORY_BASELINES = {
        '10': 0.8,   # Music - high replay value
        '17': 0.4,   # Sports - event-driven
        '20': 0.5,   # Gaming - consistent audience
        '22': 0.3,   # People & Blogs - variable
        '23': 0.4,   # Comedy - shareable
        '24': 0.5,   # Entertainment - broad appeal
        '25': 0.6,   # News - time-sensitive, high initial views
        '26': 0.3,   # Howto - evergreen but niche
        '27': 0.25,  # Education - slow burn
        '28': 0.35,  # Science & Tech - niche audience
    }

    # Region presets for convenience
    REGION_PRESETS = {
        'US': ['US'],
        'EU': [
            'GB',  # United Kingdom
            'IE',  # Ireland
            'DE',  # Germany
            'FR',  # France
            'NL',  # Netherlands
            'SE',  # Sweden
            'DK',  # Denmark
            'FI',  # Finland
            'NO',  # Norway
            'AT',  # Austria
            'BE',  # Belgium
            'IT',  # Italy
            'ES',  # Spain
            'PT',  # Portugal
            'PL',  # Poland
        ],
        'EU_ENGLISH': [
            'GB',  # United Kingdom
            'IE',  # Ireland
            'NL',  # Netherlands (high English proficiency)
            'SE',  # Sweden (high English proficiency)
            'DK',  # Denmark (high English proficiency)
            'FI',  # Finland (high English proficiency)
            'NO',  # Norway (high English proficiency)
        ],
        'US_EU': ['US', 'GB', 'IE', 'DE', 'FR', 'NL', 'SE', 'DK', 'FI', 'NO'],
    }

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the YouTube client with API key."""
        self.api_key = get_api_key(api_key)
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self._session = requests.Session()  # Reuse connections for thumbnails
        logger.info("YouTube client initialized")

    def fetch_balanced_dataset(
        self,
        days_ago: int = 30,
        videos_per_category: int = 50,
        categories: Optional[List[str]] = None,
        region: str = "US",
        min_subscribers: int = 1000,
        min_views: int = 0,
        min_duration_seconds: int = 60,
        video_duration: str = "any",
        filter_labels: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch a balanced dataset suitable for ML training.

        Uses 'date' sort order for random-ish sampling, then assigns
        labels 1-5 based on performance.

        Args:
            days_ago: Number of days ago to search (default: 30)
            videos_per_category: Target videos per category (default: 50)
            categories: List of category IDs. If None, uses defaults
            region: Region preset name ('US', 'EU', 'EU_ENGLISH', 'US_EU')
                   or a single YouTube region code (default: "US")
            min_subscribers: Minimum channel subscribers to include
                            (filters out brand new channels)
            min_views: Minimum video views to include (filters out low-traffic videos)
            min_duration_seconds: Minimum video length in seconds (default: 60 to exclude Shorts)
            video_duration: API filter for duration ('any', 'long', 'medium', 'short').
                           'medium' = 4-20 mins, 'long' = >20 mins.
            filter_labels: Optional list of labels to keep (e.g., [1, 2] for
                          flops only, [4, 5] for top performers only).
                          If None, keeps all labels.

        Returns:
            List of labeled video dictionaries ready for ML training

        Example:
            >>> client = YouTubeClient()
            >>> # Get all videos
            >>> dataset = client.fetch_balanced_dataset(days_ago=30, region="US_EU")
            >>> # Get only flops (labels 1-2)
            >>> flops = client.fetch_balanced_dataset(days_ago=30, filter_labels=[1, 2])
            >>> # Get only top performers (labels 4-5)
            >>> tops = client.fetch_balanced_dataset(days_ago=30, filter_labels=[4, 5])
        """
        # Resolve region to list of country codes
        if region in self.REGION_PRESETS:
            region_codes = self.REGION_PRESETS[region]
        else:
            # Assume it s a single country code
            region_codes = [region]

        logger.info(
            f"Fetching balanced dataset for ML training "
            f"(regions={region_codes})"
        )

        # Fetch using 'date' sort for random-ish sampling
        all_videos = []

        for region_code in region_codes:
            videos = self.fetch_videos_by_publish_date(
                days_ago=days_ago,
                max_results_per_category=videos_per_category // max(len(region_codes), 1),
                categories=categories,
                region_code=region_code,
                order="date",
                min_duration_seconds=min_duration_seconds,
                video_duration=video_duration,
            )
            all_videos.extend(videos)

        # Deduplicate by video_id 
        seen_ids = set()
        unique_videos = []
        for video in all_videos:
            if video['video_id'] not in seen_ids:
                seen_ids.add(video['video_id'])
                unique_videos.append(video)

        # Filter by minimum subscribers and views
        filtered_videos = [
            v for v in unique_videos
            if v['channel_subscribers'] >= min_subscribers
            and v['views'] >= min_views
        ]

        logger.info(
            f"After dedup and subscriber filter: {len(filtered_videos)} videos "
            f"(removed {len(unique_videos) - len(filtered_videos)} "
            f"with <{min_subscribers} subs or <{min_views} views)"
        )

        # Assign labels 1-5 based on normalized performance
        labeled_videos = self._assign_labels(filtered_videos)

        # Filter by labels if requested
        if filter_labels:
            pre_filter_count = len(labeled_videos)
            labeled_videos = [
                v for v in labeled_videos
                if v['label'] in filter_labels
            ]
            logger.info(
                f"After label filter {filter_labels}: {len(labeled_videos)} videos "
                f"(removed {pre_filter_count - len(labeled_videos)} videos)"
            )

        return labeled_videos

    def fetch_videos_by_publish_date(
        self,
        days_ago: int = 365,
        max_results_per_category: int = 10,
        categories: Optional[List[str]] = None,
        region_code: str = "US",
        order: str = "viewCount",
        min_duration_seconds: int = 0,
        video_duration: str = "any",
    ) -> List[Dict[str, Any]]:
        """
        Fetch videos published on a specific date across multiple categories.

        Args:
            days_ago: Number of days ago to search (default: 365)
            max_results_per_category: Max videos per category (default: 10)
            categories: List of category IDs to search. If None, uses defaults
            region_code: YouTube region code (default: "US")
            order: Sort order - "viewCount" (high to low), "date", "rating",
                   "relevance", "title" (default: "viewCount")
            min_duration_seconds: Minimum duration in seconds to include.
            video_duration: API filter for duration ('any', 'long', 'medium', 'short').

        Returns:
            List of video dictionaries with structured data including
            normalized metrics.
        """
        # Calculate target date
        target_date = datetime.now() - timedelta(days=days_ago)
        published_after = target_date.replace(
            hour=0, minute=0, second=0
        ).isoformat() + 'Z'
        published_before = target_date.replace(
            hour=23, minute=59, second=59
        ).isoformat() + 'Z'

        # Use default categories if none provided
        if categories is None:
            categories = list(self.DEFAULT_CATEGORIES.keys())

        logger.info(
            f"Fetching videos from {days_ago} days ago "
            f"across {len(categories)} categories "
            f"(order={order}, region={region_code})"
        )

        all_results = []

        for category in categories:
            logger.debug(f"Fetching category {category}...")

            try:
                # Search for video IDs
                search_response = self.youtube.search().list(
                    part="id",
                    publishedAfter=published_after,
                    publishedBefore=published_before,
                    maxResults=max_results_per_category,
                    order=order,
                    type="video",
                    videoCategoryId=category,
                    regionCode=region_code,
                    videoDuration=video_duration,
                ).execute()

                video_ids = [
                    item['id']['videoId']
                    for item in search_response.get('items', [])
                ]

                if not video_ids:
                    logger.debug(f"No videos found for category {category}")
                    continue

                # Get detailed video information including language metadata
                videos_response = self.youtube.videos().list(
                    part="snippet,statistics,contentDetails",
                    id=','.join(video_ids)
                ).execute()

                # Get unique channel IDs for this batch
                channel_ids = list(set([
                    video['snippet']['channelId']
                    for video in videos_response['items']
                ]))

                # Fetch channel statistics (including subscriber count)
                channels_response = self.youtube.channels().list(
                    part="statistics",
                    id=','.join(channel_ids)
                ).execute()

                # Create a mapping of channel_id -> subscriber_count
                channel_subscribers = {
                    channel['id']: int(
                        channel['statistics'].get('subscriberCount', 0)
                    )
                    for channel in channels_response['items']
                }

                # Process and structure the data
                for video in videos_response['items']:
                    channel_id = video['snippet']['channelId']
                    video_data = self._extract_video_data(
                        video,
                        days_ago,
                        channel_subscribers.get(channel_id, 0),
                        region_code=region_code,
                    )

                    # Filter by duration (e.g. remove Shorts)
                    if video_data.get('duration_seconds', 0) < min_duration_seconds:
                        continue

                    all_results.append(video_data)
                    logger.debug(
                        f"  ✓ {video_data['video_id']}: "
                        f"{video_data['views']:,} views, "
                        f"ratio={video_data['view_subscriber_ratio']:.3f}, "
                        f"lang={video_data['default_audio_language']}, "
                        f"region={region_code}"
                    )

            except Exception as e:
                logger.error(
                    f"Error fetching category {category}: {e}",
                    exc_info=True
                )
                continue

        logger.info(f"Successfully fetched {len(all_results)} videos from {region_code}")
        return all_results

    def _extract_video_data(
        self,
        video: Dict,
        days_ago: int,
        channel_subscribers: int = 0,
        region_code: str = "US",
    ) -> Dict[str, Any]:
        """
        Extract and structure video data from API response.

        Includes normalized metrics for ML training.

        Args:
            video: Raw video data from YouTube API
            days_ago: Days since publish date
            channel_subscribers: Number of subscribers for the channel
            region_code: Region where video was found

        Returns:
            Structured video dictionary with normalized metrics
        """
        video_id = video['id']
        snippet = video['snippet']
        statistics = video.get('statistics', {})
        content_details = video.get('contentDetails', {})

        views = int(statistics.get('viewCount', 0))
        likes = int(statistics.get('likeCount', 0))
        comments = int(statistics.get('commentCount', 0))
        category_id = snippet.get('categoryId', 'Unknown')

        # Normalized metrics
        if channel_subscribers > 0:
            view_subscriber_ratio = views / channel_subscribers
            like_subscriber_ratio = likes / channel_subscribers
        else:
            view_subscriber_ratio = 0.0
            like_subscriber_ratio = 0.0

        # Category-adjusted ratio
        baseline = self.CATEGORY_BASELINES.get(category_id, 0.4)
        category_adjusted_ratio = view_subscriber_ratio / baseline

        # Time decay factor (normalize for age)
        # Videos get most views in first 48 hours, then decay
        if days_ago > 0:
            time_factor = min(days_ago / 30, 1.0)  # Cap at 30 days
        else:
            time_factor = 0.1

        # Engagement rate (likes + comments relative to views)
        if views > 0:
            engagement_rate = (likes + comments) / views
        else:
            engagement_rate = 0.0

        # Get best available thumbnail
        thumbnails = snippet.get('thumbnails', {})
        thumbnail_url = (
            thumbnails.get('maxres', {}).get('url') or
            thumbnails.get('high', {}).get('url') or
            thumbnails.get('medium', {}).get('url') or
            thumbnails.get('default', {}).get('url', '')
        )

        # Parse publish datetime for additional features
        published_at = snippet['publishedAt']
        try:
            pub_dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            publish_hour = pub_dt.hour
            publish_day_of_week = pub_dt.weekday()  # 0=Monday, 6=Sunday
        except Exception:
            publish_hour = -1
            publish_day_of_week = -1

        # Extract language metadata
        default_language = snippet.get('defaultLanguage', '')
        default_audio_language = snippet.get('defaultAudioLanguage', '')

        # Parse duration
        duration_str = content_details.get('duration', 'PT0S')
        duration_seconds = self._parse_duration(duration_str)

        return {
            'video_id': video_id,
            'title': snippet['title'],
            'title_length': len(snippet['title']),
            'description': snippet.get('description', ''),
            'description_length': len(snippet.get('description', '')),
            'category_id': category_id,
            'category_name': self.DEFAULT_CATEGORIES.get(category_id, 'Unknown'),

            # Language metadata
            'default_language': default_language,
            'default_audio_language': default_audio_language,

            # Region where video was found
            'region_code': region_code,

            # Raw metrics
            'views': views,
            'likes': likes,
            'comments': comments,
            'channel_subscribers': channel_subscribers,
            'duration_seconds': duration_seconds,

            # Normalized metrics
            'view_subscriber_ratio': round(view_subscriber_ratio, 4),
            'like_subscriber_ratio': round(like_subscriber_ratio, 4),
            'category_adjusted_ratio': round(category_adjusted_ratio, 4),
            'engagement_rate': round(engagement_rate, 4),

            # Time features
            'published_date': published_at,
            'days_since_publish': days_ago,
            'publish_hour': publish_hour,
            'publish_day_of_week': publish_day_of_week,
            'time_factor': round(time_factor, 4),

            # URLs
            'video_url': f"https://www.youtube.com/watch?v={video_id}",
            'thumbnail_url': thumbnail_url,

            # Channel info
            'channel_id': snippet['channelId'],
            'channel_title': snippet['channelTitle'],

            # Placeholder for label (assigned later)
            'label': None,
        }

    def _assign_labels(
        self,
        videos: List[Dict[str, Any]],
        method: str = "category_percentile"
    ) -> List[Dict[str, Any]]:
        """
        Assign performance labels 1-5 to videos.

        Labels:
            1 = Poor performer (bottom 20%)
            2 = Below average (20-40%)
            3 = Average (40-60%)
            4 = Above average (60-80%)
            5 = Top performer (top 20%)

        Args:
            videos: List of video dictionaries with normalized metrics
            method: Labeling method
                - "global_percentile": Percentiles across all videos
                - "category_percentile": Percentiles within each category
                - "category_adjusted": Use category-adjusted ratio globally

        Returns:
            Videos with 'label' field populated (1-5)
        """
        if not videos:
            return videos

        logger.info(f"Assigning labels using method: {method}")

        if method == "category_percentile":
            # Group by category and assign percentiles within each
            from collections import defaultdict
            by_category = defaultdict(list)

            for video in videos:
                by_category[video['category_id']].append(video)

            for category_id, category_videos in by_category.items():
                ratios = [v['view_subscriber_ratio'] for v in category_videos]
                percentiles = self._calculate_percentiles(ratios)

                for video, pct in zip(category_videos, percentiles):
                    video['label'] = self._percentile_to_label(pct)
                    video['percentile'] = round(pct, 2)

        elif method == "category_adjusted":
            # Use category-adjusted ratio with global percentiles
            ratios = [v['category_adjusted_ratio'] for v in videos]
            percentiles = self._calculate_percentiles(ratios)

            for video, pct in zip(videos, percentiles):
                video['label'] = self._percentile_to_label(pct)
                video['percentile'] = round(pct, 2)

        else:  # global_percentile
            ratios = [v['view_subscriber_ratio'] for v in videos]
            percentiles = self._calculate_percentiles(ratios)

            for video, pct in zip(videos, percentiles):
                video['label'] = self._percentile_to_label(pct)
                video['percentile'] = round(pct, 2)

        # Log label distribution
        label_counts = {}
        for video in videos:
            label = video['label']
            label_counts[label] = label_counts.get(label, 0) + 1

        logger.info(f"Label distribution: {dict(sorted(label_counts.items()))}")

        return videos

    def _calculate_percentiles(self, values: List[float]) -> List[float]:
        """Calculate percentile rank for each value in the list."""
        if not values:
            return []

        arr = np.array(values)
        # Use 'weak' method: percentage of values <= current value
        percentiles = [
            (np.sum(arr <= v) / len(arr)) * 100
            for v in values
        ]
        return percentiles

    def _parse_duration(self, duration: str) -> int:
        """Parse ISO 8601 duration string (e.g., PT1H2M10S) to seconds."""
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return 0

        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        seconds = int(match.group(3)) if match.group(3) else 0

        return hours * 3600 + minutes * 60 + seconds

    def _percentile_to_label(self, percentile: float) -> int:
        """
        Convert percentile to label 1-5.

        1 = 0-20th percentile (poor)
        2 = 20-40th percentile (below average)
        3 = 40-60th percentile (average)
        4 = 60-80th percentile (above average)
        5 = 80-100th percentile (top performer)
        """
        if percentile <= 20:
            return 1
        elif percentile <= 40:
            return 2
        elif percentile <= 60:
            return 3
        elif percentile <= 80:
            return 4
        else:
            return 5

    def download_thumbnail(
        self,
        thumbnail_url: str,
        video_id: str,
        output_dir: Optional[str] = None,
        filename: Optional[str] = None
    ) -> str:
        """
        Download a video thumbnail.

        Args:
            thumbnail_url: URL of the thumbnail to download
            video_id: YouTube video ID
            output_dir: Directory to save thumbnail.
                       If None, uses OUTPUT_DIR env var or default
            filename: Custom filename. If None, uses {video_id}.jpg

        Returns:
            Path to the downloaded file

        Raises:
            requests.RequestException: If download fails
        """
        if output_dir is None:
            output_dir = get_output_dir()

        output_path = Path(output_dir)
        print("Downloading thumbnails to:", output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        if filename is None:
            filename = f"{video_id}.jpg"

        filepath = output_path / filename

        try:
            logger.debug(f"Downloading thumbnail for {video_id}")
            response = self._session.get(thumbnail_url, timeout=30)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                f.write(response.content)

            logger.info(f"Downloaded thumbnail: {filepath}")
            return str(filepath)

        except requests.RequestException as e:
            logger.error(
                f"Failed to download thumbnail for {video_id}: {e}",
                exc_info=True
            )
            raise

    def download_thumbnails_bulk(
        self,
        videos: List[Dict[str, Any]],
        output_dir: Optional[str] = None,
        include_label_in_filename: bool = True
    ) -> Dict[str, str]:
        """
        Download thumbnails for multiple videos.

        Args:
            videos: List of video dictionaries
            output_dir: Directory to save thumbnails
            include_label_in_filename: If True, prefix filename with label
                                       (e.g., "5_abc123.jpg")

        Returns:
            Dictionary mapping video_id to filepath
        """
        results = {}
        failed = []

        logger.info(f"Starting bulk download of {len(videos)} thumbnails")

        for video in videos:
            video_id = video['video_id']
            thumbnail_url = video['thumbnail_url']
            label = video.get('label', 0)

            if include_label_in_filename and label:
                filename = f"{label}_{video_id}.jpg"
            else:
                filename = f"{video_id}.jpg"

            try:
                filepath = self.download_thumbnail(
                    thumbnail_url,
                    video_id,
                    output_dir=output_dir,
                    filename=filename
                )
                results[video_id] = filepath
            except Exception as e:
                logger.warning(
                    f"Failed to download thumbnail for {video_id}: {e}"
                )
                failed.append(video_id)

        logger.info(
            f"Bulk download complete: {len(results)} succeeded, "
            f"{len(failed)} failed"
        )

        if failed:
            logger.warning(f"Failed video IDs: {failed}")

        return results

    def save_to_csv(
        self,
        videos: List[Dict[str, Any]],
        filename: str = "dataset.csv",
        append: bool = True,
        exclude_columns: Optional[List[str]] = None
    ) -> None:
        """
        Save video metadata to CSV file.

        Args:
            videos: List of video dictionaries
            filename: Output CSV filename (default: "dataset.csv")
            append: If True, append to existing file. If False, overwrite
            exclude_columns: Columns to exclude (e.g., ['description'])

        Example:
            >>> client = YouTubeClient()
            >>> videos = client.fetch_balanced_dataset(days_ago=30)
            >>> client.save_to_csv(
            ...     videos,
            ...     "training_data.csv",
            ...     exclude_columns=['description']  # Too long for CSV
            ... )
        """
        if not videos:
            logger.warning("No videos to save")
            return

        # Filter out excluded columns
        if exclude_columns:
            videos = [
                {k: v for k, v in video.items() if k not in exclude_columns}
                for video in videos
            ]

        file_exists = os.path.isfile(filename)
        mode = 'a' if append and file_exists else 'w'

        # Validate headers match for append mode
        if append and file_exists:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                existing_headers = next(reader, None)
                new_headers = list(videos[0].keys())
                if existing_headers and set(existing_headers) != set(new_headers):
                    logger.warning(
                        f"Header mismatch! Existing: {existing_headers}, "
                        f"New: {new_headers}. Overwriting file."
                    )
                    mode = 'w'

        with open(filename, mode, newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=videos[0].keys())

            if mode == 'w':
                writer.writeheader()

            writer.writerows(videos)

        action = "Appended" if mode == 'a' else "Saved"
        logger.info(f"{action} {len(videos)} videos to {filename}")
        print(f"✓ {action} {len(videos)} videos to {filename}")

    def get_dataset_stats(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about the dataset for quality checking.

        Args:
            videos: List of labeled video dictionaries

        Returns:
            Dictionary with dataset statistics
        """
        if not videos:
            return {}

        labels = [v['label'] for v in videos if v.get('label')]
        ratios = [v['view_subscriber_ratio'] for v in videos]

        from collections import Counter
        label_dist = Counter(labels)

        # Language distribution
        lang_dist = Counter(
            v.get('default_audio_language', 'unknown') or 'unknown'
            for v in videos
        )

        # Region distribution
        region_dist = Counter(
            v.get('region_code', 'unknown')
            for v in videos
        )

        stats = {
            'total_videos': len(videos),
            'label_distribution': dict(sorted(label_dist.items())),
            'label_balance': min(label_dist.values()) / max(label_dist.values())
                            if label_dist else 0,
            'categories': len(set(v['category_id'] for v in videos)),
            'language_distribution': dict(lang_dist.most_common(10)),
            'region_distribution': dict(region_dist.most_common(20)),
            'view_ratio': {
                'min': round(min(ratios), 4),
                'max': round(max(ratios), 4),
                'mean': round(np.mean(ratios), 4),
                'median': round(np.median(ratios), 4),
            },
            'subscriber_range': {
                'min': min(v['channel_subscribers'] for v in videos),
                'max': max(v['channel_subscribers'] for v in videos),
            }
        }

        return stats