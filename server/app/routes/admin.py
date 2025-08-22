from urllib import response
from fastapi import APIRouter, Depends,Request, WebSocket, WebSocketDisconnect
from app.utils.async_handler import async_handler
from app.db.database_manager import db
from app.middleware.authorize import verify_token
from app.utils.api_error import ApiError
from pydantic import BaseModel,Field
from datetime import datetime
from app.utils import download_manager
from app.utils.admin_websocket_manager import manager

router = APIRouter()

class PlanResponse(BaseModel):
    id: str
    max_requests: int
    validity_days: int | None = 30
    max_video_quality: str
    max_audio_quality: str
    playlist_support: bool=False
    subtitle_support: bool=False
    audio_only_support: bool=False
    audio_language_support: bool=False
    subtitle_language_support: bool=False
    price_inr: int  # in paise
    audio_qualities: list[str]=[]
    video_qualities: list[str]=[]

@router.get("/plans", response_model=list[PlanResponse])
@async_handler
async def get_plans(user=Depends(verify_token)):
    """
    Get all pricing plans.
    """
    if not user or not user.get("is_admin", False):
        raise ApiError(status_code=401, message="Unauthorized", error_code="UNAUTHORIZED")

    return await db.get_plans()

@router.get("/plans/{plan_id}", response_model=PlanResponse)
@async_handler
async def get_plan(plan_id: str, user=Depends(verify_token)):
    """
    Get a specific pricing plan.
    """
    if not user or not user.get("is_admin", False):
        raise ApiError(status_code=401, message="Unauthorized", error_code="UNAUTHORIZED")
    plan = await db.get_plan(plan_id)
    return plan

class UserPlanResponse(BaseModel):
    id: str
    user_id: str
    plan_id: str
    valid_till: datetime | None = None
    created_at: datetime
    requests_made: int
    validity_days: int | None = 30
    max_requests: int
    validity_days: int | None = 30
    max_video_quality: str
    max_audio_quality: str
    playlist_support: bool=False
    subtitle_support: bool=False
    audio_only_support: bool=False
    audio_language_support: bool=False
    subtitle_language_support: bool=False
    price_inr: int  # in paise
    audio_qualities: list[str]=[]
    video_qualities: list[str]=[]

@router.get("/{user_id}/plans", response_model=list[UserPlanResponse])
@async_handler
async def get_user_plans(user_id: str, user=Depends(verify_token)):
    if not user or not user.get("is_admin", False):
        raise ApiError(status_code=401, message="Unauthorized", error_code="UNAUTHORIZED")
    
    if not user_id:
        raise ApiError(status_code=400, message="User ID is required", error_code="BAD_REQUEST")

    plans = await db.get_user_plans(user_id)
    return plans

@router.get("/{user_id}/plans/{plan_id}", response_model=UserPlanResponse)
@async_handler
async def get_user_plan(user_id: str, plan_id: str, user=Depends(verify_token)):
    if not user or not user.get("is_admin", False):
        raise ApiError(status_code=401, message="Unauthorized", error_code="UNAUTHORIZED")

    if not user_id:
        raise ApiError(status_code=400, message="User ID is required", error_code="BAD_REQUEST")

    if not plan_id:
        raise ApiError(status_code=400, message="Plan ID is required", error_code="BAD_REQUEST")

    plan = await db.get_user_plan(plan_id)
    print("Returned plan:", plan)
    return plan

class AddUserPlanRequest(BaseModel):
    plan_id: str

@router.post("/{user_id}/plans", response_model=UserPlanResponse)
@async_handler
async def add_user_plan(
    user_id: str,
    request: AddUserPlanRequest,
    user=Depends(verify_token)
):
    """Add a plan to a user."""
    if not user or not user.get("is_admin", False):
        raise ApiError(status_code=401, message="Unauthorized", error_code="UNAUTHORIZED")
    plan = await db.add_user_plan(user_id, request.plan_id)
    return plan

class RemoveUserPlanRequest(BaseModel):
    plan_id: str

@router.delete("/{user_id}/plans", response_model=UserPlanResponse)
@async_handler
async def remove_user_plan(
    user_id: str,
    request: RemoveUserPlanRequest,
    user=Depends(verify_token)
):
    """Remove a plan from a user."""
    if not user or not user.get("is_admin", False):
        raise ApiError(status_code=401, message="Unauthorized", error_code="UNAUTHORIZED")
    result = await db.remove_user_plan(request.plan_id)
    return result

@router.get("/test")
@async_handler
async def test_endpoint():
    await download_manager.main()
    
    return "Success"

@router.websocket("/ws/logs")
@async_handler
async def websocket_endpoint(websocket: WebSocket,user=Depends(verify_token)):
    await manager.connect(websocket)
    try:
        # Keep the connection alive, listening for potential messages (though we don't expect any)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)