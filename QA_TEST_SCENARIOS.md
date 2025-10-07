# Production QA Test Scenarios

## 🧪 End-to-End Test Scenarios

### Test 1: Lead Magnet Flow
**Objective:** Verify complete lead capture and email delivery

**Steps:**
1. Visit landing page at `https://yourdomain.com`
2. Fill lead magnet form with test email: `qa-lead@testdomain.com`
3. Submit form and verify success message
4. Check ConvertKit for new subscriber
5. Verify email delivery within 5 minutes
6. Check admin dashboard for new lead record

**Expected Results:**
- ✅ Form submission successful
- ✅ User added to ConvertKit with "Lead_Magnet" tag  
- ✅ Lead magnet email delivered with PDF download
- ✅ Lead appears in admin dashboard
- ✅ Database record created in `lead_magnets` collection

**Test Data:**
```json
{
  "email": "qa-lead@testdomain.com",
  "first_name": "QA Lead",
  "lead_magnet_type": "ai_prompts_guide",
  "source": "qa_test"
}
```

### Test 2: User Registration Flow  
**Objective:** Verify account creation and dashboard access

**Steps:**
1. Click "Get Started" button on landing page
2. Register new account: `qa-user@testdomain.com` / `TestPass123!`
3. Verify email confirmation (if enabled)
4. Login and access customer dashboard
5. Navigate through all dashboard tabs
6. Verify prompt library shows premium gates

**Expected Results:**
- ✅ Account created successfully
- ✅ JWT token generated and stored
- ✅ Dashboard loads with correct user data
- ✅ Premium prompts show "subscription required" message
- ✅ Profile tab shows correct user information

**Test Data:**
```json
{
  "email": "qa-user@testdomain.com", 
  "password": "TestPass123!",
  "first_name": "QA",
  "last_name": "User"
}
```

### Test 3: Live Payment Flow ($1 Test Transaction)
**Objective:** Verify Stripe integration and post-purchase automation

**Steps:**
1. Navigate to pricing section
2. Click "Get Early Access Now" button  
3. Complete Stripe checkout with test card: `4242 4242 4242 4242`
4. Verify redirect to success page
5. Check for instant access email delivery
6. Login to customer account and verify premium access
7. Process refund in Stripe dashboard

**Expected Results:**
- ✅ Stripe checkout loads correctly
- ✅ Payment processes successfully
- ✅ Redirect to success page with download links
- ✅ Welcome email sent within 2 minutes
- ✅ Account upgraded to "presale_customer" status
- ✅ Premium prompts now accessible
- ✅ Refund processed successfully

**Test Payment:**
- Amount: $1.00 (to be refunded)
- Card: 4242 4242 4242 4242
- Exp: 12/25, CVC: 123

### Test 4: Admin Dashboard Functionality
**Objective:** Verify admin access and business analytics

**Steps:**
1. Login as admin: `admin@yourdomain.com`
2. Navigate to Admin Panel tab
3. Verify user metrics display correctly
4. Check recent users list
5. Review survey responses (if any)
6. Test user management functions

**Expected Results:**
- ✅ Admin login successful
- ✅ Admin Panel tab visible (not shown to regular users)
- ✅ Metrics cards show accurate data
- ✅ User list displays recent registrations
- ✅ User roles and subscription status correct
- ✅ Survey data displays properly

### Test 5: Survey Submission Flow
**Objective:** Verify survey collection and ConvertKit integration

**Steps:**
1. Access surveys tab in dashboard
2. Complete "Business Productivity Assessment"
3. Submit responses with test email
4. Verify survey appears in admin dashboard
5. Check ConvertKit for new subscriber/tag

**Expected Results:**
- ✅ Survey loads correctly
- ✅ All question types work (multiple choice, text, number)
- ✅ Submission successful
- ✅ Response stored in database
- ✅ Admin can view responses
- ✅ ConvertKit updated with survey completion

### Test 6: Mobile Responsiveness
**Objective:** Verify mobile user experience

**Steps:**
1. Test on mobile device or browser dev tools
2. Navigate through landing page
3. Complete lead magnet signup
4. Register account and access dashboard
5. Test payment flow on mobile
6. Verify all interactions work properly

**Expected Results:**
- ✅ Landing page renders correctly on mobile
- ✅ Forms are touch-friendly and functional
- ✅ Dashboard navigation works on small screens
- ✅ Payment flow optimized for mobile
- ✅ All buttons and links accessible

### Test 7: Email Automation Verification
**Objective:** Verify ConvertKit sequences trigger correctly

**Test Lead Magnet Sequence:**
1. Subscribe with email: `qa-leadmagnet@testdomain.com`
2. Verify Day 0 email (immediate delivery)
3. Check for Day 2 email (usage tips)
4. Monitor Day 4 email (value case study)  
5. Confirm Day 6 email (presale CTA)

**Test Presale Sequence:**
1. Complete purchase with email: `qa-presale@testdomain.com`
2. Verify Day 0 email (welcome + access)
3. Check Day 2 email (quick wins)
4. Monitor Day 4 email (ROI calculation)

**Expected Results:**
- ✅ All emails deliver on schedule
- ✅ Correct templates and personalization
- ✅ Download links work properly
- ✅ Unsubscribe links functional

## 🔧 Technical Tests

### API Endpoint Tests
```bash
# Health check
curl https://yourdomain.com/api/health

# Authentication test  
curl -X POST https://yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"qa-user@testdomain.com","password":"TestPass123!"}'

# Prompt library test
curl https://yourdomain.com/api/prompts

# Payment creation test
curl -X POST https://yourdomain.com/api/payments/create-checkout \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Database Tests
```bash
# Check MongoDB connection
mongosh "mongodb+srv://cluster.mongodb.net/bizpromptai_prod" --eval "db.runCommand('ping')"

# Verify collections exist
mongosh "mongodb+srv://cluster.mongodb.net/bizpromptai_prod" --eval "show collections"

# Check sample data
mongosh "mongodb+srv://cluster.mongodb.net/bizpromptai_prod" --eval "db.prompts.countDocuments()"
```

### SSL/Security Tests
```bash
# SSL certificate check
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Security headers check
curl -I https://yourdomain.com

# Rate limiting test
for i in {1..20}; do curl https://yourdomain.com/api/prompts; done
```

## 📋 Pre-Launch Checklist

### Domain & Infrastructure
- [ ] Domain configured and DNS propagated
- [ ] SSL certificate installed and valid
- [ ] CDN configured for static assets
- [ ] Server monitoring setup (New Relic, DataDog, etc.)
- [ ] Backup systems configured and tested
- [ ] Load balancer configured (if applicable)

### Application Configuration  
- [ ] All environment variables set correctly
- [ ] Database migrations completed
- [ ] Sample data loaded (prompts, surveys, admin user)
- [ ] File storage configured (AWS S3 or similar)
- [ ] Email delivery service configured
- [ ] Error tracking setup (Sentry)

### Third-Party Integrations
- [ ] Stripe live mode enabled with correct products/prices
- [ ] Stripe webhooks configured and tested  
- [ ] ConvertKit sequences created and activated
- [ ] ConvertKit forms embedded correctly
- [ ] Google Analytics tracking installed
- [ ] Google Forms created and linked

### Security & Performance
- [ ] Rate limiting enabled
- [ ] CORS configured for production domains
- [ ] Security headers implemented
- [ ] Database access restricted
- [ ] API keys secured in environment variables
- [ ] Log rotation configured

### Content & Assets
- [ ] 5-prompt PDF uploaded and accessible
- [ ] All prompt library content reviewed
- [ ] Email templates finalized in ConvertKit
- [ ] Landing page copy optimized
- [ ] Legal pages added (Terms, Privacy, Refunds)

## 🐛 Common Issues & Fixes

### Payment Issues
**Issue:** Stripe checkout not loading
**Fix:** Verify STRIPE_PUBLISHABLE_KEY in frontend environment

**Issue:** Webhooks not firing
**Fix:** Check webhook URL in Stripe dashboard matches production URL

### Email Issues  
**Issue:** Emails not delivering
**Fix:** Verify ConvertKit API credentials and sequence IDs

**Issue:** Wrong email templates
**Fix:** Check sequence configuration in ConvertKit dashboard

### Access Issues
**Issue:** Users can't login after purchase
**Fix:** Verify JWT secret consistency and user role assignment

**Issue:** Premium prompts not accessible
**Fix:** Check subscription status in user database record

### Performance Issues
**Issue:** Slow page load times
**Fix:** Enable CDN, optimize images, check database query performance

**Issue:** API timeouts
**Fix:** Add Redis caching, optimize database indexes

## 📊 Success Metrics

### Launch Day Targets
- **Visitors:** 500+ unique visitors
- **Lead Signups:** 50+ email subscribers  
- **Conversions:** 10+ presale purchases
- **Email Deliverability:** >95% delivery rate
- **Page Load Speed:** <3 seconds
- **Error Rate:** <1% of requests

### Week 1 Targets  
- **Visitors:** 2,000+ unique visitors
- **Lead Conversion:** 10% visitor to lead rate
- **Purchase Conversion:** 15% lead to customer rate
- **Revenue:** $500+ in presales
- **Email Engagement:** 40%+ open rate, 10%+ click rate
- **Customer Satisfaction:** >4.5/5 rating

This comprehensive QA plan ensures all critical user flows work correctly before launch and provides benchmarks for measuring success.