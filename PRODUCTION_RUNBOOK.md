# BizPromptAI Production Runbook

## 🚀 Quick Start Guide for Live Operations

### Admin Access
- **Production URL:** `https://yourdomain.com`
- **Admin Dashboard:** `https://yourdomain.com/dashboard` (login with admin credentials)
- **Admin Email:** `admin@yourdomain.com`
- **Temp Password:** `[Set during deployment]`

### Key Integrations
- **Stripe:** Live payment processing enabled
- **ConvertKit:** Email automation sequences active
- **MongoDB:** Production database cluster
- **Google Forms:** Lead capture and survey system

## 📋 Daily Operations Checklist

### Morning Review (9 AM)
- [ ] Check overnight sales in Stripe dashboard
- [ ] Review admin analytics for visitor/lead/conversion metrics
- [ ] Monitor email delivery rates in ConvertKit
- [ ] Scan error logs for any system issues
- [ ] Verify all services are healthy (`/api/health` endpoint)

### Afternoon Check (2 PM)
- [ ] Review customer support emails
- [ ] Check for failed payment deliveries
- [ ] Monitor social media mentions and engagement
- [ ] Update content calendar if needed

### Evening Wrap-Up (6 PM)
- [ ] Review daily KPI email report
- [ ] Process any refund requests
- [ ] Update promotional campaigns if needed
- [ ] Plan next day's content and outreach

## 🛠️ Common Operations

### Processing Refunds
1. **Stripe Dashboard Method:**
   ```
   1. Login to Stripe Dashboard
   2. Go to Payments → Find transaction
   3. Click "Refund" → Enter amount → Confirm
   4. Customer receives automatic email notification
   ```

2. **Admin Dashboard Method:**
   ```
   1. Login to admin dashboard
   2. Go to Users → Find customer
   3. Click "Process Refund" 
   4. System automatically handles Stripe refund + access removal
   ```

### Resending Access Emails
```python
# Via Admin Dashboard:
1. Go to Users → Search customer email
2. Click "Resend Access" button
3. Customer receives new login credentials + download links

# Via Database (Emergency):
curl -X POST https://yourdomain.com/api/admin/resend-access \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "customer@example.com"}'
```

### Fixing Failed Deliveries
1. **Check delivery status:**
   ```bash
   # Check email delivery logs
   curl https://yourdomain.com/api/admin/delivery-status/customer@example.com
   ```

2. **Manual delivery:**
   ```bash
   # Trigger manual delivery
   curl -X POST https://yourdomain.com/api/admin/manual-delivery \
     -H "Authorization: Bearer ADMIN_TOKEN" \
     -d '{"email": "customer@example.com", "product": "presale_toolkit"}'
   ```

3. **Account access issues:**
   ```bash
   # Reset customer access
   curl -X POST https://yourdomain.com/api/admin/reset-access \
     -H "Authorization: Bearer ADMIN_TOKEN" \
     -d '{"email": "customer@example.com"}'
   ```

## 📄 Content Management

### Updating the 5-Prompt PDF
1. **File Location:** `/app/assets/5-prompt-guide.pdf`
2. **Update Process:**
   ```bash
   # Upload new PDF to storage
   aws s3 cp new-guide.pdf s3://bizpromptai-assets/5-prompt-guide.pdf
   
   # Clear CDN cache
   aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/5-prompt-guide.pdf"
   ```

### Adding New Prompts to Library
```python
# Via Admin Dashboard:
1. Login → Prompt Library → "Add New Prompt"
2. Fill in details:
   - Title, Description, Category
   - Prompt Text, Time Saved
   - Tags, Difficulty Level
   - Premium Status (true/false)

# Via API:
curl -X POST https://yourdomain.com/api/admin/prompts \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Prompt Title",
    "description": "Prompt description",
    "category": "email",
    "prompt_text": "Act as...",
    "time_saved_minutes": 30,
    "is_premium": true,
    "tags": ["automation", "email"]
  }'
```

### Updating Pricing
```python
# In Stripe Dashboard:
1. Products → AI Automation Toolkit
2. Add new price → Update amount
3. Update price_id in application:

# Via environment variable:
STRIPE_PRICE_ID_PRESALE=price_new_id

# Or via admin dashboard:
Settings → Pricing → Update Price ID
```

## 📧 Email Management

### ConvertKit Sequence Updates
1. **Login to ConvertKit:** `app.convertkit.com`
2. **Navigate to:** Automations → Sequences
3. **Update sequences:**
   - Lead Magnet Delivery (4 emails)
   - Presale Onboarding (7 emails)
   - High Engagement Nurture

### Emergency Email Send
```python
# Send announcement to all customers
curl -X POST https://yourdomain.com/api/admin/broadcast \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Important Update",
    "content": "Email content here",
    "audience": "presale_customers"  // or "all_subscribers"
  }'
```

## 🔧 Technical Troubleshooting

### Service Health Check
```bash
# Check all services
curl https://yourdomain.com/api/health

# Expected response:
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "stripe": "connected", 
    "convertkit": "connected"
  }
}
```

### Database Issues
```bash
# Check MongoDB connection
curl https://yourdomain.com/api/admin/db-status

# Restart application (if needed)
pm2 restart bizpromptai

# Check logs
pm2 logs bizpromptai
```

### Payment Issues
```bash
# Test Stripe connection
curl -X POST https://yourdomain.com/api/payments/test-connection

# Check recent payments
curl https://yourdomain.com/api/admin/recent-payments

# Webhook status
curl https://yourdomain.com/api/admin/webhook-status
```

## 📊 Analytics & Reporting

### Daily KPI Report (Auto-sent at 6 PM)
Contains:
- Visitors (last 24h/7d/30d)
- Leads generated
- Sales completed
- Revenue totals
- Conversion rates
- Top traffic sources

### Custom Reports
```bash
# Weekly sales report
curl https://yourdomain.com/api/admin/reports/weekly-sales

# Lead source analysis  
curl https://yourdomain.com/api/admin/reports/lead-sources

# Customer satisfaction metrics
curl https://yourdomain.com/api/admin/reports/satisfaction
```

### Google Analytics Integration
- **Property ID:** `GA_MEASUREMENT_ID`
- **Key Metrics:** Pageviews, Conversions, User Flow
- **Custom Events:** Lead Signup, Purchase, Content Download

## 🔒 Security & Backup

### Security Checklist
- [ ] SSL certificate valid and auto-renewing
- [ ] API keys rotated monthly
- [ ] Database backups automated daily
- [ ] Access logs monitored for suspicious activity
- [ ] Rate limiting active on all endpoints

### Backup Procedures
```bash
# Database backup
mongodump --uri="MONGO_URL" --out=/backups/$(date +%Y%m%d)

# File assets backup
aws s3 sync s3://bizpromptai-assets /backups/assets/

# Code backup (via Git)
git push origin production
```

### Emergency Contacts
- **Technical Issues:** Your development team
- **Payment Issues:** Stripe Support (support@stripe.com)
- **Email Issues:** ConvertKit Support
- **Domain/Hosting:** Your hosting provider

## 📱 Mobile App Considerations

### Progressive Web App (PWA)
- Installable on mobile devices
- Offline capability for downloaded prompts
- Push notifications for new content
- App-like experience on mobile

### Mobile Optimization
- Touch-friendly interface
- Fast loading times
- Responsive design
- Mobile payment optimization

## 🚀 Growth & Scaling

### When to Scale Up
- **Traffic:** > 10,000 visitors/day
- **Sales:** > 100 customers/day  
- **Database:** > 1M documents
- **Email list:** > 50,000 subscribers

### Scaling Checklist
- [ ] Upgrade server resources
- [ ] Implement Redis caching
- [ ] Set up CDN for static assets
- [ ] Add load balancing
- [ ] Optimize database queries
- [ ] Implement email rate limiting

## 📞 Support Scripts

### Customer Support Templates

**Access Issues:**
```
Hi [Name],

I see you're having trouble accessing your AI Automation Toolkit. I've just resent your access credentials to this email address.

You should receive:
1. Login credentials for your dashboard
2. Direct download link for the 5-prompt guide
3. Instructions for the private member group

If you don't see the email within 10 minutes, please check your spam folder.

Best regards,
[Your Name]
```

**Refund Request:**
```
Hi [Name],

I've processed your refund request for $37. You should see the credit appear on your card within 3-5 business days.

I've also removed access to the premium content as requested.

If you change your mind, you're always welcome back at the current pricing.

Best regards,
[Your Name]
```

**Technical Issues:**
```
Hi [Name],

Thank you for reporting this technical issue. I've escalated it to our development team and they're working on a fix.

As a temporary workaround: [provide specific steps]

I'll follow up within 24 hours with an update.

Best regards,
[Your Name]
```

This runbook covers all essential operations for managing the BizPromptAI platform in production. Keep it updated as new features are added or processes change.