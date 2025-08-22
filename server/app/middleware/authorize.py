import traceback
from fastapi.middleware import Middleware
from app.db.config import supabase
from fastapi import Request,Depends
from app.utils.api_error import ApiError
from app.logger import logger

def verify_token(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise ApiError(status_code=401, message="Authorization token is missing", error_code="UNAUTHORIZED")
    if not token.startswith("Bearer "):
        raise ApiError(status_code=401, message="Invalid token format", error_code="UNAUTHORIZED")
    token = token.split(" ")[1]
    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        if not user:
            raise ApiError(status_code=401, message="Invalid token", error_code="UNAUTHORIZED")
        
        # Get user details from the database
        user_data = supabase.table("users").select("*").eq("id", user.id).execute()
        if not user_data.data:
            raise ApiError(status_code=404, message="User not found", error_code="USER_NOT_FOUND")
        
        user_info = user_data.data[0]

        return user_info
        
    except Exception as e:
        logger.error(f"❌ Error verifying token: {e}")
        logger.error(traceback.format_exc())
        raise ApiError(status_code=401, message="Invalid token", error_code="UNAUTHORIZED")