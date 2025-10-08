from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    company: Optional[str] = None
    role: str = "customer"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class LeadMagnetSignup(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: Optional[str] = None
    magnet_type: Optional[str] = None
    source_page: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    convertkit_subscriber_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: Optional[str] = None
    email: EmailStr
    amount: float
    currency: str = "usd"
    product_name: str
    payment_status: PaymentStatus = PaymentStatus.PENDING
    stripe_payment_intent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class Prompt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    category: str
    tags: List[str] = Field(default_factory=list)
    is_premium: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Request/Response Models
class SubscribeRequest(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    magnet_type: Optional[str] = None
    source_page: Optional[str] = None

class PaymentCheckoutRequest(BaseModel):
    product_type: str  # "presale" or "regular"
    success_url: str
    cancel_url: str

class PaymentStatusResponse(BaseModel):
    session_id: str
    payment_status: str
    amount: Optional[float] = None
    currency: Optional[str] = None
    product_name: Optional[str] = None