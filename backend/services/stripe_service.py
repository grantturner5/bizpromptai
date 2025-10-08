import os
from typing import Dict, Any, Optional
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import PaymentTransaction, PaymentStatus
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StripePaymentService:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.api_key = os.getenv("STRIPE_API_KEY", "sk_test_emergent")
        
        # Initialize Stripe checkout
        self.stripe_checkout = StripeCheckout(
            api_key=self.api_key,
            webhook_url=""  # Will be set dynamically
        )
        
        # Product pricing
        self.products = {
            "presale": {
                "name": "BizPromptAI - 47 AI Business Prompts (Presale)",
                "amount": 37.00,
                "description": "Limited time presale pricing - 47 ChatGPT prompts to save 12+ hours weekly"
            },
            "regular": {
                "name": "BizPromptAI - 47 AI Business Prompts",
                "amount": 47.00,
                "description": "47 ChatGPT prompts to automate your business and save 12+ hours weekly"
            }
        }
    
    async def create_checkout_session(
        self,
        product_type: str,
        email: str,
        success_url: str,
        cancel_url: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create Stripe checkout session with security best practices"""
        
        if product_type not in self.products:
            raise ValueError(f"Invalid product type: {product_type}")
        
        product = self.products[product_type]
        
        # Create checkout session request
        checkout_request = CheckoutSessionRequest(
            amount=product["amount"],
            currency="usd",
            success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=cancel_url,
            metadata={
                "product_type": product_type,
                "email": email,
                "user_id": user_id or "",
                "product_name": product["name"]
            }
        )
        
        # Set webhook URL dynamically
        host_url = success_url.split('/success')[0]  # Extract base URL
        webhook_url = f"{host_url}/api/webhook/stripe"
        self.stripe_checkout.webhook_url = webhook_url
        
        try:
            # Create checkout session
            session = await self.stripe_checkout.create_checkout_session(checkout_request)
            
            # Store payment transaction in database
            transaction = PaymentTransaction(
                session_id=session.session_id,
                user_id=user_id,
                email=email,
                amount=product["amount"],
                currency="usd",
                product_name=product["name"],
                payment_status=PaymentStatus.PENDING,
                metadata={
                    "product_type": product_type,
                    "stripe_session_id": session.session_id
                }
            )
            
            # Insert into database
            await self.db.payment_transactions.insert_one(transaction.dict())
            
            logger.info(f"Created checkout session {session.session_id} for {email}")
            
            return {
                "checkout_url": session.url,
                "session_id": session.session_id,
                "amount": product["amount"],
                "product_name": product["name"]
            }
            
        except Exception as e:
            logger.error(f"Failed to create checkout session: {str(e)}")
            raise
    
    async def get_payment_status(self, session_id: str) -> Dict[str, Any]:
        """Get payment status from Stripe and update database"""
        
        try:
            # Get status from Stripe
            status = await self.stripe_checkout.get_checkout_status(session_id)
            
            # Update database record
            update_data = {
                "payment_status": status.payment_status,
                "stripe_payment_intent_id": status.metadata.get("payment_intent_id")
            }
            
            if status.payment_status == "paid":
                update_data["completed_at"] = datetime.utcnow()
                update_data["payment_status"] = PaymentStatus.COMPLETED
            elif status.status == "expired":
                update_data["payment_status"] = PaymentStatus.CANCELLED
            
            # Update transaction record
            await self.db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )
            
            # Get updated transaction
            transaction = await self.db.payment_transactions.find_one({"session_id": session_id})
            
            return {
                "session_id": session_id,
                "payment_status": status.payment_status,
                "stripe_status": status.status,
                "amount": status.amount_total / 100,  # Convert from cents
                "currency": status.currency,
                "transaction": transaction
            }
            
        except Exception as e:
            logger.error(f"Failed to get payment status for session {session_id}: {str(e)}")
            raise
    
    async def handle_webhook(self, request_body: bytes, signature: str) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        
        try:
            # Process webhook
            webhook_response = await self.stripe_checkout.handle_webhook(
                request_body, signature
            )
            
            # Update database based on webhook event
            if webhook_response.event_type == "checkout.session.completed":
                await self._handle_successful_payment(webhook_response)
            elif webhook_response.event_type == "checkout.session.expired":
                await self._handle_expired_payment(webhook_response)
            
            logger.info(f"Processed webhook event: {webhook_response.event_type}")
            return {"status": "processed", "event_type": webhook_response.event_type}
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {str(e)}")
            raise
    
    async def _handle_successful_payment(self, webhook_data) -> None:
        """Handle successful payment webhook"""
        
        session_id = webhook_data.session_id
        
        # Update transaction status
        await self.db.payment_transactions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "payment_status": PaymentStatus.COMPLETED,
                    "completed_at": datetime.utcnow()
                }
            }
        )
        
        # Get transaction details for additional processing
        transaction = await self.db.payment_transactions.find_one({"session_id": session_id})
        
        if transaction:
            # Add customer to premium users, send welcome email, etc.
            await self._process_successful_purchase(transaction)
    
    async def _handle_expired_payment(self, webhook_data) -> None:
        """Handle expired payment webhook"""
        
        session_id = webhook_data.session_id
        
        await self.db.payment_transactions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "payment_status": PaymentStatus.CANCELLED
                }
            }
        )
    
    async def _process_successful_purchase(self, transaction: Dict[str, Any]) -> None:
        """Process successful purchase - upgrade user, send emails, etc."""
        
        # Update user role to premium if user exists
        if transaction.get("user_id"):
            await self.db.users.update_one(
                {"id": transaction["user_id"]},
                {
                    "$set": {
                        "role": "premium_customer",
                        "purchase_date": datetime.utcnow()
                    }
                }
            )
        
        logger.info(f"Processed successful purchase for {transaction['email']}")
        
        # Here you would also:
        # - Send welcome email with prompt access
        # - Add to ConvertKit customer sequence
        # - Grant access to premium content