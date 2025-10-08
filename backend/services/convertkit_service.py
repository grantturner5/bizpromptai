import os
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConvertKitService:
    def __init__(self):
        self.api_key = os.getenv("CONVERTKIT_API_KEY")
        self.api_secret = os.getenv("CONVERTKIT_API_SECRET")
        self.form_id = os.getenv("CONVERTKIT_FORM_ID")
        self.base_url = "https://api.convertkit.com/v3"
        
        # Email sequence IDs (you'll configure these in ConvertKit)
        self.sequences = {
            "welcome": "12345",  # Welcome sequence ID
            "lead_magnet": "12346",  # Lead magnet sequence ID
            "customer_onboarding": "12347",  # Customer onboarding sequence
            "nurture": "12348"  # Long-term nurture sequence
        }
        
        # Tag IDs for different subscriber types
        self.tags = {
            "lead_magnet_subscriber": "10001",
            "paying_customer": "10002",
            "presale_customer": "10003",
            "regular_customer": "10004",
            "high_engagement": "10005"
        }
    
    async def add_subscriber(
        self,
        email: str,
        first_name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        custom_fields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add subscriber to ConvertKit"""
        
        if not self.api_key or not self.form_id:
            logger.warning("ConvertKit API key or form ID not configured")
            return {"success": False, "error": "ConvertKit not configured"}
        
        url = f"{self.base_url}/forms/{self.form_id}/subscribe"
        
        payload = {
            "api_key": self.api_key,
            "email": email
        }
        
        if first_name:
            payload["first_name"] = first_name
        
        if custom_fields:
            payload.update(custom_fields)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        subscriber_id = data.get("subscription", {}).get("subscriber", {}).get("id")
                        
                        # Add tags if provided
                        if tags and subscriber_id:
                            for tag in tags:
                                await self.add_tag_to_subscriber(email, tag)
                        
                        logger.info(f"Successfully added subscriber: {email}")
                        return {
                            "success": True,
                            "subscriber_id": subscriber_id,
                            "data": data
                        }
                    else:
                        error_data = await response.json()
                        logger.error(f"ConvertKit API error: {error_data}")
                        return {"success": False, "error": error_data}
                        
        except Exception as e:
            logger.error(f"Failed to add subscriber {email}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def add_to_sequence(
        self,
        email: str,
        sequence_name: str,
        custom_fields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add subscriber to email sequence"""
        
        if sequence_name not in self.sequences:
            return {"success": False, "error": f"Unknown sequence: {sequence_name}"}
        
        sequence_id = self.sequences[sequence_name]
        url = f"{self.base_url}/sequences/{sequence_id}/subscribe"
        
        payload = {
            "api_key": self.api_key,
            "email": email
        }
        
        if custom_fields:
            payload.update(custom_fields)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Added {email} to {sequence_name} sequence")
                        return {"success": True, "data": data}
                    else:
                        error_data = await response.json()
                        logger.error(f"Failed to add to sequence: {error_data}")
                        return {"success": False, "error": error_data}
                        
        except Exception as e:
            logger.error(f"Failed to add {email} to sequence {sequence_name}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def add_tag_to_subscriber(self, email: str, tag_name: str) -> Dict[str, Any]:
        """Add tag to subscriber"""
        
        if tag_name not in self.tags:
            return {"success": False, "error": f"Unknown tag: {tag_name}"}
        
        tag_id = self.tags[tag_name]
        url = f"{self.base_url}/tags/{tag_id}/subscribe"
        
        payload = {
            "api_key": self.api_key,
            "email": email
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Added tag '{tag_name}' to {email}")
                        return {"success": True, "data": data}
                    else:
                        error_data = await response.json()
                        logger.error(f"Failed to add tag: {error_data}")
                        return {"success": False, "error": error_data}
                        
        except Exception as e:
            logger.error(f"Failed to add tag {tag_name} to {email}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def process_lead_magnet_signup(
        self,
        email: str,
        first_name: Optional[str] = None,
        magnet_type: str = "general"
    ) -> Dict[str, Any]:
        """Complete lead magnet signup process"""
        
        try:
            # Step 1: Add to main list
            subscriber_result = await self.add_subscriber(
                email=email,
                first_name=first_name,
                tags=["lead_magnet_subscriber"]
            )
            
            if not subscriber_result["success"]:
                return subscriber_result
            
            # Step 2: Add to lead magnet sequence
            sequence_result = await self.add_to_sequence(
                email=email,
                sequence_name="lead_magnet"
            )
            
            # Step 3: Add to nurture sequence (delayed)
            await asyncio.sleep(1)  # Small delay
            nurture_result = await self.add_to_sequence(
                email=email,
                sequence_name="nurture"
            )
            
            return {
                "success": True,
                "message": "Lead magnet signup processed successfully",
                "subscriber_id": subscriber_result.get("subscriber_id"),
                "sequences_added": ["lead_magnet", "nurture"]
            }
            
        except Exception as e:
            logger.error(f"Lead magnet signup failed for {email}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def process_customer_purchase(
        self,
        email: str,
        first_name: Optional[str] = None,
        product_type: str = "regular",
        amount: float = 47.0
    ) -> Dict[str, Any]:
        """Process customer purchase and onboarding"""
        
        try:
            # Determine customer tag based on purchase type
            customer_tag = "presale_customer" if product_type == "presale" else "regular_customer"
            
            # Step 1: Add customer tags
            await self.add_tag_to_subscriber(email, "paying_customer")
            await self.add_tag_to_subscriber(email, customer_tag)
            
            # Step 2: Add to customer onboarding sequence
            onboarding_result = await self.add_to_sequence(
                email=email,
                sequence_name="customer_onboarding",
                custom_fields={
                    "purchase_amount": str(amount),
                    "purchase_date": datetime.utcnow().isoformat(),
                    "product_type": product_type
                }
            )
            
            logger.info(f"Processed customer purchase for {email} - {product_type} ${amount}")
            
            return {
                "success": True,
                "message": "Customer purchase processed successfully",
                "onboarding_sequence": onboarding_result["success"],
                "customer_type": customer_tag
            }
            
        except Exception as e:
            logger.error(f"Customer purchase processing failed for {email}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_subscriber_info(self, email: str) -> Dict[str, Any]:
        """Get subscriber information from ConvertKit"""
        
        if not self.api_secret:
            return {"success": False, "error": "ConvertKit API secret not configured"}
        
        url = f"{self.base_url}/subscribers"
        params = {
            "api_secret": self.api_secret,
            "email_address": email
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        subscribers = data.get("subscribers", [])
                        
                        if subscribers:
                            return {"success": True, "subscriber": subscribers[0]}
                        else:
                            return {"success": False, "error": "Subscriber not found"}
                    else:
                        error_data = await response.json()
                        return {"success": False, "error": error_data}
                        
        except Exception as e:
            logger.error(f"Failed to get subscriber info for {email}: {str(e)}")
            return {"success": False, "error": str(e)}