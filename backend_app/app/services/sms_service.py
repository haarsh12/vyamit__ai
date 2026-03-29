"""
SMS Service using Fast2SMS — OTP and bill sharing.
"""
import logging
import os

import requests

logger = logging.getLogger("sms")

FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY")


def _phone_tail(phone: str) -> str:
    digits = "".join(c for c in phone if c.isdigit())
    return digits[-4:] if len(digits) >= 4 else "****"


class SMSService:
    def __init__(self):
        if FAST2SMS_API_KEY:
            self.api_key = FAST2SMS_API_KEY
            logger.info("[OK] Fast2SMS service initialized.")
        else:
            self.api_key = None
            logger.warning("[WARN] FAST2SMS_API_KEY not set — SMS will be mocked.")

    def send_otp(self, phone_number: str, otp: str):
        """Send OTP via Fast2SMS OTP route."""
        tail = _phone_tail(phone_number)
        if not self.api_key:
            logger.warning("[WARN] SMS mock: OTP not sent over network (phone ending %s)", tail)
            return True

        try:
            clean_phone = phone_number.replace("+91", "").replace(" ", "").strip()
            url = "https://www.fast2sms.com/dev/bulkV2"
            params = {
                "authorization": self.api_key,
                "route": "otp",
                "variables_values": otp,
                "numbers": clean_phone,
                "flash": "0",
            }

            logger.info("[INFO] Sending OTP via Fast2SMS (phone ending %s)", tail)
            response = requests.get(url, params=params, timeout=10)
            logger.info("[INFO] Fast2SMS HTTP status: %s", response.status_code)

            if response.text.startswith("<!DOCTYPE") or response.text.startswith("<html"):
                logger.error("[ERROR] Fast2SMS returned HTML (check API key and route).")
                return True

            if not response.text or not response.text.strip():
                logger.error("[ERROR] Fast2SMS returned empty body.")
                return True

            try:
                result = response.json()
            except ValueError:
                logger.error("[ERROR] Fast2SMS invalid JSON: %s", response.text[:200])
                return True

            if result.get("return"):
                logger.info("[OK] OTP SMS accepted by Fast2SMS (phone ending %s).", tail)
                return True
            logger.error("[ERROR] Fast2SMS: %s", result.get("message"))
            return True

        except Exception as e:
            logger.error("[ERROR] Fast2SMS request failed: %s", e)
            return True


def send_sms_bill(to_number: str, message: str) -> dict:
    """Send bill text via Fast2SMS quick route."""
    tail = _phone_tail(to_number)
    if not FAST2SMS_API_KEY:
        logger.warning("[WARN] Fast2SMS not configured — bill SMS mocked (phone ending %s)", tail)
        logger.debug("Mock bill message length: %s chars", len(message))
        return {
            "success": True,
            "message_id": "MOCK_MSG_12345",
            "error": None,
        }

    try:
        clean_phone = to_number.replace("+91", "").replace(" ", "").strip()
        url = "https://www.fast2sms.com/dev/bulkV2"
        params = {
            "authorization": FAST2SMS_API_KEY,
            "route": "q",
            "message": message,
            "language": "english",
            "flash": 0,
            "numbers": clean_phone,
        }

        logger.info("[INFO] Sending bill SMS (phone ending %s)", tail)
        response = requests.get(url, params=params, timeout=10)
        logger.info("[INFO] Fast2SMS HTTP status: %s", response.status_code)

        if not response.text or not response.text.strip():
            logger.error("[ERROR] Fast2SMS returned empty response")
            return {
                "success": False,
                "message_id": None,
                "error": "Empty response from Fast2SMS",
            }

        result = response.json()
        if result.get("return"):
            logger.info("[OK] Bill SMS sent (phone ending %s)", tail)
            return {
                "success": True,
                "message_id": result.get("request_id"),
                "error": None,
            }
        logger.error("[ERROR] Fast2SMS: %s", result.get("message"))
        return {
            "success": False,
            "message_id": None,
            "error": result.get("message"),
        }

    except Exception as e:
        logger.error("[ERROR] Fast2SMS error: %s", e)
        return {
            "success": False,
            "message_id": None,
            "error": str(e),
        }
