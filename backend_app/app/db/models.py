from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(15), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    shop_details = relationship("ShopDetails", back_populates="owner", uselist=False)
    bills = relationship("Bill", back_populates="user")

class ShopDetails(Base):
    __tablename__ = "shop_details"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    shop_name = Column(String(200), nullable=False)
    address = Column(Text, nullable=True)
    phone1 = Column(String(15), nullable=True)
    phone2 = Column(String(15), nullable=True)
    gst_number = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="shop_details")

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(200), nullable=False)
    alternative_names = Column(Text, nullable=True)  # JSON string of alternative names
    price = Column(Float, default=0.0)
    unit = Column(String(50), default="kg")
    category = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    bill_items = relationship("BillItem", back_populates="item")

class Bill(Base):
    __tablename__ = "bills"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    bill_number = Column(String(50), unique=True, nullable=False)
    customer_name = Column(String(200), nullable=True)
    customer_phone = Column(String(15), nullable=True)
    total_amount = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    final_amount = Column(Float, default=0.0)
    payment_method = Column(String(50), default="cash")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="bills")
    bill_items = relationship("BillItem", back_populates="bill", cascade="all, delete-orphan")

class BillItem(Base):
    __tablename__ = "bill_items"
    
    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    item_name = Column(String(200), nullable=False)  # Store name at time of billing
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Relationships
    bill = relationship("Bill", back_populates="bill_items")
    item = relationship("Item", back_populates="bill_items")