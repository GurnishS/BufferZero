from app.logger import logger
import httpx
import urllib.parse
import json
import random
import concurrent
import asyncio
from app.utils.api_error import ApiError
import os
from yt_dlp import YoutubeDL
from app.config import COOKIE_PATH
from app.enums.video_qualities import VideoQuality
from app.enums.audio_qualities import AudioQuality
from app.db.database_manager import db

headers_list = [
    # Chrome (Windows)
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    },
    # Chrome (macOS)
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    },
    # Firefox (Windows)
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    },
    # Firefox (macOS)
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    },
    # Microsoft Edge (Windows)
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    },
    # Safari (macOS)
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    },
    # Chrome (Android Mobile)
    {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    },
    {
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    },
    # Safari (iOS Mobile)
    {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    },
    {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    },
    # Chrome (Linux)
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    },
    {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    },
    # Opera (Windows)
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/110.0.0.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    },
]

class YoutubeService:
    """
    YouTube service for handling video/audio downloads, searches, and metadata extraction.
    
    This service provides async methods for:
    - Searching videos and playlists
    - Getting video/playlist information with caching
    - Downloading videos and audio with quality control
    - Managing download locks to prevent concurrent downloads
    """
    
    def __init__(self) -> None:
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
    
    async def get_suggestions(self, q: str) -> dict[str, str | list[str]]:
        """
        Get search suggestions from Google/YouTube.
        
        Args:
            q: Search query string
            
        Returns:
            dictionary containing query and suggestions or error message
        """
        if not q or not q.strip():
            return {"error": "Query parameter is required"}
        
        url = f"https://suggestqueries.google.com/complete/search?client=youtube&ds=yt&q={urllib.parse.quote(q)}"

        headers = {
            "User-Agent": random.choice(headers_list)["User-Agent"],
            "Accept": random.choice(headers_list)["Accept"],
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                body = response.text

                # Strip JSONP wrapper
                if body.startswith("window.google.ac.h("):
                    json_str = body[len("window.google.ac.h("):-1]
                    parsed = json.loads(json_str)
                    
                    if len(parsed) > 1 and isinstance(parsed[1], list):
                        suggestions = [
                            item[0] for item in parsed[1] 
                            if isinstance(item, list) and len(item) > 0
                        ]
                        return {"query": parsed[0], "suggestions": suggestions}

                return {"error": "Unexpected response format"}

        except httpx.TimeoutException:
            logger.error(f"Timeout while fetching suggestions for query: {q}")
            return {"error": "Request timeout"}
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while fetching suggestions: {e}")
            return {"error": f"HTTP error: {e}"}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return {"error": "Invalid response format"}
        except Exception as e:
            logger.error(f"Unexpected error while fetching suggestions: {e}")
            return {"error": str(e)}

    async def search_videos(self, query: str, max_results: int = 10) -> list[dict[str, any]]:
        """
        Search YouTube videos using yt-dlp.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 10)
            
        Returns:
            list of video information dictionaries
            
        Raises:
            ApiError: If query is missing or search fails
        """
        if not query or not query.strip():
            raise ApiError(status_code=400, message="Query parameter is required", error_code="MISSING_QUERY")

        # Validate max_results
        max_results = max(1, min(max_results, 50))  # Limit between 1-50

        ydl_opts = {
            "quiet": True,
            "retries": 3,
            "extract_flat": True,
            "forcejson": True,
            "noplaylist": True,
            "max_results": max_results
        }
        
        if os.path.exists(COOKIE_PATH):
            ydl_opts["cookiefile"] = COOKIE_PATH
            
        def search_in_thread() -> dict[str, any]:
            with YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)

        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(self._executor, search_in_thread)
            
            data=info.get("entries", [])
            
            return [{
                "video_id": d.get("id"),
                "title": d.get("title"),
                "video_url": d.get("url"),
                "description":d.get("description"),
                "thumbnail": "https://img.youtube.com/vi/"+d.get("id")+"/hqdefault.jpg",
                "duration": d.get("duration"),
                "uploader": d.get("uploader"),
                "upload_date": d.get("upload_date", ""),
            } for d in data]

        except Exception as e:
            logger.error(f"Error searching YouTube videos for query '{query}': {e}")
            raise ApiError(status_code=500, message="Failed to search YouTube videos", error_code="SEARCH_ERROR")
        
    async def search_shorts(self, query: str, max_results: int = 10) -> list[dict[str, any]]:
        """
        Search YouTube Shorts using yt-dlp.

        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 10)
            
        Returns:
            list of video information dictionaries
            
        Raises:
            ApiError: If query is missing or search fails
        """
        if not query or not query.strip():
            raise ApiError(status_code=400, message="Query parameter is required", error_code="MISSING_QUERY")

        # Validate max_results
        max_results = max(1, min(max_results, 50))  # Limit between 1-50

        ydl_opts = {
            "quiet": True,
            "retries": 3,
            "extract_flat": True,
            "forcejson": True,
            "noplaylist": True,
            "max_results": max_results+10 #To filter out simple videos if any
        }
        
        if os.path.exists(COOKIE_PATH):
            ydl_opts["cookiefile"] = COOKIE_PATH
            
        def search_in_thread() -> dict[str, any]:
            with YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(f"ytsearch{max_results+10}:{query} #shorts", download=False)

        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(self._executor, search_in_thread)
            # Filter out non shorts videos
            shorts = [entry for entry in info.get("entries", []) if "/shorts/" in entry.get("url", "")]
            if len(shorts) > max_results:
                shorts = shorts[:max_results]            
            return [{
                "video_id": d.get("id"),
                "title": d.get("title"),
                "video_url": d.get("url"),
                "description":d.get("description"),
                "thumbnail": "https://img.youtube.com/vi/"+d.get("id")+"/hqdefault.jpg",
                "duration": d.get("duration"),
                "uploader": d.get("uploader"),
                "upload_date": d.get("upload_date", ""),
            } for d in shorts]
        except Exception as e:
            logger.error(f"Error searching YouTube videos for query '{query}': {e}")
            raise ApiError(status_code=500, message="Failed to search YouTube videos", error_code="SEARCH_ERROR")

    async def search_playlists(self, query: str, max_results: int = 5) -> list[dict[str, any]]:
        """
        Search for playlists and fetch their full details concurrently.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 5)
            
        Returns:
            list of playlist information dictionaries
            
        Raises:
            ApiError: If query is missing or search fails
        """
        if not query or not query.strip():
            raise ApiError(400, "Query parameter is required", "MISSING_QUERY")

        # Validate max_results
        max_results = max(1, min(max_results, 20))  # Limit between 1-20

        # Step 1: Perform a fast search to get playlist URLs
        encoded_query = urllib.parse.quote_plus(query)
        search_url = f"https://www.youtube.com/results?search_query={encoded_query}&sp=EgIQAw%3D%3D"

        ydl_opts = {
            'quiet': True,
            'retries': 3,
            'extract_flat': True,
            'forcejson': True,
            'playlistend': max_results,
        }

        def search_for_urls_in_thread() -> dict[str, any]:
            with YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(search_url, download=False)
        
        try:
            loop = asyncio.get_running_loop()
            search_result = await loop.run_in_executor(self._executor, search_for_urls_in_thread)
            
            if not (search_result and search_result.get('entries')):
                return []
            
            playlists=search_result['entries']
            print(playlists)

            return [
                {
                    "playlist_id": d.get("id", ""),
                    "title": d.get("title", ""),
                    "thumbnail": self._extract_thumbnail(d.get("thumbnails", [])),
                    "playlist_url": d.get("url", ""),
                }
                for d in playlists
            ]

        except Exception as e:
            logger.error(f"Error during playlist search for query '{query}': {e}")
            raise ApiError(500, "Failed during playlist search process", "SEARCH_PROCESS_ERROR")
        
        
    async def get_video_info(self, video_id: str) -> dict[str, any]:
        """
        Get video information with caching support.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            dictionary containing video information or None if not found
            
        Raises:
            ApiError: If video_id is invalid or extraction fails
        """
        if not video_id or not video_id.strip():
            raise ApiError(400, "Invalid YouTube video ID", "INVALID_ID")

        # Check cache first
        cached_video = await db.get_video(video_id)
        if cached_video:
            logger.info(f"Cache hit for video ID: {video_id}")
            return cached_video
        
        logger.info(f"Cache miss for video ID: {video_id}, fetching from yt-dlp")
        
        # Extract video info using yt-dlp
        ydl_opts = {
            "skip_download": True,
            "retries": 3,
            "forcejson": True,
            "no_warnings": False,
            "encoding": "utf-8",
            'extractor_args': {
                'youtube': {
                    'player_client': ['all']
                }
            }
        }
        
        if os.path.exists(COOKIE_PATH):
            ydl_opts["cookiefile"] = COOKIE_PATH

        url = self.get_video_url(video_id)
        logger.info(f"Fetching video info for url: {url}")

        def extract_info_in_thread() -> dict[str, any]:
            with YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        
        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(self._executor, extract_info_in_thread)
            
            # Check for video format availability
            if not info.get("formats"):
                logger.error(f"No formats available for video ID: {video_id}")
                raise ApiError(404, "Video formats not available", "NO_FORMATS")

            video_info = {
                "video_id": video_id,
                "title": info.get("title", "Unknown"),
                "thumbnail": "https://img.youtube.com/vi/"+video_id+"/hqdefault.jpg",
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader", "Unknown"),
                "upload_date": info.get("upload_date", ""),
                "description": info.get("description", "")
            }

            # Process available formats
            available_formats = info.get("formats", [])
            audio_qualities = self._extract_audio_qualities(available_formats, video_id)
            video_qualities = self._extract_video_qualities(available_formats, video_id)
            #Add audio filesize to approx video filesize
            for video in video_qualities:
                video["filesize"] += audio_qualities[-1]["filesize"] if audio_qualities else 0
            
            video_info["video_qualities"] = video_qualities
            video_info["audio_qualities"] = audio_qualities
            
            # Store video information in the database
            success = await db.store_video_info(video_info)
                    
            if not success:
                logger.error(f"Failed to store video information for video ID: {video_id}")
                raise ApiError(500, "Failed to store video information", "STORAGE_ERROR")
                
            logger.info(f"Video information stored successfully for video ID: {video_id}")
            return video_info
            
        except ApiError:
            raise
        except Exception as e:
            logger.error(f"Error extracting video info for {video_id}: {e}")
            raise ApiError(500, "Failed to extract video information", "EXTRACTION_ERROR")

    def _extract_video_qualities(self, available_formats: list[dict[str, any]], video_id: str) -> list[dict[str, any]]:
        """Extract available video qualities from formats."""
        video_qualities = []
        for video_format in VideoQuality.list():
            matched = next((fmt for fmt in available_formats if video_format in fmt.get("format_note", "")), None)
            if matched:
                logger.info(f"Video format {video_format} is available for video ID: {video_id}")
                video_qualities.append({
                    "format": video_format,
                    "filesize": matched.get("filesize", 0),
                })
            else:
                logger.warning(f"Video format {video_format} not available for video ID: {video_id}")
        return video_qualities

    def _extract_audio_qualities(self, available_formats: list[dict[str, any]], video_id: str) -> list[dict[str, any]]:
        """Extract available audio qualities from formats."""
        audio_qualities = []
        for audio_quality in AudioQuality.list():
            matched = next((fmt for fmt in available_formats if audio_quality in fmt.get("format_note", "")), None)
            if matched:
                logger.info(f"Audio quality {audio_quality} is available for video ID: {video_id}")
                audio_qualities.append({
                    "format": audio_quality,
                    "filesize": matched.get("filesize", 0),
                })
            else:
                logger.warning(f"Audio quality {audio_quality} not available for video ID: {video_id}")
        return audio_qualities
    
    async def get_playlist_info(self, playlist_id: str) -> dict[str, any]:
        """
        Get playlist information with caching support.
        
        Args:
            playlist_id: YouTube playlist ID
            
        Returns:
            dictionary containing playlist information or None if not found
            
        Raises:
            ApiError: If playlist_id is invalid or extraction fails
        """
        if not playlist_id or not playlist_id.strip():
            raise ApiError(400, "Invalid YouTube playlist ID", "INVALID_ID")

        # Check cache first
        cached_playlist = await db.get_playlist(playlist_id)
        if cached_playlist:
            logger.info(f"Cache hit for playlist ID: {playlist_id}")
            return cached_playlist
        
        logger.info(f"Cache miss for playlist ID: {playlist_id}, fetching from yt-dlp")
        
        # Fetch playlist information using yt-dlp
        ydl_opts = {
            "quiet": True,
            "retries": 3,
            "extract_flat": True,
            "dump_single_json": True,
            "is_playlist": True,
            "encoding": "utf-8",
            'extractor_args': {
                'youtube': {
                    'player_client': ['all']
                }
            }
        }
        
        playlist_url = self.get_playlist_url(playlist_id)
        
        def extract_info_in_thread() -> dict[str, any]:
            with YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(playlist_url, download=False)

        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(self._executor, extract_info_in_thread)
            
            playlist_info = {
                "playlist_id": playlist_id,
                "title": info.get("title", "Unknown Playlist"),
                "uploader": info.get("uploader", "Unknown"),
                "description": info.get("description", ""),
                "thumbnail": self._extract_thumbnail(info.get("thumbnails", [])),
                "total_videos": len(info.get("entries", [])),
                "videos": []
            }
            
            # Process playlist videos
            for idx, entry in enumerate(info.get("entries", [])):
                if entry:
                    
                    video_id = entry.get("id", "")
                    #Set thumbnail of the first video as playlist thumbnail
                    if idx==0:
                        playlist_info["thumbnail"] = "https://img.youtube.com/vi/"+video_id+"/hqdefault.jpg"

                    playlist_info["videos"].append({
                        "video_id": video_id,
                        "title": entry.get("title", "Unknown Video"),
                        "thumbnail": "https://img.youtube.com/vi/"+video_id+"/hqdefault.jpg",
                        "duration": entry.get("duration", 0),
                        "uploader": entry.get("uploader", "Unknown"),
                        "upload_date": entry.get("upload_date", ""),
                        "description": entry.get("description", "")
                    })
                    
            # Store playlist information in the database
            success = await db.store_playlist_info(playlist_info)
            if not success:
                logger.error(f"Failed to store playlist information for playlist ID: {playlist_id}")
                raise ApiError(500, "Failed to store playlist information", "STORAGE_ERROR")
            
            logger.info(f"Playlist information stored successfully for playlist ID: {playlist_id}")
            return playlist_info
            
        except ApiError:
            raise
        except Exception as e:
            logger.error(f"Error extracting playlist info for {playlist_id}: {e}")
            raise ApiError(500, "Failed to extract playlist information", "EXTRACTION_ERROR")

    def _extract_thumbnail(self, thumbnails: list[dict[str, any]]) -> str:
        """Extract the best thumbnail URL from thumbnails list."""
        if not thumbnails or not isinstance(thumbnails, list):
            return ""
        
        # Get the first thumbnail with a URL
        for thumbnail in thumbnails:
            if isinstance(thumbnail, dict) and thumbnail.get("url"):
                return thumbnail["url"]
        
        return ""

    def get_video_url(self, video_id: str) -> str:
        """
        Returns the YouTube video URL based on the video ID.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Complete YouTube video URL
        """
        return f"https://www.youtube.com/watch?v={video_id}"
    
    def get_playlist_url(self, playlist_id: str) -> str:
        """
        Returns the YouTube playlist URL based on the playlist ID.
        
        Args:
            playlist_id: YouTube playlist ID
            
        Returns:
            Complete YouTube playlist URL
        """
        return f"https://www.youtube.com/playlist?list={playlist_id}"

    def get_short_video_url(self, video_id: str) -> str:
        """
        Returns the YouTube short video URL based on the video ID.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Complete YouTube shorts URL
        """
        return f"https://www.youtube.com/shorts/{video_id}"

#Global yt_service instance
yt = YoutubeService()