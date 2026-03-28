import random
import string
import logging
from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.db.models import OTP

# Configure logging
logger = logging.getLogger(__name__)

class OTPService:
    def generate_otp(self) -> str:
        """Generates a FIXED 6-digit OTP for demo purposes"""
        # FIXED OTP FOR DEMO - Always returns 112233
        return '112233'

    def create_otp(self, session: Session, phone_number: str) -> str:
        """Generates OTP, saves to DB, and returns it"""
        
        # FIX: Sanitize phone
        clean_phone = phone_number.strip()

        # 1. Generate Code (FIXED: Always 112233)
        code = self.generate_otp()
        
        # 2. Set Expiry (5 minutes from now)
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        # 3. Create Record
        otp_record = OTP(
            phone_number=clean_phone,
            otp_code=code,  
            expires_at=expires_at,
            is_used=False
        )
        
        # 4. Save to DB
        session.add(otp_record)
        session.commit()
        session.refresh(otp_record)
        
        # ============================================
        # 🔐 OTP GENERATED - DEPLOYMENT LOGGING
        # ============================================
        logger.warning("=" * 60)
        logger.warning("🔐 OTP GENERATED FOR DEPLOYMENT")
        logger.warning("=" * 60)
        logger.warning(f"📱 Phone Number: {clean_phone}")
        logger.warning(f"🔢 OTP Code: {code}")
        logger.warning(f"⏰ Expires At: {expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        logger.warning("=" * 60)
        print("\n" + "=" * 60)
        print("🔐 OTP GENERATED FOR DEPLOYMENT")
        print("=" * 60)
        print(f"📱 Phone Number: {clean_phone}")
        print(f"🔢 OTP Code: {code}")
        print(f"⏰ Expires At: {expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("=" * 60 + "\n")
        
        return code

    def verify_otp(self, session: Session, phone_number: str, code: str) -> bool:
        """Checks if the OTP is valid and not expired"""
        
        # FIX: Sanitize phone
        clean_phone = phone_number.strip()

        logger.info(f"🔍 Verifying OTP for phone: {clean_phone}, code: {code}")

        # 1. Find the OTP in DB
        statement = select(OTP).where(
            OTP.phone_number == clean_phone,
            OTP.otp_code == code,
            OTP.is_used == False,
            OTP.expires_at > datetime.utcnow()
        )
        result = session.exec(statement).first()
        
        if not result:
            logger.warning(f"❌ OTP verification FAILED for {clean_phone}")
            return False
            
        # 2. Mark as used so it can't be used again
        result.is_used = True
        session.add(result)
        session.commit()
        
        logger.warning(f"✅ OTP verification SUCCESS for {clean_phone}")
        
        return True