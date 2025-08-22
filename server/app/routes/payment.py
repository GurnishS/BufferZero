from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from app.utils.api_error import ApiError
from app.db.database_manager import db
from app.middleware.authorize import verify_token
from app.config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
from app.logger import logger
import razorpay
import json
import os
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter()

# Initialize Razorpay client
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@router.post("/create-payment")
async def create_payment(request: Request, user: dict = Depends(verify_token)):
    """
    Create a payment order.
    """
    try:
        user_id = user.get("id")
        data = await request.json()
        plan_id = data.get("plan_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized: User ID not found")
        
        if not plan_id:
            raise HTTPException(status_code=400, detail="Plan ID is required")

        plan = await db.get_plan(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")

        # Create razorpay order
        # Calculate total amount including 18% GST
        base_amount = plan['price_inr']
        gst_amount = int(round(base_amount * 0.18))
        total_amount = base_amount + gst_amount

        razorpay_order = client.order.create({
            "amount": total_amount,  # Amount should be in paise (including GST)
            "currency": "INR",
            "payment_capture": 1
        })

        # Store payment record in database
        order = await db.create_payment(user_id, razorpay_order['id'], plan)

        return {
            "order_id": order['razorpay_order_id'],
            "amount": total_amount,
            "currency": "INR",
            "key_id": RAZORPAY_KEY_ID
        }

    except HTTPException:
        raise
    except ApiError as e:
        logger.error(f"API error creating payment: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/verify-payment")
async def verify_payment(request: Request, user: dict = Depends(verify_token)):
    """
    Verify a Razorpay payment and activate user plan.
    """
    try:
        user_id = user.get("id")
        data = await request.json()
        
        payment_id = data.get("payment_id")
        order_id = data.get("order_id") 
        signature = data.get("signature")
        plan_id = data.get("plan_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized: User ID not found")
        
        if not all([payment_id, order_id, signature, plan_id]):
            missing_fields = []
            if not payment_id: missing_fields.append("payment_id")
            if not order_id: missing_fields.append("order_id")
            if not signature: missing_fields.append("signature")
            if not plan_id: missing_fields.append("plan_id")
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )

        # 1. Verify Razorpay signature
        import hmac
        import hashlib
        
        # Get Razorpay key secret from environment
        key_secret = RAZORPAY_KEY_SECRET
        
        # Create signature verification string
        msg = f"{order_id}|{payment_id}"
        expected_signature = hmac.new(
            key_secret.encode(), 
            msg.encode(), 
            hashlib.sha256
        ).hexdigest()
        
        # Verify signature
        if not hmac.compare_digest(expected_signature, signature):
            logger.error(f"Payment signature verification failed for payment_id: {payment_id}")
            # Update payment status as failed
            try:
                await db.update_payment_status_failed(user_id, order_id, payment_id, signature)
            except Exception as db_error:
                logger.error(f"Failed to update payment status to failed: {db_error}")
            raise HTTPException(status_code=400, detail="Invalid payment signature")

        # 2. Fetch payment details from Razorpay to double-check
        try:
            payment_details = client.payment.fetch(payment_id)
        except Exception as razorpay_error:
            logger.error(f"Failed to fetch payment details from Razorpay: {razorpay_error}")
            raise HTTPException(status_code=400, detail="Failed to verify payment with Razorpay")
        
        if payment_details['status'] != 'captured':
            logger.error(f"Payment not captured. Status: {payment_details['status']}")
            await db.update_payment_status_failed(user_id, order_id, payment_id, signature)
            raise HTTPException(status_code=400, detail=f"Payment not captured. Status: {payment_details['status']}")
            
        if payment_details['order_id'] != order_id:
            logger.error(f"Order ID mismatch. Expected: {order_id}, Got: {payment_details['order_id']}")
            await db.update_payment_status_failed(user_id, order_id, payment_id, signature)
            raise HTTPException(status_code=400, detail="Order ID mismatch")

        # 3. Get plan details
        plan = await db.get_plan(plan_id)
        if not plan:
            logger.error(f"Plan not found: {plan_id}")
            await db.update_payment_status_failed(user_id, order_id, payment_id, signature)
            raise HTTPException(status_code=404, detail="Plan not found")

        # 4. Verify payment amount matches plan price (both should be in paise)
        # Calculate expected total amount (plan price + 18% GST), rounded to nearest integer
        base_amount = plan['price_inr']
        gst_amount = int(round(base_amount * 0.18))
        expected_total = base_amount + gst_amount

        if abs(payment_details['amount'] - expected_total) > 2:  # Allow small rounding error
            logger.error(f"Payment amount mismatch. Expected: {expected_total}, Got: {payment_details['amount']}")
            await db.update_payment_status_failed(user_id, order_id, payment_id, signature)
            raise HTTPException(status_code=400, detail="Payment amount mismatch (GST included)")

        # 5. Update payment status in database and create user plan
        try:
            created_plan = await db.update_payment_status_completed(
                user_id=user_id,
                order_id=order_id,
                payment_id=payment_id,
                signature=signature,
                plan=plan
            )
        except Exception as db_error:
            logger.error(f"Failed to update payment status to completed: {db_error}")
            raise HTTPException(status_code=500, detail="Failed to activate plan")

        logger.info(f"Payment verified and plan activated for user: {user_id}, plan: {plan_id}")
        
        return {
            "success": True,
            "message": "Payment verified successfully",
            "user_plan_id": created_plan['id'],
            "plan_id": plan_id,
            "plan_name": plan.get('name', plan['id']),
            "valid_until": created_plan.get('valid_till')
        }

    except HTTPException:
        raise
    except ApiError as e:
        logger.error(f"API error verifying payment: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error verifying payment: {e}")
        raise HTTPException(status_code=500, detail="Payment verification failed")
