"""
SMS Service using Fast2SMS
Handles OTP and Bill sharing via SMS
"""
import os
import logging
import requests

logger = logging.getLogger("sms")

# Fast2SMS Configuration
FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY")


class SMSService:
    def __init__(self):
        if FAST2SMS_API_KEY:
            self.api_key = FAST2SMS_API_KEY
            logger.info("✅ Fast2SMS Service initialized")
        else:
            self.api_key = None
            logger.warning("⚠️ Fast2SMS API key not found - SMS will be mocked")
    
    def send_otp(self, phone_number: str, otp: str):
        """Send OTP via SMS using Fast2SMS OTP Message API"""
        if not self.api_key:
            logger.warning(f"SMS MOCK → {phone_number} OTP={otp}")
            return True
        
        try:
            # Clean phone number - remove +91 and any spaces
            clean_phone = phone_number.replace("+91", "").replace(" ", "").strip()
            
            # Fast2SMS bulk API with OTP route (uses GET method)
            url = "https://www.fast2sms.com/dev/bulkV2"
            
            headers = {
                "authorization": self.api_key
            }
            
            # Use OTP Message route as shown in Fast2SMS dashboard
            params = {
                "authorization": self.api_key,
                "route": "otp",
                "variables_values": otp,  # The OTP code
                "numbers": clean_phone,
                "flash": "0"
            }
            
            logger.info(f"📤 Sending OTP to {clean_phone} via Fast2SMS...")
            logger.info(f"📤 API Key: {self.api_key[:10]}...{self.api_key[-10:]}")
            logger.info(f"📤 Using GET /dev/bulkV2 with route=otp")
            logger.info(f"📤 Full URL: {url}?{requests.compat.urlencode(params)}")
            
            # Use GET method
            response = requests.get(url, params=params, timeout=10)
            
            logger.info(f"📥 Fast2SMS Response Status: {response.status_code}")
            logger.info(f"📥 Fast2SMS Response: {response.text}")
            
            # Check if response is HTML (error page)
            if response.text.startswith("<!DOCTYPE") or response.text.startswith("<html"):
                logger.error(f"❌ Fast2SMS returned HTML error page")
                logger.error(f"   This usually means wrong endpoint or parameters")
                logger.info(f"📱 OTP for {phone_number}: {otp} (SMS failed but OTP generated)")
                return True
            
            # Check if response is empty
            if not response.text or response.text.strip() == "":
                logger.error(f"❌ Fast2SMS returned empty response. Status: {response.status_code}")
                logger.info(f"📱 OTP for {phone_number}: {otp} (SMS failed but OTP generated)")
                return True
            
            try:
                result = response.json()
                
                if result.get("return"):
                    logger.info(f"✅ OTP sent successfully to {clean_phone}")
                    logger.info(f"   Message ID: {result.get('request_id')}")
                    return True
                else:
                    logger.error(f"❌ Fast2SMS error: {result.get('message')}")
                    logger.info(f"📱 OTP for {phone_number}: {otp} (SMS failed but OTP generated)")
                    return True
                    
            except ValueError as e:
                logger.error(f"❌ Fast2SMS returned invalid JSON: {response.text[:100]}")
                logger.info(f"📱 OTP for {phone_number}: {otp} (SMS failed but OTP generated)")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to send OTP: {e}")
            logger.info(f"📱 OTP for {phone_number}: {otp} (SMS failed but OTP generated)")
            return True


def send_sms_bill(to_number: str, message: str) -> dict:
    """
    Send bill via Fast2SMS using simple SMS API (GET method)
    
    Args:
        to_number: Phone number (10 digits)
        message: Bill text to send
    
    Returns:
        dict with success status and message ID or error
    """
    
    if not FAST2SMS_API_KEY:
        logger.warning("⚠️ Fast2SMS not configured - SMS mocked")
        print(f"📱 MOCK SMS to {to_number}:")
        print(message)
        return {
            "success": True,
            "message_id": "MOCK_MSG_12345",
            "error": None
        }
    
    try:
        # Clean phone number
        clean_phone = to_number.replace("+91", "").replace(" ", "").strip()
        
        # Use simple SMS API with GET method
        url = "https://www.fast2sms.com/dev/bulkV2"
        
        headers = {
            "authorization": FAST2SMS_API_KEY
        }
        
        params = {
            "route": "q",  # Quick transactional route
            "message": message,
            "language": "english",
            "flash": 0,
            "numbers": clean_phone
        }
        
        logger.info(f"📤 Sending bill SMS to {clean_phone}...")
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        logger.info(f"📥 Response Status: {response.status_code}")
        logger.info(f"📥 Response: {response.text}")
        
        if not response.text or response.text.strip() == "":
            logger.error(f"❌ Fast2SMS returned empty response")
            return {
                "success": False,
                "message_id": None,
                "error": "Empty response from Fast2SMS"
            }
        
        result = response.json()
        
        if result.get("return"):
            logger.info(f"✅ Bill SMS sent to {clean_phone}")
            return {
                "success": True,
                "message_id": result.get("request_id"),
                "error": None
            }
        else:
            logger.error(f"❌ Fast2SMS error: {result.get('message')}")
            return {
                "success": False,
                "message_id": None,
                "error": result.get("message")
            }
        
    except Exception as e:
        logger.error(f"❌ Fast2SMS error: {e}")
        return {
            "success": False,
            "message_id": None,
            "error": str(e)
        }
