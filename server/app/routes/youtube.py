from fastapi import APIRouter, Depends, Query, Request
from app.utils.async_handler import async_handler
from app.db.database_manager import db
from app.middleware.authorize import verify_token
from app.utils.api_error import ApiError
from app.services.yt_service import yt
from app.config import DEFAULT_DOWNLOAD_TIMEOUT
from fastapi.responses import FileResponse
from app.enums.video_qualities import VideoQuality
from app.enums.audio_qualities import AudioQuality
from pydantic import BaseModel
from datetime import date, datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

def get_client_info(request: Request) -> tuple[str, str]:
    """
    Extract client IP and fingerprint from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Tuple of (ip_address, fingerprint)
    """
    ip = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
    fingerprint = request.headers.get("Fingerprint", "unknown")
    return ip, fingerprint

class SuggestionResponse(BaseModel):
    """
    Response model for YouTube video suggestions.
    """
    query:str
    suggestions: list[str]

@router.get("/suggestions",response_model=SuggestionResponse)
@async_handler
async def get_youtube_suggestions(
    request: Request,
    user=Depends(verify_token), 
    q: str = Query(..., min_length=1, description="Search query for suggestions")
):
    """
    Get YouTube video suggestions based on search query.
    
    Args:
        q: Search query string (minimum 1 character)
        
    Returns:
        List of YouTube video suggestions
    """
    try:
        suggestions = await yt.get_suggestions(q)
        return suggestions
    except Exception as e:
        logger.error(f"Failed to get suggestions for query '{q}': {str(e)}")
        raise ApiError(status_code=500, message="Failed to get suggestions", error_code="SUGGESTIONS_ERROR")

class VideoSearchResponse(BaseModel):
    """
    Response model for YouTube video search results.
    """
    video_id:str
    title:str
    video_url:str
    description:str | None=None
    thumbnail:str
    duration:int | None=None
    uploader:str | None=None
    upload_date:str | None=None

@router.get("/video/search",response_model=list[VideoSearchResponse])
@async_handler
async def search_youtube_videos(
    request: Request,
    user=Depends(verify_token), 
    query: str = Query(..., min_length=1, description="Search query for videos"),
    max_results: int = Query(10, ge=1, le=50, description="Maximum number of results (1-50)")
):
    """
    Search YouTube videos.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (1-50)
        
    Returns:
        List of YouTube video search results
    """
    try:
        results = await yt.search_videos(query, max_results)
        return results
    except Exception as e:
        logger.error(f"Failed to search videos for query '{query}': {str(e)}")
        raise ApiError(status_code=500, message="Failed to search videos", error_code="VIDEO_SEARCH_ERROR")

@router.get("/shorts/search",response_model=list[VideoSearchResponse])
@async_handler
async def search_youtube_shorts(
    request: Request,
    user=Depends(verify_token), 
    query: str = Query(..., min_length=1, description="Search query for shorts"),
    max_results: int = Query(10, ge=1, le=50, description="Maximum number of results (1-50)")
):
    """
    Search YouTube shorts.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (1-50)

    Returns:
        List of YouTube shorts search results
    """
    try:
        results = await yt.search_shorts(query, max_results)
        return results
    except Exception as e:
        logger.error(f"Failed to search shorts for query '{query}': {str(e)}")
        raise ApiError(status_code=500, message="Failed to search shorts", error_code="SHORTS_SEARCH_ERROR")

class PlaylistSearchResponse(BaseModel):
    playlist_id:str
    title:str
    thumbnail:str
    playlist_url:str

@router.get("/playlist/search",response_model=list[PlaylistSearchResponse])
@async_handler
async def search_youtube_playlists(
    request: Request,
    user=Depends(verify_token), 
    query: str = Query(..., min_length=1, description="Search query for playlists"),
    max_results: int = Query(10, ge=1, le=50, description="Maximum number of results (1-50)")
):
    """
    Search YouTube playlists.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (1-50)
        
    Returns:
        List of YouTube playlist search results
    """
    try:
        results = await yt.search_playlists(query, max_results)
        return results
    except Exception as e:
        logger.error(f"Failed to search playlists for query '{query}': {str(e)}")
        raise ApiError(status_code=500, message="Failed to search playlists", error_code="PLAYLIST_SEARCH_ERROR")

@router.get("/video/search")
@async_handler
async def search_youtube_videos(
    request: Request,
    user=Depends(verify_token), 
    query: str = Query(..., min_length=1, description="Search query for videos"),
    max_results: int = Query(10, ge=1, le=50, description="Maximum number of results (1-50)")
):
    """
    Search YouTube videos.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (1-50)
        
    Returns:
        List of YouTube video search results
    """
    try:
        results = await yt.search_videos(query, max_results)
        return results
    except Exception as e:
        logger.error(f"Failed to search videos for query '{query}': {str(e)}")
        raise ApiError(status_code=500, message="Failed to search videos", error_code="VIDEO_SEARCH_ERROR")

@router.get("/shorts/search")
@async_handler
async def search_youtube_shorts(
    request: Request,
    user=Depends(verify_token), 
    query: str = Query(..., min_length=1, description="Search query for shorts"),
    max_results: int = Query(10, ge=1, le=50, description="Maximum number of results (1-50)")
):
    """
    Search YouTube shorts.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (1-50)

    Returns:
        List of YouTube shorts search results
    """
    try:
        results = await yt.search_shorts(query, max_results)
        return results
    except Exception as e:
        logger.error(f"Failed to search shorts for query '{query}': {str(e)}")
        raise ApiError(status_code=500, message="Failed to search shorts", error_code="SHORTS_SEARCH_ERROR")

@router.get("/playlist/search")
@async_handler
async def search_youtube_playlists(
    request: Request,
    user=Depends(verify_token), 
    query: str = Query(..., min_length=1, description="Search query for playlists"),
    max_results: int = Query(10, ge=1, le=50, description="Maximum number of results (1-50)")
):
    """
    Search YouTube playlists.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (1-50)
        
    Returns:
        List of YouTube playlist search results
    """
    try:
        results = await yt.search_playlists(query, max_results)
        return results
    except Exception as e:
        logger.error(f"Failed to search playlists for query '{query}': {str(e)}")
        raise ApiError(status_code=500, message="Failed to search playlists", error_code="PLAYLIST_SEARCH_ERROR")

class VideoInfoResponse(BaseModel):
    video_id: str
    title: str
    duration: float | None = None
    uploader: str | None = None
    upload_date: date | None = None
    description: str | None = None
    created_at: datetime
    thumbnail: str | None = None
    video_qualities: list[dict] | None = None
    audio_qualities: list[dict] | None = None

    class Config:
        orm_mode = True
    
@router.get("/video/info",response_model=VideoInfoResponse)
@async_handler
async def get_youtube_info(
    request: Request,
    user=Depends(verify_token), 
    video_id: str = Query(..., min_length=1, description="YouTube video ID")
):
    """
    Get YouTube video information and available formats.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        Video information including title, duration, formats, etc.
    """
    try:
        video_info = await yt.get_video_info(video_id)
        return video_info
    except Exception as e:
        logger.error(f"Failed to get video info for '{video_id}': {str(e)}")
        raise ApiError(status_code=500, message="Failed to get video information", error_code="VIDEO_INFO_ERROR")

class PlaylistInfoResponse(BaseModel):
    playlist_id: str
    created_at: datetime
    title: str | None = None
    description: str | None = None
    uploader: str | None = None
    thumbnail: str | None = None
    total_videos: int | None = None
    videos: list[dict] | None = None

    class Config:
        from_attributes = True

@router.get("/playlist/info",response_model=PlaylistInfoResponse)
@async_handler
async def get_youtube_playlist_info(
    request: Request,
    user=Depends(verify_token), 
    playlist_id: str = Query(..., min_length=1, description="YouTube playlist ID")
):
    """
    Get YouTube playlist information and video list.
    
    Args:
        url: YouTube playlist URL
        
    Returns:
        Playlist information including title, video count, video list, etc.
    """
    try:
        playlist_info = await yt.get_playlist_info(playlist_id)
        return playlist_info
    except Exception as e:
        logger.error(f"Failed to get playlist info for '{playlist_id}': {str(e)}")
        raise ApiError(status_code=500, message="Failed to get playlist information", error_code="PLAYLIST_INFO_ERROR")

# @router.get("/video/download")
# @async_handler
# async def download_youtube_video(
#     request: Request,
#     user=Depends(verify_token), 
#     video_id: str = Query(..., min_length=1, description="YouTube video ID"),
#     quality: str = Query(..., description=f"Video quality: {', '.join(VideoQuality.list())}"),
#     user_plan_id: str = Query(..., description="User plan ID to use for download"),
#     download_subtitles: bool = Query(False, description="Whether to download subtitles")
# ):
#     """
#     Download YouTube video with specified quality.
    
#     Args:
#         video_id: YouTube video ID
#         quality: Video quality (must be valid VideoQuality)
#         user_plan_id: ID of the user plan to use for this download
#         download_subtitles: Whether to include subtitles
        
#     Returns:
#         File download response with the video file
#     """
#     # Validate quality
#     if quality not in VideoQuality.list():
#         raise ApiError(
#             status_code=400, 
#             message=f"Invalid quality: {quality}. Valid options are: {', '.join(VideoQuality.list())}", 
#             error_code="INVALID_QUALITY"
#         )
    
#     try:
#         # Verify user plan ownership
#         user_plan = await db.get_user_plan(user_plan_id)
#         if user_plan["user_id"] != user["id"]:
#             raise ApiError(status_code=403, message="Access denied to this plan", error_code="ACCESS_DENIED")
        
#         # Get video information
        
#         video_info = await yt.get_video_info(video_id)
#         print(f"Video info for {video_id}: {video_info}")

#         video_filesize_approx = get_filesize_by_quality(video_info, quality,"video_qualities")
#         ytdlp_timeout = video_filesize_approx / (2 * 1024 * 1024) + DEFAULT_DOWNLOAD_TIMEOUT if video_filesize_approx else DEFAULT_DOWNLOAD_TIMEOUT

#         if not video_info:
#             raise ApiError(status_code=404, message="Video not found", error_code="VIDEO_NOT_FOUND")
        
#         # Extract client information
#         ip, fingerprint = get_client_info(request)
        
#         # Store download request in database
#         download_request = await db.store_download_request(
#             user_id=user["id"], 
#             user_plan_id=user_plan_id,  # Use the parameter directly instead of user_plan["id"]
#             source_url=yt.get_video_url(video_id), 
#             video_id=video_info["video_id"], 
#             thumbnail_url=video_info['thumbnail'], 
#             title=video_info['title'], 
#             video_quality=quality, 
#             audio_quality=None, 
#             subtitles=download_subtitles, 
#             ip=ip, 
#             fingerprint=fingerprint
#         )

#         try:
#             # Download the video
#             video_path = await yt.download_video(video_id, quality, download_subtitles,ytdlp_timeout)
            
#             if not video_path:
#                 await db.store_download_error(download_request["id"], "Failed to download video")
#                 raise ApiError(status_code=500, message="Failed to download video", error_code="DOWNLOAD_FAILED")
            
#             # Mark download as completed
#             await db.store_download_completion(download_request["id"])
            
#             # Return file response
#             return FileResponse(
#                 video_path,
#                 media_type="application/octet-stream",
#                 headers={"Content-Disposition": f"attachment; filename={video_info['title']}.mp4"}
#             )
            
#         except Exception as download_error:
#             await db.store_download_error(download_request["id"], str(download_error))
#             logger.error(f"Video download failed for {video_id}: {str(download_error)}")
#             raise ApiError(status_code=500, message="Video download failed", error_code="DOWNLOAD_FAILED")
            
#     except ApiError:
#         raise
#     except Exception as e:
#         logger.error(f"Unexpected error in video download: {str(e)}")
#         raise ApiError(status_code=500, message="Internal server error", error_code="INTERNAL_ERROR")

# @router.get("/audio/download")
# @async_handler
# async def download_youtube_audio(
#     request: Request,
#     user=Depends(verify_token), 
#     url: str = Query(..., min_length=1, description="YouTube video URL or video ID"),
#     quality: str = Query(..., description=f"Audio quality: {', '.join(AudioQuality.list())}"),
#     user_plan_id: str = Query(..., description="User plan ID to use for download")
# ):
#     """
#     Download YouTube audio with specified quality.
    
#     Args:
#         url: YouTube video URL or video ID
#         quality: Audio quality (must be valid AudioQuality)
#         user_plan_id: ID of the user plan to use for this download
        
#     Returns:
#         File download response with the audio file
#     """
#     # Extract video ID from URL if needed
#     if url.startswith('http'):
#         # Extract video ID from URL
#         if 'watch?v=' in url:
#             video_id = url.split('watch?v=')[1].split('&')[0]
#         elif 'youtu.be/' in url:
#             video_id = url.split('youtu.be/')[1].split('?')[0]
#         else:
#             raise ApiError(
#                 status_code=400, 
#                 message="Invalid YouTube URL format", 
#                 error_code="INVALID_URL"
#             )
#     else:
#         # It's already a video ID
#         video_id = url
    
#     # Validate quality
#     if quality not in AudioQuality.list():
#         raise ApiError(
#             status_code=400, 
#             message=f"Invalid quality: {quality}. Valid options are: {', '.join(AudioQuality.list())}", 
#             error_code="INVALID_QUALITY"
#         )
    
#     try:
#         # Verify user plan exists and belongs to user
#         user_plan = await db.get_user_plan(user_plan_id)
#         if not user_plan:
#             raise ApiError(status_code=404, message="User plan not found", error_code="PLAN_NOT_FOUND")
        
#         if user_plan["user_id"] != user["id"]:
#             raise ApiError(status_code=403, message="Access denied to this plan", error_code="ACCESS_DENIED")

#         # Get video information
#         video_info = await yt.get_video_info(video_id)
#         if not video_info:
#             raise ApiError(status_code=404, message="Video not found", error_code="VIDEO_NOT_FOUND")
        
#         # Extract client information
#         ip, fingerprint = get_client_info(request)
        
#         # Store download request in database
#         download_request = await db.store_download_request(
#             user_id=user["id"], 
#             user_plan_id=user_plan_id,  # Use the parameter directly instead of user_plan["id"]
#             source_url=yt.get_video_url(video_id), 
#             video_id=video_info["video_id"], 
#             thumbnail_url=video_info['thumbnail'], 
#             title=video_info['title'], 
#             video_quality=None, 
#             audio_quality=quality, 
#             subtitles=False,
#             ip=ip, 
#             fingerprint=fingerprint
#         )

#         try:
#             # Get audio properties and download
#             audio_props = yt.get_audio_ytdlp_query(quality)
#             audio_path = await yt.download_audio(
#                 video_id=video_info["video_id"], 
#                 quality=quality,
#                 audio_query=audio_props["query"], 
#                 audio_tag=audio_props["tag"]
#             )

#             if not audio_path:
#                 await db.store_download_error(download_request["id"], "Failed to download audio")
#                 raise ApiError(status_code=500, message="Failed to download audio", error_code="DOWNLOAD_FAILED")
            
#             # Mark download as completed
#             await db.store_download_completion(download_request["id"])
            
#             # Return file response
#             return FileResponse(
#                 audio_path,
#                 media_type="application/octet-stream",
#                 headers={"Content-Disposition": f"attachment; filename={video_info['title']}.mp3"}
#             )
            
#         except Exception as download_error:
#             await db.store_download_error(download_request["id"], str(download_error))
#             logger.error(f"Audio download failed for {video_id}: {str(download_error)}")
#             raise ApiError(status_code=500, message="Audio download failed", error_code="DOWNLOAD_FAILED")
            
#     except ApiError:
#         raise
#     except Exception as e:
#         logger.error(f"Unexpected error in audio download: {str(e)}")
#         raise ApiError(status_code=500, message="Internal server error", error_code="INTERNAL_ERROR")


# def get_filesize_by_quality(data, quality,col):
#     for item in data[col]:
#         if item['format'] == quality:
#             return item['filesize']
#     return None