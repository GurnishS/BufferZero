from app.db.config import supabase
from app.utils.api_error import ApiError
from app.logger import logger
from app.utils.async_handler import async_handler
from fastapi.concurrency import run_in_threadpool
from app.utils.api_error import ApiError
from postgrest.exceptions import APIError
from datetime import timedelta, datetime

class DatabaseManager:
    """
    Database manager for handling all database operations with Supabase.
    
    This class provides async methods for:
    - Managing pricing plans and user plans
    - Handling video/audio cache and metadata
    - Tracking download requests and completions
    - Managing cached formats and playlists
    """
    
    def __init__(self) -> None:
        """Initialize database manager with Supabase table references."""
        self.plans = supabase.table("pricing_plans")
        self.users = supabase.table("users")
        self.cached_info = supabase.table("cached_info")
        self.cached_formats = supabase.table("cached_formats")
        self.cached_playlist = supabase.table("cached_playlist")
        self.user_plans = supabase.table("user_plans")
        self.downloads = supabase.table("downloads")
        self.payments = supabase.table("payments")
        
    async def get_plans(self) -> list[dict[str, any]]:
        """
        Retrieve all available pricing plans.
        
        Returns:
            list of pricing plan dictionaries
            
        Raises:
            ApiError: If no plans found or database error occurs
        """
        try:
            response = await run_in_threadpool(self.plans.select("*").execute)
            
            if not hasattr(response, 'data') or not response.data:
                logger.warning("No pricing plans found in database")
                raise ApiError(
                    status_code=404,
                    message="No plans found", 
                    error_code="PLANS_NOT_FOUND"
                )
            
            logger.info(f"Retrieved {len(response.data)} pricing plans")
            return response.data
            
        except APIError as e:
            logger.error(f"Database error while fetching plans: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Database error: {str(e)}", 
                error_code="DATABASE_ERROR"
            )
        except Exception as e:
            logger.error(f"Unexpected error while fetching plans: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Unexpected error: {str(e)}", 
                error_code="UNEXPECTED_ERROR"
            )

    async def get_plan(self, plan_id: str) -> dict[str, any]:
        """
        Retrieve a specific pricing plan by ID.
        
        Args:
            plan_id: Unique identifier for the pricing plan
            
        Returns:
            dictionary containing plan information
            
        Raises:
            ApiError: If plan not found or database error occurs
        """
        if not plan_id or not plan_id.strip():
            raise ApiError(
                status_code=400, 
                message="Plan ID is required", 
                error_code="INVALID_PLAN_ID"
            )
            
        try:
            response = await run_in_threadpool(
                self.plans.select("*").eq("id", plan_id).execute
            )
            
            if not hasattr(response, 'data') or not response.data:
                logger.warning(f"Plan not found with ID: {plan_id}")
                raise ApiError(
                    status_code=404, 
                    message="Plan not found", 
                    error_code="PLAN_NOT_FOUND"
                )
                
            logger.info(f"Retrieved plan with ID: {plan_id}")
            return response.data[0]
            
        except APIError as e:
            logger.error(f"Database error while fetching plan {plan_id}: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Database error: {str(e)}", 
                error_code="DATABASE_ERROR"
            )
        except Exception as e:
            logger.error(f"Unexpected error while fetching plan {plan_id}: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Unexpected error: {str(e)}", 
                error_code="UNEXPECTED_ERROR"
            )
            
    async def get_user_plans(self, user_id: str) -> list[dict[str, any]]:
        """
        Retrieve all plans associated with a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            list of user plan dictionaries with merged plan information
            
        Raises:
            ApiError: If database error occurs
        """
        if not user_id or not user_id.strip():
            raise ApiError(
                status_code=400, 
                message="User ID is required", 
                error_code="INVALID_USER_ID"
            )
            
        try:
            # Get user plans
            plan_ids_response = await run_in_threadpool(
                self.user_plans.select("*").eq("user_id", user_id).execute
            )
            
            user_plans = plan_ids_response.data

            if not user_plans:
                logger.info(f"No plans found for user: {user_id}")
                return []

            full_plans = []
            for plan in user_plans:
                try:
                    plans_response = await run_in_threadpool(
                        self.plans.select("*").eq("id", plan['plan_id']).execute
                    )
                    
                    if not plans_response.data:
                        logger.warning(f"Plan with ID {plan['plan_id']} not found for user {user_id}")
                        continue
                        
                    plan_info = plans_response.data[0].copy()
                    plan_info.pop("id", None)  # Remove plan id to avoid conflicts
                    merged_info = {**plan, **plan_info}
                    full_plans.append(merged_info)
                    
                except Exception as e:
                    logger.error(f"Error processing plan {plan['plan_id']} for user {user_id}: {e}")
                    continue

            logger.info(f"Retrieved {len(full_plans)} plans for user: {user_id}")
            return full_plans
            
        except APIError as e:
            logger.error(f"Database error while fetching user plans for {user_id}: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Database error: {str(e)}", 
                error_code="DATABASE_ERROR"
            )
        except Exception as e:
            logger.error(f"Unexpected error while fetching user plans for {user_id}: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Unexpected error: {str(e)}", 
                error_code="UNEXPECTED_ERROR"
            )

    async def get_user_plan(self, user_plan_id: str) -> dict[str, any]:
        """
        Retrieve a specific user plan with merged plan information.
        
        Args:
            user_plan_id: Unique identifier for the user plan
            
        Returns:
            dictionary containing merged user plan and plan information
            
        Raises:
            ApiError: If user plan not found or database error occurs
        """
        if not user_plan_id or not user_plan_id.strip():
            raise ApiError(
                status_code=400, 
                message="User plan ID is required", 
                error_code="INVALID_USER_PLAN_ID"
            )
            
        try:
            # Get user plan
            response = await run_in_threadpool(
                self.user_plans.select("*").eq("id", user_plan_id).execute
            )
            
            if not response.data:
                logger.warning(f"User plan not found with ID: {user_plan_id}")
                raise ApiError(
                    status_code=404, 
                    message="User plan not found", 
                    error_code="USER_PLAN_NOT_FOUND"
                )
            
            user_plan = response.data[0]
            
            # Fetch additional plan data
            plan_response = await run_in_threadpool(
                self.plans.select("*").eq("id", user_plan["plan_id"]).execute
            )
            
            if not plan_response.data:
                logger.warning(f"Associated plan not found for user plan {user_plan_id}")
                raise ApiError(
                    status_code=404, 
                    message="Associated plan not found", 
                    error_code="PLAN_NOT_FOUND"
                )

            # Merge user plan data with plan data
            plan = plan_response.data[0]
            plan.pop("id")
            merged_plan = {**user_plan, **plan}
            
            logger.info(f"Retrieved user plan with ID: {user_plan_id}")
            return merged_plan

        except APIError as e:
            logger.error(f"Database error while fetching user plan {user_plan_id}: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Database error: {str(e)}", 
                error_code="DATABASE_ERROR"
            )
        except Exception as e:
            logger.error(f"Unexpected error while fetching user plan {user_plan_id}: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Unexpected error: {str(e)}", 
                error_code="UNEXPECTED_ERROR"
            )

    async def add_user_plan(self, user_id: str, plan_id: str) -> dict[str, any]:
        """
        Add a new plan to a user's account.
        
        Args:
            user_id: Unique identifier for the user
            plan_id: Unique identifier for the plan to add
            
        Returns:
            dictionary containing the created user plan information
            
        Raises:
            ApiError: If database error occurs
        """
        if not user_id or not user_id.strip():
            raise ApiError(
                status_code=400, 
                message="User ID is required", 
                error_code="INVALID_USER_ID"
            )
            
        if not plan_id or not plan_id.strip():
            raise ApiError(
                status_code=400, 
                message="Plan ID is required", 
                error_code="INVALID_PLAN_ID"
            )
            
        try:
            # Verify plan exists before adding
            plan = await self.get_plan(plan_id)
            duration_days = plan.get("validity_days", 30)
            if not plan:
                raise ApiError(
                    status_code=404, 
                    message="Plan not found", 
                    error_code="PLAN_NOT_FOUND"
                )
            
            # Calculate validity period
            valid_until = datetime.utcnow() + timedelta(days=duration_days)
            
            user_plan_data = {
                "user_id": user_id, 
                "plan_id": plan_id,
                "valid_till": valid_until.isoformat(),
                "requests_made": 0  # Initialize requests counter
            }
            
            response = await run_in_threadpool(
                self.user_plans.insert(user_plan_data).execute
            )
            
            if not response.data:
                raise ApiError(
                    status_code=500, 
                    message="Failed to create user plan", 
                    error_code="CREATION_FAILED"
                )
            
            logger.info(f"Added plan {plan_id} to user {user_id} for {duration_days} days")
            return response.data[0]
            
        except ApiError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error while adding plan {plan_id} to user {user_id}: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Unexpected error: {str(e)}", 
                error_code="UNEXPECTED_ERROR"
            )
        
    async def remove_user_plan(self, user_id: str, plan_id: str) -> dict[str, any]:
        """
        Remove a plan from a user's account.
        
        Args:
            user_id: Unique identifier for the user
            plan_id: Unique identifier for the plan to remove
            
        Returns:
            dictionary containing the removed user plan information
            
        Raises:
            ApiError: If user plan not found or database error occurs
        """
        if not user_id or not user_id.strip():
            raise ApiError(
                status_code=400, 
                message="User ID is required", 
                error_code="INVALID_USER_ID"
            )
            
        if not plan_id or not plan_id.strip():
            raise ApiError(
                status_code=400, 
                message="Plan ID is required", 
                error_code="INVALID_PLAN_ID"
            )
            
        try:
            response = await run_in_threadpool(
                self.user_plans.delete().eq("id", plan_id).execute
            )
            
            if not response.data:
                logger.warning(f"User plan not found for user {user_id} and plan {plan_id}")
                raise ApiError(
                    status_code=404, 
                    message="User plan not found", 
                    error_code="USER_PLAN_NOT_FOUND"
                )
                
            #fetch full plan details
            plan = await self.plans.get(plan_id)
            if not plan:
                logger.warning(f"Plan not found: {plan_id}")
                raise ApiError(
                    status_code=404,
                    message="Plan not found",
                    error_code="PLAN_NOT_FOUND"
                )

            plan.pop("id")
            merged_plan = {**response.data[0], **plan}

            logger.info(f"Removed plan {plan_id} from user {user_id}")
            return merged_plan

        except APIError as e:
            logger.error(f"Database error while removing plan {plan_id} from user {user_id}: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Database error: {str(e)}", 
                error_code="DATABASE_ERROR"
            )
        except Exception as e:
            logger.error(f"Unexpected error while removing plan {plan_id} from user {user_id}: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Unexpected error: {str(e)}", 
                error_code="UNEXPECTED_ERROR"
            )
            
    async def get_video(self, video_id: str) -> dict[str, any]:
        """
        Retrieve cached video information with format availability.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            dictionary containing video information with cached format status, or None if not found
            
        Raises:
            ApiError: If database error occurs
        """
        if not video_id or not video_id.strip():
            raise ApiError(
                status_code=400,
                message="Video ID is required",
                error_code="INVALID_VIDEO_ID"
            )
            
        try:
            response = await run_in_threadpool(
                self.cached_info.select("*").eq("video_id", video_id).execute
            )

            if not response.data:
                logger.debug(f"No cached video info found for video: {video_id}")
                return None

            video_info = response.data[0].copy()

            # Initialize cached status for all qualities
            for quality in video_info.get("video_qualities", []):
                quality["is_cached"] = False

            for quality in video_info.get("audio_qualities", []):
                quality["is_cached"] = False

            # Check for cached formats
            try:
                formats_response = await run_in_threadpool(
                    self.cached_formats.select("*").eq("video_id", video_id).execute
                )

                if formats_response.data:
                    cached_formats = formats_response.data

                    # Update cached status based on available formats
                    for quality in video_info.get("video_qualities", []):
                        quality_tag = f"video_{quality.get('format', '')}"
                        if any(f.get("tag") == quality_tag for f in cached_formats):
                            quality["is_cached"] = True

                    for quality in video_info.get("audio_qualities", []):
                        quality_tag = f"audio_{quality.get('format', '')}"
                        if any(f.get("tag") == quality_tag for f in cached_formats):
                            quality["is_cached"] = True

            except Exception as format_error:
                logger.warning(f"Error checking cached formats for video {video_id}: {format_error}")
                # Continue without cached format information

            logger.debug(f"Retrieved cached video info for: {video_id}")
            return video_info

        except APIError as e:
            logger.error(f"Database error while fetching video {video_id}: {e}")
            raise ApiError(
                status_code=500,
                message=f"Database error: {str(e)}",
                error_code="DATABASE_ERROR"
            )
        except Exception as e:
            logger.error(f"Unexpected error while fetching video {video_id}: {e}")
            raise ApiError(
                status_code=500,
                message=f"Unexpected error: {str(e)}",
                error_code="UNEXPECTED_ERROR"
            )
            
    async def store_video_info(self, video_info: dict[str, any]) -> list[dict[str, any]]:
        """
        Store video information in the cache.
        
        Args:
            video_info: dictionary containing video metadata
            
        Returns:
            list containing the stored video information
            
        Raises:
            ApiError: If database error occurs
        """
        if not video_info or not isinstance(video_info, dict):
            raise ApiError(
                status_code=400,
                message="Valid video info is required",
                error_code="INVALID_VIDEO_INFO"
            )
            
        if not video_info.get("video_id"):
            raise ApiError(
                status_code=400,
                message="Video ID is required in video info",
                error_code="MISSING_VIDEO_ID"
            )
            
        try:
            response = await run_in_threadpool(
                self.cached_info.insert(video_info).execute
            )
            
            if not response.data:
                raise ApiError(
                    status_code=500,
                    message="Failed to store video information",
                    error_code="STORAGE_FAILED"
                )
                
            logger.info(f"Stored video info for video: {video_info['video_id']}")
            return response.data
            
        except APIError as e:
            logger.error(f"Database error while storing video info: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Database error: {str(e)}", 
                error_code="DATABASE_ERROR"
            )
        except Exception as e:
            logger.error(f"Unexpected error while storing video info: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Unexpected error: {str(e)}", 
                error_code="UNEXPECTED_ERROR"
            )
            
    async def get_cached_format(self, video_id: str, tag: str) -> dict[str, any]:
        """
        Retrieve a specific cached format and increment access count.
        
        Args:
            video_id: YouTube video ID
            tag: Format tag identifier
            
        Returns:
            dictionary containing cached format information, or None if not found
            
        Raises:
            ApiError: If database error occurs
        """
        if not video_id or not video_id.strip():
            raise ApiError(
                status_code=400,
                message="Video ID is required",
                error_code="INVALID_VIDEO_ID"
            )
            
        if not tag or not tag.strip():
            raise ApiError(
                status_code=400,
                message="Format tag is required",
                error_code="INVALID_TAG"
            )
            
        try:
            response = await run_in_threadpool(
                self.cached_formats.select("*").eq("video_id", video_id).eq("tag", tag).execute
            )
            
            if not response.data:
                logger.debug(f"No cached format found for video {video_id} with tag {tag}")
                return None
                
            cached_format = response.data[0]
            
            # Increment access count asynchronously
            try:
                current_count = cached_format.get("access_count", 0)
                await run_in_threadpool(
                    self.cached_formats.update({
                        "access_count": current_count + 1
                    }).eq("video_id", video_id).eq("tag", tag).execute
                )
                logger.debug(f"Incremented access count for format {tag} of video {video_id}")
            except Exception as count_error:
                logger.warning(f"Failed to increment access count for {video_id}/{tag}: {count_error}")
                # Continue without failing the main operation
            
            logger.debug(f"Retrieved cached format {tag} for video {video_id}")
            return cached_format
            
        except APIError as e:
            logger.error(f"Database error while fetching cached format {video_id}/{tag}: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Database error: {str(e)}", 
                error_code="DATABASE_ERROR"
            )
        except Exception as e:
            logger.error(f"Unexpected error while fetching cached format {video_id}/{tag}: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Unexpected error: {str(e)}", 
                error_code="UNEXPECTED_ERROR"
            )
        
    async def store_cached_format(self, format_info: dict[str, any]) -> list[dict[str, any]]:
        """
        Store cached format information.
        
        Args:
            format_info: dictionary containing format metadata
            
        Returns:
            list containing the stored format information
            
        Raises:
            ApiError: If database error occurs
        """
        if not format_info or not isinstance(format_info, dict):
            raise ApiError(
                status_code=400,
                message="Valid format info is required",
                error_code="INVALID_FORMAT_INFO"
            )
            
        required_fields = ["video_id", "tag", "path"]
        for field in required_fields:
            if not format_info.get(field):
                raise ApiError(
                    status_code=400,
                    message=f"{field} is required in format info",
                    error_code=f"MISSING_{field.upper()}"
                )
                
        try:
            # Add tracking metadata (only include fields that exist in schema)
            format_info_with_metadata = {
                **format_info,
                "access_count": 0
            }
            
            response = await run_in_threadpool(
                self.cached_formats.insert(format_info_with_metadata).execute
            )
            
            if not response.data:
                raise ApiError(
                    status_code=500,
                    message="Failed to store cached format",
                    error_code="STORAGE_FAILED"
                )
                
            logger.info(f"Stored cached format {format_info['tag']} for video {format_info['video_id']}")
            return response.data
            
        except APIError as e:
            logger.error(f"Database error while storing cached format: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Database error: {str(e)}", 
                error_code="DATABASE_ERROR"
            )
        except Exception as e:
            logger.error(f"Unexpected error while storing cached format: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Unexpected error: {str(e)}", 
                error_code="UNEXPECTED_ERROR"
            )
        
    async def remove_cached_format(self, video_id: str, tag: str) -> list[dict[str, any]]:
        """
        Remove a specific cached format.
        
        Args:
            video_id: YouTube video ID
            tag: Format tag identifier
            
        Returns:
            list containing the removed format information
            
        Raises:
            ApiError: If format not found or database error occurs
        """
        if not video_id or not video_id.strip():
            raise ApiError(
                status_code=400,
                message="Video ID is required",
                error_code="INVALID_VIDEO_ID"
            )
            
        if not tag or not tag.strip():
            raise ApiError(
                status_code=400,
                message="Format tag is required",
                error_code="INVALID_TAG"
            )
            
        try:
            response = await run_in_threadpool(
                self.cached_formats.delete().eq("video_id", video_id).eq("tag", tag).execute
            )
            
            if not response.data:
                logger.warning(f"Cached format not found for video {video_id} with tag {tag}")
                raise ApiError(
                    status_code=404, 
                    message="Cached format not found", 
                    error_code="FORMAT_NOT_FOUND"
                )
                
            logger.info(f"Removed cached format {tag} for video {video_id}")
            return response.data
            
        except APIError as e:
            logger.error(f"Database error while removing cached format {video_id}/{tag}: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Database error: {str(e)}", 
                error_code="DATABASE_ERROR"
            )
        except Exception as e:
            logger.error(f"Unexpected error while removing cached format {video_id}/{tag}: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Unexpected error: {str(e)}", 
                error_code="UNEXPECTED_ERROR"
            )
    
    async def get_playlist(self, playlist_id: str) -> dict[str, any]:
        """
        Retrieve cached playlist information.
        
        Args:
            playlist_id: YouTube playlist ID
            
        Returns:
            dictionary containing playlist information, or None if not found
            
        Raises:
            ApiError: If database error occurs
        """
        if not playlist_id or not playlist_id.strip():
            raise ApiError(
                status_code=400,
                message="Playlist ID is required",
                error_code="INVALID_PLAYlist_ID"
            )
            
        try:
            response = await run_in_threadpool(
                self.cached_playlist.select("*").eq("playlist_id", playlist_id).execute
            )
            
            if not response.data:
                logger.debug(f"No cached playlist info found for: {playlist_id}")
                return None
                
            logger.debug(f"Retrieved cached playlist info for: {playlist_id}")
            return response.data[0]
            
        except APIError as e:
            logger.error(f"Database error while fetching playlist {playlist_id}: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Database error: {str(e)}", 
                error_code="DATABASE_ERROR"
            )
        except Exception as e:
            logger.error(f"Unexpected error while fetching playlist {playlist_id}: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Unexpected error: {str(e)}", 
                error_code="UNEXPECTED_ERROR"
            )
        
    async def store_playlist_info(self, playlist_info: dict[str, any]) -> list[dict[str, any]]:
        """
        Store playlist information in the cache.
        
        Args:
            playlist_info: dictionary containing playlist metadata
            
        Returns:
            list containing the stored playlist information
            
        Raises:
            ApiError: If database error occurs
        """
        if not playlist_info or not isinstance(playlist_info, dict):
            raise ApiError(
                status_code=400,
                message="Valid playlist info is required",
                error_code="INVALID_PLAYlist_INFO"
            )
            
        if not playlist_info.get("playlist_id"):
            raise ApiError(
                status_code=400,
                message="Playlist ID is required in playlist info",
                error_code="MISSING_PLAYlist_ID"
            )
            
        try:
            response = await run_in_threadpool(
                self.cached_playlist.insert(playlist_info).execute
            )
            
            if not response.data:
                raise ApiError(
                    status_code=500,
                    message="Failed to store playlist information",
                    error_code="STORAGE_FAILED"
                )
                
            logger.info(f"Stored playlist info for: {playlist_info['playlist_id']}")
            return response.data
            
        except APIError as e:
            logger.error(f"Database error while storing playlist info: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Database error: {str(e)}", 
                error_code="DATABASE_ERROR"
            )
        except Exception as e:
            logger.error(f"Unexpected error while storing playlist info: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Unexpected error: {str(e)}", 
                error_code="UNEXPECTED_ERROR"
            )
        
    async def get_all_cached_videos(self) -> list[dict[str, any]]:
        """
        Retrieve all cached video formats.
        
        Returns:
            list of all cached video format dictionaries
            
        Raises:
            ApiError: If database error occurs
        """
        try:
            response = await run_in_threadpool(
                self.cached_formats.select("*").execute
            )
            
            cached_videos = response.data if response.data else []
            logger.debug(f"Retrieved {len(cached_videos)} cached video formats")
            return cached_videos
            
        except APIError as e:
            logger.error(f"Database error while fetching all cached videos: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Database error: {str(e)}", 
                error_code="DATABASE_ERROR"
            )
        except Exception as e:
            logger.error(f"Unexpected error while fetching all cached videos: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Unexpected error: {str(e)}", 
                error_code="UNEXPECTED_ERROR"
            )
        
    async def get_cache_stats(self) -> dict[str, int|float]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            dictionary containing cache statistics including counts and sizes
            
        Raises:
            ApiError: If database error occurs
        """
        try:
            videos = await self.get_all_cached_videos()

            stats = {
                "total_formats": len(videos),
                "total_size_bytes": 0,
                "audio_files": {"count": 0, "size_bytes": 0},
                "video_files": {"count": 0, "size_bytes": 0},
                "unique_videos": set(),
                "format_types": {}
            }
            
            for video in videos:
                file_size = video.get("filesize", 0)
                stats["total_size_bytes"] += file_size
                
                # Track unique videos
                if video.get("video_id"):
                    stats["unique_videos"].add(video["video_id"])
                
                # Categorize by codec
                if video.get("acodec") and video.get("acodec") != "none":
                    stats["audio_files"]["count"] += 1
                    stats["audio_files"]["size_bytes"] += file_size
                    
                if video.get("vcodec") and video.get("vcodec") != "none":
                    stats["video_files"]["count"] += 1
                    stats["video_files"]["size_bytes"] += file_size
                
                # Track format types
                tag = video.get("tag", "unknown")
                stats["format_types"][tag] = stats["format_types"].get(tag, 0) + 1

            # Convert to final format
            result = {
                "total_formats": stats["total_formats"],
                "unique_videos": len(stats["unique_videos"]),
                "total_audio_files": stats["audio_files"]["count"],
                "total_video_files": stats["video_files"]["count"],
                "total_size_bytes": stats["total_size_bytes"],
                "total_size_mb": round(stats["total_size_bytes"] / (1024 * 1024), 2),
                "total_size_gb": round(stats["total_size_bytes"] / (1024 * 1024 * 1024), 2),
                "audio_size_mb": round(stats["audio_files"]["size_bytes"] / (1024 * 1024), 2),
                "video_size_mb": round(stats["video_files"]["size_bytes"] / (1024 * 1024), 2),
                "format_breakdown": stats["format_types"]
            }
            
            logger.info(f"Generated cache stats: {result['unique_videos']} videos, {result['total_size_gb']}GB")
            return result
            
        except Exception as e:
            logger.error(f"Unexpected error while generating cache stats: {e}")
            raise ApiError(
                status_code=500, 
                message=f"Unexpected error: {str(e)}", 
                error_code="UNEXPECTED_ERROR"
            )

    async def cleanup_expired_cache(self, days_old: int = 30) -> dict[str, int]:
        """
        Clean up cache entries older than specified days.
        
        Args:
            days_old: Number of days after which cache entries are considered expired
            
        Returns:
            dictionary containing cleanup statistics
            
        Raises:
            ApiError: If database error occurs
        """
        if days_old <= 0:
            raise ApiError(
                status_code=400,
                message="Days must be positive",
                error_code="INVALID_DAYS"
            )
            
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            cutoff_iso = cutoff_date.isoformat()
            
            # Count items to be deleted by created_at or similar timestamp column
            # Note: Adjust column names based on your actual schema
            expired_formats = await run_in_threadpool(
                self.cached_formats.select("*").execute
            )
            
            expired_videos = await run_in_threadpool(
                self.cached_info.select("*").execute
            )
            
            expired_playlists = await run_in_threadpool(
                self.cached_playlist.select("*").execute
            )
            
            # For now, return empty stats since we need to check actual schema
            stats = {
                "expired_formats": 0,
                "expired_videos": 0,
                "expired_playlists": 0,
                "total_cleaned": 0
            }
            
            logger.info(f"Cache cleanup temporarily disabled - needs schema verification for timestamp columns")
            return stats
            
        except APIError as e:
            logger.error(f"Database error during cache cleanup: {e}")
            raise ApiError(
                status_code=500,
                message=f"Database error: {str(e)}",
                error_code="DATABASE_ERROR"
            )
        except Exception as e:
            logger.error(f"Unexpected error during cache cleanup: {e}")
            raise ApiError(
                status_code=500,
                message=f"Unexpected error: {str(e)}",
                error_code="UNEXPECTED_ERROR"
            )
        
# Global database manager instance
db = DatabaseManager()