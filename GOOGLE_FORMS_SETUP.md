# Google Forms Integration Setup

## 📝 Survey Form Configuration

### Form Title: "Business Productivity Assessment - AI Automation Insights"

### Form Description:
```
Help us understand your biggest productivity challenges and be the first to access our AI automation solutions.

This 2-minute survey will help us create better tools for business professionals like you.

As a thank you, you'll get immediate access to our 5-Prompt Quick Start Guide (normally $15).
```

### Questions Configuration

#### Question 1: Business Task Analysis
**Type:** Multiple Choice (Required)
**Question:** "Which business task currently costs you the most time each week?"

**Options:**
- Email writing and responses
- Content creation (blogs, social posts, proposals)
- Research and competitive analysis  
- Project management and reporting
- Meeting preparation and follow-up
- Sales outreach and lead generation
- Other (please specify)

#### Question 2: Time Investment
**Type:** Short Answer (Required)
**Question:** "Approximately how many hours per week do you spend on your biggest time-consuming task?"

**Validation:** Number, minimum 1, maximum 80

#### Question 3: Purchase Intent
**Type:** Multiple Choice (Required)  
**Question:** "Would you pre-order a complete AI automation toolkit (47 prompts) for $37 if it could save you 10+ hours per week?"

**Options:**
- Yes, I would purchase immediately
- Yes, but I need more information first
- Maybe, depends on the specific prompts included
- No, I'm not interested right now
- No, the price is too high for me

#### Question 4: AI Concerns (Optional)
**Type:** Paragraph Text (Optional)
**Question:** "What's your biggest concern or question about using AI for business automation? (Optional - helps us address common worries)"

**Helper Text:** "Common concerns include: accuracy, learning curve, integration with existing tools, job security, etc."

#### Question 5: Contact Information
**Type:** Short Answer (Required)
**Question:** "Email address (to send your free 5-Prompt Guide)"

**Validation:** Email format required

#### Question 6: Name (Optional)
**Type:** Short Answer (Optional)
**Question:** "First Name (for personalization - optional)"

### Hidden Fields for UTM Tracking

Add these as hidden/prefilled fields that can be populated via URL parameters:

#### UTM Source
**Type:** Short Answer (Hidden)
**Parameter Name:** `utm_source`
**Default Value:** "organic"

#### UTM Medium  
**Type:** Short Answer (Hidden)
**Parameter Name:** `utm_medium`
**Default Value:** "survey"

#### UTM Campaign
**Type:** Short Answer (Hidden)
**Parameter Name:** `utm_campaign`
**Default Value:** "productivity_assessment"

#### Timestamp
**Type:** Short Answer (Hidden)
**Parameter Name:** `timestamp`
**Default Value:** Auto-populated with current datetime

## 🔗 Form URL Structure

### Base Form URL:
`https://forms.gle/YOUR_FORM_ID_HERE`

### UTM-Enabled URL Examples:
```
# LinkedIn Traffic
https://forms.gle/YOUR_FORM_ID_HERE?utm_source=linkedin&utm_medium=social&utm_campaign=productivity_poll

# Email Campaign
https://forms.gle/YOUR_FORM_ID_HERE?utm_source=email&utm_medium=newsletter&utm_campaign=lead_nurture

# Website Embed
https://forms.gle/YOUR_FORM_ID_HERE?utm_source=website&utm_medium=embed&utm_campaign=homepage_form

# Direct Link
https://forms.gle/YOUR_FORM_ID_HERE?utm_source=direct&utm_medium=link&utm_campaign=social_share
```

## ⚙️ Response Processing Setup

### Google Sheets Integration
1. **Create Response Spreadsheet:**
   - Form responses automatically populate Google Sheets
   - Add calculated columns for analysis
   - Set up data validation and formatting

2. **Spreadsheet Columns:**
   - Timestamp (auto)
   - Email Address
   - First Name
   - Biggest Time-Consuming Task
   - Hours Per Week
   - Purchase Intent
   - AI Concerns
   - UTM Source
   - UTM Medium  
   - UTM Campaign
   - Lead Score (calculated)
   - Follow-up Status

### Zapier Integration (Alternative)
```javascript
// Zapier Webhook Configuration
{
  "trigger": "Google Forms New Response",
  "actions": [
    {
      "app": "Webhooks",
      "action": "POST",
      "url": "https://yourdomain.com/api/webhooks/google-form",
      "data": {
        "email": "{{Email Address}}",
        "first_name": "{{First Name}}",
        "biggest_task": "{{Business Task}}",
        "hours_per_week": "{{Hours Per Week}}",
        "purchase_intent": "{{Purchase Intent}}",
        "ai_concerns": "{{AI Concerns}}",
        "utm_source": "{{UTM Source}}",
        "utm_medium": "{{UTM Medium}}",
        "utm_campaign": "{{UTM Campaign}}"
      }
    },
    {
      "app": "ConvertKit",
      "action": "Add Subscriber",
      "email": "{{Email Address}}",
      "first_name": "{{First Name}}",
      "tags": ["Lead_Magnet", "Survey_Completed"]
    }
  ]
}
```

### Direct API Integration
```python
# Webhook endpoint in your application
@app.post("/api/webhooks/google-form")
async def handle_google_form_submission(request: Request):
    """Process Google Forms responses"""
    data = await request.json()
    
    # Extract and validate data
    survey_response = {
        "survey_id": "productivity_assessment",
        "user_email": data.get("email"),
        "responses": {
            "biggest_task": data.get("biggest_task"),
            "hours_per_week": data.get("hours_per_week"), 
            "purchase_intent": data.get("purchase_intent"),
            "ai_concerns": data.get("ai_concerns")
        },
        "utm_data": {
            "source": data.get("utm_source"),
            "medium": data.get("utm_medium"),
            "campaign": data.get("utm_campaign")
        },
        "submitted_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Save to database
    await db.survey_responses.insert_one(survey_response)
    
    # Add to ConvertKit
    convertkit = ConvertKitIntegration()
    await convertkit.add_subscriber_to_sequence(
        email=data.get("email"),
        sequence_id=CONVERTKIT_SEQUENCE_LEAD_MAGNET,
        first_name=data.get("first_name")
    )
    await convertkit.add_tag_to_subscriber(
        email=data.get("email"),
        tag_id=CONVERTKIT_TAG_LEAD_MAGNET
    )
    
    # Calculate lead score
    lead_score = calculate_lead_score(survey_response)
    
    # High-intent leads get special treatment
    if lead_score > 80:
        await convertkit.add_tag_to_subscriber(
            email=data.get("email"),
            tag_id=CONVERTKIT_TAG_HIGH_INTENT
        )
    
    return {"status": "success", "lead_score": lead_score}

def calculate_lead_score(response_data):
    """Calculate lead score based on survey responses"""
    score = 0
    
    # Time investment scoring
    hours = response_data["responses"].get("hours_per_week", 0)
    if hours >= 10:
        score += 30
    elif hours >= 5:
        score += 20
    elif hours >= 2:
        score += 10
    
    # Purchase intent scoring
    intent = response_data["responses"].get("purchase_intent", "")
    if "immediately" in intent.lower():
        score += 50
    elif "more information" in intent.lower():
        score += 30
    elif "maybe" in intent.lower():
        score += 15
    
    # Task type scoring (some tasks have higher automation potential)
    task = response_data["responses"].get("biggest_task", "")
    high_value_tasks = ["email", "content creation", "research"]
    if any(hvt in task.lower() for hvt in high_value_tasks):
        score += 20
    
    return min(score, 100)  # Cap at 100
```

## 📊 Response Analytics Setup

### Google Sheets Analysis Dashboard
Create additional sheets in your response spreadsheet:

#### Summary Sheet
```
=QUERY(Responses!A:J, "SELECT COUNT(A), AVG(D) WHERE A IS NOT NULL", 1)
```

#### Lead Score Distribution
```
=ARRAYFORMULA(IF(Responses!D2:D<>"", 
  IF(Responses!D2:D>=10, "High Priority",
  IF(Responses!D2:D>=5, "Medium Priority", "Low Priority")), ""))
```

#### Purchase Intent Analysis
```
=COUNTIF(Responses!F:F, "*immediately*")
=COUNTIF(Responses!F:F, "*more information*")  
=COUNTIF(Responses!F:F, "*maybe*")
```

#### UTM Source Performance
```
=QUERY(Responses!A:J, "SELECT I, COUNT(I) WHERE I IS NOT NULL GROUP BY I ORDER BY COUNT(I) DESC", 1)
```

### ConvertKit Tag Strategy
Based on survey responses, automatically apply tags:

- **High_Intent** - Purchase intent = "immediately"
- **Needs_Info** - Purchase intent = "more information"
- **Email_Heavy** - Biggest task = "Email writing"
- **Content_Creator** - Biggest task = "Content creation"
- **Heavy_User** - Hours per week >= 10
- **Budget_Conscious** - Mentioned price concerns

## 🔄 Follow-up Automation

### Immediate Actions (Day 0)
1. Send lead magnet email with 5-prompt PDF
2. Add to appropriate ConvertKit sequence
3. Apply behavioral tags based on responses
4. Update lead score in CRM

### Day 3 Follow-up
- **High Intent Leads:** Personal outreach email
- **Needs Info Leads:** Send case studies and testimonials
- **Maybe Leads:** Educational content about AI benefits

### Day 7 Follow-up
- **High Intent:** Direct sales call offer
- **Needs Info:** Product demo invitation
- **Maybe:** Success stories and social proof

## 📱 Mobile Optimization

### Form Settings
- Enable "Mobile-friendly" option in Google Forms
- Use shorter question text for mobile screens
- Minimize required fields to reduce abandonment
- Test on various mobile devices

### Embedding Options
```html
<!-- Responsive Embed Code -->
<div style="position: relative; width: 100%; height: 0; padding-bottom: 56.25%;">
  <iframe 
    src="https://forms.gle/YOUR_FORM_ID_HERE" 
    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"
    frameborder="0"
    marginheight="0" 
    marginwidth="0">
    Loading...
  </iframe>
</div>
```

## 🎯 A/B Testing Setup

### Test Variations
1. **Question Order:** Task selection first vs. time investment first
2. **Pricing Mention:** $37 vs. "affordable" vs. no price
3. **CTA Copy:** "Get Free Guide" vs. "Send My Prompts" vs. "Start Saving Time"
4. **Form Length:** 4 questions vs. 6 questions vs. 3 questions

### Testing Process
1. Create multiple form versions
2. Split traffic 50/50 using different URLs
3. Track completion rates and lead quality
4. Measure downstream conversion to purchase
5. Implement winning variation

This Google Forms setup captures high-quality leads while providing detailed insights into your target audience's needs and purchase intent.