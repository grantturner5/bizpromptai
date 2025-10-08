import os
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime, timezone
import bcrypt
import jwt
from typing import Optional, Dict, Any
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import models and services
from models import (
    User, LeadMagnetSignup, PaymentTransaction, Prompt,
    SubscribeRequest, PaymentCheckoutRequest, PaymentStatusResponse
)
from services.stripe_service import StripePaymentService
from services.convertkit_service import ConvertKitService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
client: AsyncIOMotorClient = None
database: AsyncIOMotorDatabase = None

# Services
stripe_service: StripePaymentService = None
convertkit_service: ConvertKitService = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global client, database, stripe_service, convertkit_service
    
    # Connect to MongoDB
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    database = client.bizpromptai
    
    # Initialize services
    stripe_service = StripePaymentService(database)
    convertkit_service = ConvertKitService()
    
    # Initialize sample data
    await initialize_sample_data()
    
    logger.info("BizPromptAI backend started successfully")
    yield
    
    # Shutdown
    if client:
        client.close()

app = FastAPI(
    title="BizPromptAI Backend",
    description="Backend API for BizPromptAI - AI Business Prompt Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def initialize_sample_data():
    """Initialize sample data for development"""
    try:
        # Check if admin user exists
        admin_user = await database.users.find_one({"email": "admin@bizpromptai.com"})
        if not admin_user:
            # Create admin user
            hashed_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
            admin = User(
                email="admin@bizpromptai.com",
                name="Admin User",
                role="admin"
            )
            await database.users.insert_one({
                **admin.dict(),
                "password": hashed_password.decode('utf-8')
            })
            logger.info("Created admin user")
        
        # Check if prompts exist
        prompts_count = await database.prompts.count_documents({})
        if prompts_count == 0:
            # Create sample prompts
            sample_prompts = [
                Prompt(
                    title="Email Marketing Campaign Creator",
                    content="Create a comprehensive email marketing campaign for [PRODUCT/SERVICE] targeting [TARGET AUDIENCE]. Include subject lines, email sequences, and call-to-action strategies.",
                    category="Marketing",
                    tags=["email", "marketing", "campaigns"]
                ),
                Prompt(
                    title="Social Media Content Planner",
                    content="Generate a 30-day social media content calendar for [BUSINESS TYPE] focusing on [GOALS]. Include post ideas, hashtags, and engagement strategies.",
                    category="Social Media",
                    tags=["social media", "content", "planning"]
                ),
                Prompt(
                    title="Business Process Optimizer",
                    content="Analyze and optimize the [BUSINESS PROCESS] for [COMPANY]. Identify bottlenecks, suggest improvements, and create implementation timeline.",
                    category="Operations",
                    tags=["process", "optimization", "efficiency"]
                )
            ]
            
            for prompt in sample_prompts:
                await database.prompts.insert_one(prompt.dict())
            
            logger.info("Created sample prompts")
            
    except Exception as e:
        logger.error(f"Failed to initialize sample data: {str(e)}")

# Authentication endpoints
@app.post("/api/auth/register")
async def register(user_data: dict):
    """Register new user"""
    try:
        # Check if user exists
        existing_user = await database.users.find_one({"email": user_data["email"]})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        hashed_password = bcrypt.hashpw(user_data["password"].encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user = User(
            email=user_data["email"],
            name=user_data["name"],
            company=user_data.get("company"),
            role="customer"
        )
        
        # Insert user
        await database.users.insert_one({
            **user.dict(),
            "password": hashed_password.decode('utf-8')
        })
        
        # Generate JWT token
        token_data = {"user_id": user.id, "email": user.email}
        token = jwt.encode(token_data, os.getenv("SECRET_KEY", "secret"), algorithm="HS256")
        
        # Add to ConvertKit welcome sequence
        if convertkit_service:
            await convertkit_service.add_subscriber(
                email=user.email,
                first_name=user.name,
                tags=["paying_customer"]
            )
            await convertkit_service.add_to_sequence(
                email=user.email,
                sequence_name="welcome"
            )
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/auth/login")
async def login(credentials: dict):
    """Login user"""
    try:
        # Find user
        user_data = await database.users.find_one({"email": credentials["email"]})
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check password
        if not bcrypt.checkpw(credentials["password"].encode('utf-8'), user_data["password"].encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Generate JWT token
        token_data = {"user_id": user_data["id"], "email": user_data["email"]}
        token = jwt.encode(token_data, os.getenv("SECRET_KEY", "secret"), algorithm="HS256")
        
        # Remove password from response
        user_data.pop("password", None)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

# Lead magnet endpoints
@app.post("/api/lead-magnet")
async def lead_magnet_signup(
    request: SubscribeRequest,
    background_tasks: BackgroundTasks
):
    """Handle lead magnet signup"""
    try:
        # Store lead in database
        lead = LeadMagnetSignup(
            email=request.email,
            name=request.first_name,
            magnet_type=request.magnet_type,
            source_page=request.source_page
        )
        
        await database.lead_magnets.insert_one(lead.dict())
        
        # Process ConvertKit signup in background
        if convertkit_service:
            background_tasks.add_task(
                convertkit_service.process_lead_magnet_signup,
                request.email,
                request.first_name,
                request.magnet_type or "general"
            )
        
        return {
            "success": True,
            "message": "Successfully subscribed! Check your email for your free prompts.",
            "lead_id": lead.id
        }
        
    except Exception as e:
        logger.error(f"Lead magnet signup failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Signup failed")

# Payment endpoints
@app.post("/api/payments/create-checkout")
async def create_payment_checkout(
    request: PaymentCheckoutRequest,
    user_request: Request
):
    """Create Stripe checkout session"""
    try:
        if not stripe_service:
            raise HTTPException(status_code=500, detail="Payment service not available")
        
        # Get user email from request (could be from auth or form)
        email = getattr(user_request.state, 'user_email', 'customer@bizpromptai.com')
        user_id = getattr(user_request.state, 'user_id', None)
        
        # Create checkout session
        result = await stripe_service.create_checkout_session(
            product_type=request.product_type,
            email=email,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            user_id=user_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Checkout creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Payment setup failed")

@app.get("/api/payments/status/{session_id}")
async def get_payment_status(session_id: str):
    """Get payment status for session"""
    try:
        if not stripe_service:
            raise HTTPException(status_code=500, detail="Payment service not available")
        
        result = await stripe_service.get_payment_status(session_id)
        
        # If payment completed, process customer onboarding
        if result["payment_status"] == "paid" and convertkit_service:
            transaction = result.get("transaction")
            if transaction:
                await convertkit_service.process_customer_purchase(
                    email=transaction["email"],
                    product_type=transaction.get("metadata", {}).get("product_type", "regular"),
                    amount=transaction["amount"]
                )
        
        return PaymentStatusResponse(**result).dict()
        
    except Exception as e:
        logger.error(f"Payment status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Status check failed")

@app.post("/api/webhook/stripe")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Handle Stripe webhook events"""
    try:
        if not stripe_service:
            raise HTTPException(status_code=500, detail="Payment service not available")
        
        # Get raw body and signature
        body = await request.body()
        signature = request.headers.get("stripe-signature", "")
        
        # Process webhook in background
        background_tasks.add_task(
            stripe_service.handle_webhook,
            body,
            signature
        )
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Stripe webhook failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

# Prompt endpoints
@app.get("/api/prompts")
async def get_prompts(category: Optional[str] = None):
    """Get available prompts"""
    try:
        query = {"category": category} if category else {}
        prompts = await database.prompts.find(query).to_list(length=None)
        return {"prompts": prompts}
        
    except Exception as e:
        logger.error(f"Failed to fetch prompts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch prompts")

# Admin endpoints
@app.get("/api/admin/dashboard")
async def admin_dashboard():
    """Get admin dashboard data"""
    try:
        # Get counts
        users_count = await database.users.count_documents({})
        leads_count = await database.lead_magnets.count_documents({})
        transactions_count = await database.payment_transactions.count_documents({})
        
        # Get recent activity
        recent_users = await database.users.find().sort("created_at", -1).limit(5).to_list(length=5)
        recent_leads = await database.lead_magnets.find().sort("created_at", -1).limit(5).to_list(length=5)
        
        return {
            "stats": {
                "total_users": users_count,
                "total_leads": leads_count,
                "total_transactions": transactions_count
            },
            "recent_activity": {
                "users": recent_users,
                "leads": recent_leads
            }
        }
        
    except Exception as e:
        logger.error(f"Admin dashboard failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Dashboard data unavailable")

# Health check
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "database": "connected" if database else "disconnected",
            "stripe": "configured" if stripe_service else "not configured",
            "convertkit": "configured" if convertkit_service and convertkit_service.api_key else "not configured"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )