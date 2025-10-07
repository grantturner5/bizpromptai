# BizPromptAI Production Deployment Guide

## 🚀 Production Deployment Checklist

### 1. Production Environment Setup

#### A. Server Deployment
```bash
# Deploy to your production server (DigitalOcean, AWS, Vercel, etc.)
# Example for DigitalOcean App Platform:

# 1. Create new app
# 2. Connect GitHub repository
# 3. Configure build settings:
#    - Build Command: npm run build (frontend)
#    - Run Command: pip install -r requirements.txt && uvicorn server:app --host 0.0.0.0 --port 8000 (backend)

# 4. Set environment variables (see section B)
```

#### B. Environment Variables (Production)
```env
# Backend (.env)
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/bizpromptai_prod
DB_NAME=bizpromptai_production
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
STRIPE_API_KEY=sk_live_YOUR_LIVE_STRIPE_KEY
JWT_SECRET=your_super_secure_jwt_secret_256_bit
CONVERTKIT_API_KEY=your_live_convertkit_api_key
CONVERTKIT_API_SECRET=your_convertkit_secret

# Frontend (.env)
REACT_APP_BACKEND_URL=https://api.yourdomain.com
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_PUBLISHABLE_KEY
```

#### C. Domain & SSL Setup
1. Point your domain to your server IP
2. Configure SSL certificate (Let's Encrypt or CloudFlare)
3. Update CORS origins in backend configuration

### 2. Stripe Live Mode Configuration

#### A. Create Live Product
```javascript
// Use Stripe Dashboard or API to create:
const product = {
  name: "AI Automation Toolkit Presale",
  description: "47 battle-tested AI prompts + bonuses",
  type: "good"
};

const price = {
  unit_amount: 3700, // $37.00
  currency: "usd",
  product: product_id
};
```

#### B. Update Payment Integration
```python
# In server.py, update payment configuration:
LIVE_PRODUCTS = {
    "ai_toolkit_presale": {
        "price_id": "price_live_YOUR_PRICE_ID",
        "amount": 37.00,
        "currency": "usd",
        "name": "AI Automation Toolkit - Presale"
    }
}
```

#### C. Test Transaction Process
1. Create test purchase for $1.00
2. Verify webhook delivery
3. Confirm email delivery
4. Test account access provisioning
5. Refund test transaction

### 3. Digital Delivery System

#### A. PDF Storage Setup
```python
# Add to server.py for secure file hosting
import boto3  # For AWS S3 or similar

class DigitalDelivery:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = 'bizpromptai-assets'
    
    def generate_presigned_url(self, file_key, expiration=3600):
        """Generate secure download link"""
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': file_key},
            ExpiresIn=expiration
        )
    
    def deliver_presale_content(self, user_email):
        """Auto-deliver content after purchase"""
        pdf_url = self.generate_presigned_url('5-prompt-guide.pdf')
        # Send email with download link
        # Update user account with presale access
```

#### B. Email Templates
```html
<!-- Purchase Confirmation Email Template -->
<h2>🎉 Welcome to the AI Automation Toolkit!</h2>
<p>Your presale purchase is confirmed. Here's your immediate access:</p>

<div style="background: #f8f9fa; padding: 20px; margin: 20px 0;">
  <h3>📥 Instant Downloads</h3>
  <p><strong>5-Prompt Quick Start Guide:</strong></p>
  <a href="{{PDF_DOWNLOAD_LINK}}" style="background: #ff6b35; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">
    Download Your Guide (PDF)
  </a>
</div>

<div style="background: #e8f5e8; padding: 20px; margin: 20px 0;">
  <h3>🔐 Your Account Access</h3>
  <p>Login to your exclusive presale area:</p>
  <p><strong>Email:</strong> {{USER_EMAIL}}</p>
  <p><strong>Access Link:</strong> <a href="{{LOGIN_URL}}">{{LOGIN_URL}}</a></p>
</div>

<div style="background: #fff3cd; padding: 20px; margin: 20px 0;">
  <h3>📅 What's Next?</h3>
  <p>✅ Full 47-prompt toolkit: <strong>Delivery within 7 days</strong></p>
  <p>✅ Private feedback group access</p>
  <p>✅ Lifetime updates</p>
  <p>✅ Bonus video tutorials</p>
</div>
```

### 4. ConvertKit Integration Setup

#### A. API Configuration
```python
# Add to server.py
import requests

class ConvertKitIntegration:
    def __init__(self):
        self.api_key = os.getenv('CONVERTKIT_API_KEY')
        self.api_secret = os.getenv('CONVERTKIT_API_SECRET')
        self.base_url = "https://api.convertkit.com/v3"
    
    def add_subscriber_to_sequence(self, email, sequence_id, first_name=None):
        """Add subscriber to ConvertKit sequence"""
        url = f"{self.base_url}/sequences/{sequence_id}/subscribe"
        data = {
            "api_key": self.api_key,
            "email": email,
            "first_name": first_name
        }
        return requests.post(url, data=data)
    
    def add_tag_to_subscriber(self, email, tag_id):
        """Add tag to subscriber"""
        url = f"{self.base_url}/tags/{tag_id}/subscribe"
        data = {
            "api_key": self.api_key,
            "email": email
        }
        return requests.post(url, data=data)
```

#### B. Sequence Configuration IDs
```python
# ConvertKit Configuration
CONVERTKIT_CONFIG = {
    "sequences": {
        "lead_magnet_delivery": "SEQUENCE_ID_1",  # Replace with actual ID
        "presale_onboarding": "SEQUENCE_ID_2"     # Replace with actual ID
    },
    "tags": {
        "lead_magnet": "TAG_ID_1",               # Replace with actual ID
        "presale_customer": "TAG_ID_2"           # Replace with actual ID
    },
    "forms": {
        "lead_magnet_form": "FORM_ID_1"          # Replace with actual ID
    }
}
```

### 5. Google Forms Integration

#### A. Form Setup
1. Create form with questions:
   - Which business task costs most time? (Multiple choice)
   - Hours per week on this task? (Short answer)
   - Would you pre-order 47-prompt toolkit for $37? (Multiple choice)
   - Biggest AI concern? (Optional text)

2. Add hidden fields for UTM tracking:
   - utm_source
   - utm_medium
   - utm_campaign
   - timestamp

#### B. Form Response Webhook
```python
# Add webhook endpoint for Google Forms
@app.post("/api/webhooks/google-form")
async def handle_google_form_submission(request: Request):
    """Process Google Form submissions"""
    data = await request.json()
    
    # Extract form data
    email = data.get('email')
    responses = data.get('responses')
    utm_data = data.get('utm', {})
    
    # Save to database
    survey_response = SurveyResponse(
        survey_id="productivity_assessment",
        user_email=email,
        responses=responses,
        utm_data=utm_data
    )
    
    # Add to ConvertKit
    convertkit = ConvertKitIntegration()
    convertkit.add_subscriber_to_sequence(
        email, 
        CONVERTKIT_CONFIG["sequences"]["lead_magnet_delivery"]
    )
    convertkit.add_tag_to_subscriber(
        email,
        CONVERTKIT_CONFIG["tags"]["lead_magnet"]
    )
    
    return {"status": "success"}
```

### 6. Analytics Dashboard Setup

#### A. Enhanced Admin Dashboard
```python
# Add advanced analytics to admin dashboard
@app.get("/api/admin/analytics")
async def get_advanced_analytics(admin_user: dict = Depends(get_admin_user)):
    """Get comprehensive business analytics"""
    
    # Date ranges
    last_7_days = datetime.now(timezone.utc) - timedelta(days=7)
    last_30_days = datetime.now(timezone.utc) - timedelta(days=30)
    
    # Visitor metrics (implement with Google Analytics API)
    visitors = {
        "last_7_days": await get_visitor_count(last_7_days),
        "last_30_days": await get_visitor_count(last_30_days)
    }
    
    # Lead metrics
    leads = {
        "last_7_days": await db.lead_magnets.count_documents({
            "created_at": {"$gte": last_7_days.isoformat()}
        }),
        "last_30_days": await db.lead_magnets.count_documents({
            "created_at": {"$gte": last_30_days.isoformat()}
        })
    }
    
    # Sales metrics
    sales = {
        "last_7_days": await db.payment_transactions.count_documents({
            "created_at": {"$gte": last_7_days.isoformat()},
            "payment_status": "paid"
        }),
        "last_30_days": await db.payment_transactions.count_documents({
            "created_at": {"$gte": last_30_days.isoformat()},
            "payment_status": "paid"
        })
    }
    
    # Conversion funnel
    funnel = {
        "visitors_to_leads": (leads["last_7_days"] / visitors["last_7_days"]) * 100 if visitors["last_7_days"] > 0 else 0,
        "leads_to_customers": (sales["last_7_days"] / leads["last_7_days"]) * 100 if leads["last_7_days"] > 0 else 0
    }
    
    return {
        "visitors": visitors,
        "leads": leads,
        "sales": sales,
        "funnel": funnel,
        "revenue": {
            "last_7_days": sales["last_7_days"] * 37,
            "last_30_days": sales["last_30_days"] * 37
        }
    }
```

### 7. Production Security Checklist

- [ ] SSL certificate installed and configured
- [ ] Strong JWT secret (256-bit minimum)
- [ ] Database credentials secured
- [ ] API keys stored in environment variables
- [ ] CORS properly configured for production domain
- [ ] Rate limiting enabled on API endpoints
- [ ] Input validation on all forms
- [ ] SQL injection prevention (using parameterized queries)
- [ ] File upload security (if applicable)
- [ ] Error messages don't expose sensitive information

### 8. Monitoring & Maintenance

#### A. Health Check Endpoint
```python
@app.get("/api/health")
async def health_check():
    """Health check for monitoring"""
    try:
        # Check database connection
        await db.list_collection_names()
        
        # Check external services
        stripe_health = test_stripe_connection()
        convertkit_health = test_convertkit_connection()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {
                "database": "connected",
                "stripe": "connected" if stripe_health else "error",
                "convertkit": "connected" if convertkit_health else "error"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
```

#### B. Daily KPI Email
```python
import schedule
import smtplib
from email.mime.text import MimeText

def send_daily_kpi_report():
    """Send daily KPI report at 6 PM"""
    analytics = get_daily_analytics()
    
    email_content = f"""
    📊 BizPromptAI Daily Report - {datetime.now().strftime('%Y-%m-%d')}
    
    🎯 Key Metrics:
    • Visitors: {analytics['visitors']}
    • Leads: {analytics['leads']} 
    • Sales: {analytics['sales']}
    • Revenue: ${analytics['revenue']}
    
    📈 Conversion Rates:
    • Visitor → Lead: {analytics['visitor_to_lead_rate']:.1f}%
    • Lead → Customer: {analytics['lead_to_customer_rate']:.1f}%
    
    🔥 Top Performing:
    • Traffic Source: {analytics['top_traffic_source']}
    • Lead Magnet: {analytics['top_lead_magnet']}
    
    Login to view detailed analytics: https://yourdomain.com/dashboard
    """
    
    # Send email (implement with your preferred email service)
    send_email("admin@yourdomain.com", "Daily KPI Report", email_content)

# Schedule daily report
schedule.every().day.at("18:00").do(send_daily_kpi_report)
```

## 🔧 Next Steps for Live Deployment

1. **Set up your production server** (DigitalOcean, AWS, Vercel, etc.)
2. **Configure domain and SSL certificate**
3. **Set up MongoDB Atlas production cluster**
4. **Create live Stripe account and products**
5. **Set up ConvertKit account and sequences**
6. **Configure Google Forms and webhooks**
7. **Deploy application with production environment variables**
8. **Run end-to-end testing**
9. **Set up monitoring and alerts**

## 📞 Support & Troubleshooting

### Common Issues:
- **Payment not processing**: Check Stripe webhook configuration
- **Emails not sending**: Verify ConvertKit API credentials  
- **Access not granted**: Check user role assignment in database
- **Form submissions failing**: Verify webhook endpoints are accessible

### Monitoring Commands:
```bash
# Check application logs
docker logs bizpromptai-backend

# Monitor database connections
mongo --eval "db.serverStatus().connections"

# Test API endpoints
curl -X GET https://yourdomain.com/api/health

# Check SSL certificate
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

This guide provides the complete blueprint for production deployment. Each section includes specific code, configurations, and step-by-step instructions for implementing in your live environment.