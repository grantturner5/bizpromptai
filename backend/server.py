from fastapi import FastAPI, APIRouter, HTTPException, Depends, BackgroundTasks, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr, validator
from typing import List, Optional, Dict, Any, Union
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import asyncio
import hmac
import hashlib
import json
from enum import Enum


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Business Automation Platform", description="Complete automation platform for digital product launches", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-this')
JWT_ALGORITHM = "HS256"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"

class CampaignType(str, Enum):
    WELCOME_SERIES = "welcome_series"
    PRODUCT_LAUNCH = "product_launch"
    RE_ENGAGEMENT = "re_engagement"
    LEAD_NURTURE = "lead_nurture"

class PromptCategory(str, Enum):
    EMAIL = "email"
    CONTENT = "content"
    RESEARCH = "research"
    MEETINGS = "meetings"
    SALES = "sales"

# Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER
    is_active: bool = True
    subscription_status: str = "free"  # free, paid, trial
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None
    
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class LeadMagnetSignup(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    lead_magnet_type: str = "ai_prompts_guide"
    source: str = "website"

class Prompt(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: PromptCategory
    prompt_text: str
    time_saved_minutes: int
    difficulty_level: str = "beginner"  # beginner, intermediate, advanced
    tags: List[str] = []
    is_premium: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Survey(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    questions: List[Dict[str, Any]]
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SurveyResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    survey_id: str
    user_email: EmailStr
    responses: Dict[str, Any]
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Purchase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_email: EmailStr
    product_name: str
    amount: float
    currency: str = "usd"
    stripe_session_id: str
    payment_status: str
    purchased_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Campaign(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    campaign_type: CampaignType
    description: str
    target_audience: str
    status: str = "active"  # active, paused, completed
    metrics: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Utility functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def get_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Initialize sample data
async def initialize_sample_data():
    """Initialize the database with sample prompts and admin user"""
    try:
        # Create admin user if not exists
        admin_exists = await db.users.find_one({"role": "admin"})
        if not admin_exists:
            admin_user = User(
                email="admin@bizpromptai.com",
                role=UserRole.ADMIN,
                first_name="Admin",
                last_name="User"
            )
            admin_doc = admin_user.model_dump()
            admin_doc['password'] = hash_password("admin123")
            admin_doc['created_at'] = admin_doc['created_at'].isoformat()
            await db.users.insert_one(admin_doc)
            logger.info("Admin user created")
        
        # Create sample prompts if collection is empty
        prompts_count = await db.prompts.count_documents({})
        if prompts_count == 0:
            sample_prompts = [
                Prompt(
                    title="Cold Email Generator",
                    description="Generate professional cold outreach emails that get responses",
                    category=PromptCategory.EMAIL,
                    prompt_text="Act as business development expert. Write professional cold outreach email with: Target Company [X], Target Person [Y], Your Background [Z], Value Proposition [A], Call to Action [B]. Conversational, professional, under 150 words, include subject line.",
                    time_saved_minutes=25,
                    tags=["outreach", "business development", "sales"]
                ),
                Prompt(
                    title="Meeting Agenda Creator",
                    description="Create structured meeting agendas that keep discussions focused",
                    category=PromptCategory.MEETINGS,
                    prompt_text="Create professional meeting agenda: Purpose [X], Duration [Y], Attendees [Z], Key Topics [A], Outcomes [B]. Format: Welcome (2 min), time-limited topics, actions, next steps.",
                    time_saved_minutes=20,
                    tags=["meetings", "productivity", "planning"]
                ),
                Prompt(
                    title="Project Status Report Generator",
                    description="Generate executive-level project status reports quickly",
                    category=PromptCategory.RESEARCH,
                    prompt_text="Create project status report: Project [X], Period [Y], Status [Z], Accomplishments [A], Milestones [B], Risks [C], Support [D]. Executive format, bullet points.",
                    time_saved_minutes=45,
                    tags=["reporting", "project management", "communication"]
                ),
                Prompt(
                    title="Competitor Analysis Framework",
                    description="Comprehensive competitor research and analysis template",
                    category=PromptCategory.RESEARCH,
                    prompt_text="Analyze competitor [X] in industry [Y], focus [Z]. Provide: overview, products/pricing, strengths/weaknesses, differentiation, opportunities. Strategic, actionable.",
                    time_saved_minutes=120,
                    tags=["research", "competitive analysis", "strategy"]
                ),
                Prompt(
                    title="LinkedIn Content Creator",
                    description="Generate engaging LinkedIn posts that drive engagement",
                    category=PromptCategory.CONTENT,
                    prompt_text="Write LinkedIn post: Topic [X], Audience [Y], Message [Z], Experience [A], CTA [B]. Hook start, 2-3 insights, credibility, engagement question. 300 words max.",
                    time_saved_minutes=30,
                    tags=["linkedin", "content marketing", "social media"]
                )
            ]
            
            for prompt in sample_prompts:
                doc = prompt.model_dump()
                doc['created_at'] = doc['created_at'].isoformat()
                await db.prompts.insert_one(doc)
            logger.info(f"Inserted {len(sample_prompts)} sample prompts")

        # Create sample survey if not exists
        survey_exists = await db.surveys.find_one({})
        if not survey_exists:
            sample_survey = Survey(
                title="Business Productivity Assessment",
                description="Help us understand your biggest productivity challenges",
                questions=[
                    {
                        "id": "q1",
                        "type": "multiple_choice",
                        "question": "Which business task costs you the most time?",
                        "options": ["Email writing", "Content creation", "Research", "Project management", "Meetings"]
                    },
                    {
                        "id": "q2", 
                        "type": "number",
                        "question": "How many hours per week do you spend on this task?"
                    },
                    {
                        "id": "q3",
                        "type": "multiple_choice", 
                        "question": "Would you pre-order our 47-prompt toolkit for $37?",
                        "options": ["Yes immediately", "Yes need more info", "Maybe", "No not interested", "No too expensive"]
                    },
                    {
                        "id": "q4",
                        "type": "text",
                        "question": "What's your biggest concern about AI automation? (Optional)"
                    }
                ]
            )
            doc = sample_survey.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            await db.surveys.insert_one(doc)
            logger.info("Sample survey created")
            
    except Exception as e:
        logger.error(f"Error initializing sample data: {e}")

# Authentication endpoints
@api_router.post("/auth/register")
async def register_user(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user = User(**user_data.model_dump(exclude={'password'}))
    user_doc = user.model_dump()
    user_doc['password'] = hash_password(user_data.password)
    user_doc['created_at'] = user_doc['created_at'].isoformat()
    
    await db.users.insert_one(user_doc)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.model_dump()
    }

@api_router.post("/auth/login")
async def login_user(login_data: UserLogin):
    user = await db.users.find_one({"email": login_data.email}, {"_id": 0})
    if not user or not verify_password(login_data.password, user.get('password', '')):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.get('is_active', True):
        raise HTTPException(status_code=401, detail="Account deactivated")
    
    # Update last login
    await db.users.update_one(
        {"email": login_data.email},
        {"$set": {"last_login": datetime.now(timezone.utc).isoformat()}}
    )
    
    access_token = create_access_token(data={"sub": user['email']})
    
    user_data = User(**user)
    return {
        "access_token": access_token,
        "token_type": "bearer", 
        "user": user_data.model_dump()
    }

@api_router.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    user_data = User(**current_user)
    return user_data.model_dump()

# Lead magnet endpoints
@api_router.post("/lead-magnet/signup")
async def lead_magnet_signup(signup_data: LeadMagnetSignup):
    """Handle lead magnet signup and trigger email automation"""
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": signup_data.email})
    
    if not existing_user:
        # Create new user account
        new_user = User(
            email=signup_data.email,
            first_name=signup_data.first_name,
            subscription_status="lead"
        )
        user_doc = new_user.model_dump()
        user_doc['created_at'] = user_doc['created_at'].isoformat()
        await db.users.insert_one(user_doc)
    
    # Store lead magnet signup
    lead_doc = signup_data.model_dump()
    lead_doc['id'] = str(uuid.uuid4())
    lead_doc['created_at'] = datetime.now(timezone.utc).isoformat()
    await db.lead_magnets.insert_one(lead_doc)
    
    # TODO: Integrate with ConvertKit to add to sequence
    # This would trigger the welcome email sequence
    
    return {
        "success": True,
        "message": "Successfully signed up for lead magnet",
        "lead_magnet_url": "/lead-magnet/download/ai-prompts-guide.pdf"
    }

# Prompt library endpoints
@api_router.get("/prompts", response_model=List[Prompt])
async def get_prompts(category: Optional[str] = None, is_premium: Optional[bool] = None):
    query = {}
    if category:
        query["category"] = category
    if is_premium is not None:
        query["is_premium"] = is_premium
    
    prompts = await db.prompts.find(query, {"_id": 0}).to_list(1000)
    
    # Convert ISO strings back to datetime
    for prompt in prompts:
        if isinstance(prompt['created_at'], str):
            prompt['created_at'] = datetime.fromisoformat(prompt['created_at'])
    
    return prompts

@api_router.get("/prompts/categories")
async def get_prompt_categories():
    """Get available prompt categories with counts"""
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    categories = await db.prompts.aggregate(pipeline).to_list(100)
    return [{"category": cat["_id"], "count": cat["count"]} for cat in categories]

@api_router.get("/prompts/premium")
async def get_premium_prompts(current_user: dict = Depends(get_current_user)):
    """Get premium prompts - requires authentication and paid subscription"""
    if current_user.get("subscription_status") not in ["paid", "trial"]:
        raise HTTPException(status_code=403, detail="Premium subscription required")
    
    prompts = await db.prompts.find({"is_premium": True}, {"_id": 0}).to_list(1000)
    
    for prompt in prompts:
        if isinstance(prompt['created_at'], str):
            prompt['created_at'] = datetime.fromisoformat(prompt['created_at'])
    
    return prompts

# Survey endpoints
@api_router.get("/surveys", response_model=List[Survey])
async def get_active_surveys():
    surveys = await db.surveys.find({"is_active": True}, {"_id": 0}).to_list(100)
    
    for survey in surveys:
        if isinstance(survey['created_at'], str):
            survey['created_at'] = datetime.fromisoformat(survey['created_at'])
    
    return surveys

@api_router.post("/surveys/{survey_id}/responses")
async def submit_survey_response(survey_id: str, responses: Dict[str, Any], user_email: EmailStr):
    # Validate survey exists
    survey = await db.surveys.find_one({"id": survey_id})
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    # Create response record
    response = SurveyResponse(
        survey_id=survey_id,
        user_email=user_email,
        responses=responses
    )
    
    doc = response.model_dump()
    doc['submitted_at'] = doc['submitted_at'].isoformat()
    await db.survey_responses.insert_one(doc)
    
    return {"success": True, "message": "Survey response submitted"}

# Admin endpoints
@api_router.get("/admin/dashboard")
async def get_admin_dashboard(admin_user: dict = Depends(get_admin_user)):
    """Get admin dashboard metrics"""
    
    # User metrics
    total_users = await db.users.count_documents({})
    paid_users = await db.users.count_documents({"subscription_status": "paid"})
    recent_signups = await db.users.count_documents({
        "created_at": {"$gte": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()}
    })
    
    # Lead magnet metrics
    total_leads = await db.lead_magnets.count_documents({})
    recent_leads = await db.lead_magnets.count_documents({
        "created_at": {"$gte": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()}
    })
    
    # Survey metrics
    total_responses = await db.survey_responses.count_documents({})
    
    # Revenue metrics (placeholder)
    total_revenue = 0.0  # Calculate from purchases collection
    
    return {
        "users": {
            "total": total_users,
            "paid": paid_users,
            "recent_signups": recent_signups,
            "conversion_rate": (paid_users / total_users * 100) if total_users > 0 else 0
        },
        "leads": {
            "total": total_leads,
            "recent": recent_leads
        },
        "surveys": {
            "total_responses": total_responses
        },
        "revenue": {
            "total": total_revenue,
            "monthly_target": 925.0
        }
    }

@api_router.get("/admin/users")
async def get_all_users(admin_user: dict = Depends(get_admin_user)):
    """Get all users for admin management"""
    users = await db.users.find({}, {"_id": 0, "password": 0}).to_list(1000)
    
    for user in users:
        if isinstance(user.get('created_at'), str):
            user['created_at'] = datetime.fromisoformat(user['created_at'])
        if isinstance(user.get('last_login'), str):
            user['last_login'] = datetime.fromisoformat(user['last_login'])
    
    return users

@api_router.get("/admin/survey-responses")
async def get_survey_responses(admin_user: dict = Depends(get_admin_user)):
    """Get all survey responses for analysis"""
    responses = await db.survey_responses.find({}, {"_id": 0}).to_list(1000)
    
    for response in responses:
        if isinstance(response.get('submitted_at'), str):
            response['submitted_at'] = datetime.fromisoformat(response['submitted_at'])
    
    return responses

# Payment endpoints (Stripe integration)
@api_router.post("/payments/create-checkout")
async def create_payment_checkout(request: Request):
    """Create Stripe checkout session for product purchase"""
    try:
        # Install emergentintegrations if not already installed
        try:
            from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
        except ImportError:
            raise HTTPException(status_code=500, detail="Payment service not available")
        
        # Get Stripe API key from environment
        stripe_api_key = os.environ.get('STRIPE_API_KEY')
        if not stripe_api_key:
            raise HTTPException(status_code=500, detail="Payment configuration missing")
        
        # Get host URL from request
        host_url = str(request.base_url)
        webhook_url = f"{host_url}api/payments/webhook"
        
        # Initialize Stripe checkout
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
        
        # Define product packages
        packages = {
            "ai_toolkit_presale": {
                "amount": 37.0,
                "currency": "usd",
                "name": "AI Business Automation Toolkit - Presale"
            },
            "ai_toolkit_regular": {
                "amount": 47.0,
                "currency": "usd", 
                "name": "AI Business Automation Toolkit - Regular"
            }
        }
        
        # For now, use presale package
        package = packages["ai_toolkit_presale"]
        
        # Create checkout session
        success_url = f"{host_url}success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{host_url}cancel"
        
        checkout_request = CheckoutSessionRequest(
            amount=package["amount"],
            currency=package["currency"],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "product": "ai_toolkit_presale",
                "source": "website"
            }
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Store payment transaction record
        transaction = {
            "id": str(uuid.uuid4()),
            "session_id": session.session_id,
            "amount": package["amount"],
            "currency": package["currency"],
            "product_name": package["name"],
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.payment_transactions.insert_one(transaction)
        
        return {"checkout_url": session.url, "session_id": session.session_id}
        
    except Exception as e:
        logger.error(f"Payment creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment session")

@api_router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str):
    """Check payment status for a session"""
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        
        stripe_api_key = os.environ.get('STRIPE_API_KEY')
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url="")
        
        status = await stripe_checkout.get_checkout_status(session_id)
        
        # Update local transaction record
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {
                "payment_status": status.payment_status,
                "status": status.status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # If payment successful, upgrade user subscription
        if status.payment_status == "paid":
            user_email = status.metadata.get("user_email")
            if user_email:
                await db.users.update_one(
                    {"email": user_email},
                    {"$set": {"subscription_status": "paid"}}
                )
        
        return status.model_dump()
        
    except Exception as e:
        logger.error(f"Payment status check failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to check payment status")

@api_router.post("/payments/webhook")
async def handle_stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        
        stripe_api_key = os.environ.get('STRIPE_API_KEY') 
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url="")
        
        webhook_request_body = await request.body()
        signature = request.headers.get("Stripe-Signature", "")
        
        webhook_response = await stripe_checkout.handle_webhook(webhook_request_body, signature)
        
        # Process webhook event
        if webhook_response.payment_status == "paid":
            # Update subscription status
            user_email = webhook_response.metadata.get("user_email")
            if user_email:
                await db.users.update_one(
                    {"email": user_email},
                    {"$set": {"subscription_status": "paid"}}
                )
        
        return JSONResponse(status_code=200, content={"received": True})
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        return JSONResponse(status_code=400, content={"error": str(e)})

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    await initialize_sample_data()
    logger.info("Application started successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()