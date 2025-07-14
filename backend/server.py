from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import jwt
import bcrypt
import os
import uuid
from dotenv import load_dotenv
import asyncio
import json
import re
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

app = FastAPI(title="ChatBot Omni-Channel API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "test_database")
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Collections
users_collection = db.users
chat_history_collection = db.chat_history
bot_configs_collection = db.bot_configs
webhook_logs_collection = db.webhook_logs

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
security = HTTPBearer()

# Default AI provider settings
DEFAULT_AI_PROVIDER = "gemini"
DEFAULT_AI_KEY = "AIzaSyBgVNvJp88oDPsqERwMbZCjCV6fqDXIShg"

# Create default superadmin if not exists
def create_default_superadmin():
    existing_admin = users_collection.find_one({"email": "admin@omnibot.com"})
    if not existing_admin:
        admin_data = {
            "user_id": str(uuid.uuid4()),
            "email": "admin@omnibot.com",
            "full_name": "Super Admin",
            "password": hash_password("admin123"),
            "role": "superadmin",
            "plan": "premium",
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        users_collection.insert_one(admin_data)
        print("✅ Default superadmin created: admin@omnibot.com / admin123")

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class BotConfig(BaseModel):
    bot_name: str
    platform: str  # whatsapp, telegram, line, instagram
    api_key: str
    webhook_url: Optional[str] = None
    ai_provider: str = DEFAULT_AI_PROVIDER
    ai_model: str = "gemini-2.0-flash"
    ai_api_key: Optional[str] = None
    system_message: str = "You are a helpful assistant."
    auto_reply: bool = True
    phone_number: Optional[str] = None  # For WhatsApp
    phone_number_id: Optional[str] = None  # For WhatsApp Business API

class ChatMessage(BaseModel):
    message: str
    bot_id: str
    platform: str
    sender_id: str

class AISettings(BaseModel):
    provider: str  # openai, anthropic, gemini, deepseek, qwen, kimi
    model: str
    api_key: str
    system_message: str = "You are a helpful assistant."

class XenditSettings(BaseModel):
    api_key: str
    public_key: str
    callback_token: str

class PhoneNumberVerification(BaseModel):
    phone_number: str
    verification_code: str

class TestChatMessage(BaseModel):
    message: str
    bot_id: str

# Utility functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = users_collection.find_one({"user_id": user_id})
    if user is None:
        raise credentials_exception
    return user

def get_user_chat_count(user_id: str) -> int:
    """Get current month's chat count for user"""
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    count = chat_history_collection.count_documents({
        "user_id": user_id,
        "created_at": {"$gte": start_of_month}
    })
    return count

def get_user_limit(user_plan: str) -> int:
    """Get chat limit based on user plan"""
    limits = {
        "free": 100,
        "basic": 1000,
        "premium": 5000
    }
    return limits.get(user_plan, 100)

def validate_phone_number(phone_number: str) -> bool:
    """Validate phone number format"""
    # Basic phone number validation
    pattern = r'^\+?[\d\s\-\(\)]{10,15}$'
    return re.match(pattern, phone_number) is not None

async def send_ai_message(message: str, ai_settings: dict, session_id: str = None) -> str:
    """Send message to AI provider and get response"""
    try:
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Use user's AI settings or default
        provider = ai_settings.get("provider", DEFAULT_AI_PROVIDER)
        model = ai_settings.get("model", "gemini-2.0-flash")
        api_key = ai_settings.get("api_key", DEFAULT_AI_KEY)
        system_message = ai_settings.get("system_message", "You are a helpful assistant.")
        
        # Create LLM chat instance
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=system_message
        )
        
        # Set the model based on provider
        chat.with_model(provider, model)
        
        # Create user message
        user_message = UserMessage(text=message)
        
        # Get response
        response = await chat.send_message(user_message)
        return response
        
    except Exception as e:
        print(f"AI Error: {str(e)}")
        return f"Sorry, I encountered an error: {str(e)}"

# Initialize default superadmin on startup
create_default_superadmin()

# Routes
@app.get("/")
async def root():
    return {"message": "ChatBot Omni-Channel API is running!", "version": "1.0.0"}

@app.post("/api/auth/register")
async def register(user: UserCreate):
    # Check if user already exists
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user.password)
    
    user_data = {
        "user_id": user_id,
        "email": user.email,
        "full_name": user.full_name,
        "password": hashed_password,
        "role": "user",
        "plan": "free",
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    users_collection.insert_one(user_data)
    
    # Create access token
    access_token = create_access_token(data={"sub": user_id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "user_id": user_id,
            "email": user.email,
            "full_name": user.full_name,
            "role": "user",
            "plan": "free"
        }
    }

@app.post("/api/auth/login")
async def login(user: UserLogin):
    # Find user
    db_user = users_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    access_token = create_access_token(data={"sub": db_user["user_id"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "user_id": db_user["user_id"],
            "email": db_user["email"],
            "full_name": db_user["full_name"],
            "role": db_user["role"],
            "plan": db_user["plan"]
        }
    }

@app.get("/api/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    chat_count = get_user_chat_count(current_user["user_id"])
    limit = get_user_limit(current_user["plan"])
    
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "role": current_user["role"],
        "plan": current_user["plan"],
        "chat_count": chat_count,
        "chat_limit": limit
    }

@app.post("/api/bots")
async def create_bot(bot: BotConfig, current_user: dict = Depends(get_current_user)):
    bot_id = str(uuid.uuid4())
    
    # Validate phone number for WhatsApp
    if bot.platform == "whatsapp" and bot.phone_number:
        if not validate_phone_number(bot.phone_number):
            raise HTTPException(status_code=400, detail="Invalid phone number format")
    
    bot_data = {
        "bot_id": bot_id,
        "user_id": current_user["user_id"],
        "bot_name": bot.bot_name,
        "platform": bot.platform,
        "api_key": bot.api_key,
        "webhook_url": bot.webhook_url,
        "ai_provider": bot.ai_provider,
        "ai_model": bot.ai_model,
        "ai_api_key": bot.ai_api_key,
        "system_message": bot.system_message,
        "auto_reply": bot.auto_reply,
        "phone_number": bot.phone_number,
        "phone_number_id": bot.phone_number_id,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    bot_configs_collection.insert_one(bot_data)
    
    return {"bot_id": bot_id, "message": "Bot created successfully"}

@app.get("/api/bots")
async def get_bots(current_user: dict = Depends(get_current_user)):
    bots = list(bot_configs_collection.find(
        {"user_id": current_user["user_id"]},
        {"_id": 0, "api_key": 0, "ai_api_key": 0}
    ))
    return {"bots": bots}

@app.get("/api/bots/{bot_id}")
async def get_bot(bot_id: str, current_user: dict = Depends(get_current_user)):
    bot = bot_configs_collection.find_one({
        "bot_id": bot_id,
        "user_id": current_user["user_id"]
    }, {"_id": 0})
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    return bot

@app.put("/api/bots/{bot_id}")
async def update_bot(bot_id: str, bot: BotConfig, current_user: dict = Depends(get_current_user)):
    # Validate phone number for WhatsApp
    if bot.platform == "whatsapp" and bot.phone_number:
        if not validate_phone_number(bot.phone_number):
            raise HTTPException(status_code=400, detail="Invalid phone number format")
    
    result = bot_configs_collection.update_one(
        {"bot_id": bot_id, "user_id": current_user["user_id"]},
        {"$set": bot.dict()}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    return {"message": "Bot updated successfully"}

@app.delete("/api/bots/{bot_id}")
async def delete_bot(bot_id: str, current_user: dict = Depends(get_current_user)):
    result = bot_configs_collection.delete_one({
        "bot_id": bot_id,
        "user_id": current_user["user_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    return {"message": "Bot deleted successfully"}

@app.post("/api/chat/send")
async def send_chat_message(message: ChatMessage, current_user: dict = Depends(get_current_user)):
    # Check user's chat limit
    chat_count = get_user_chat_count(current_user["user_id"])
    limit = get_user_limit(current_user["plan"])
    
    if chat_count >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Chat limit exceeded. Your plan allows {limit} messages per month."
        )
    
    # Get bot configuration
    bot = bot_configs_collection.find_one({"bot_id": message.bot_id})
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Prepare AI settings
    ai_settings = {
        "provider": bot.get("ai_provider", DEFAULT_AI_PROVIDER),
        "model": bot.get("ai_model", "gemini-2.0-flash"),
        "api_key": bot.get("ai_api_key", DEFAULT_AI_KEY),
        "system_message": bot.get("system_message", "You are a helpful assistant.")
    }
    
    # Send message to AI
    session_id = f"{current_user['user_id']}_{message.bot_id}"
    ai_response = await send_ai_message(message.message, ai_settings, session_id)
    
    # Save chat history
    chat_id = str(uuid.uuid4())
    chat_data = {
        "chat_id": chat_id,
        "user_id": current_user["user_id"],
        "bot_id": message.bot_id,
        "platform": message.platform,
        "sender_id": message.sender_id,
        "user_message": message.message,
        "ai_response": ai_response,
        "created_at": datetime.utcnow()
    }
    
    chat_history_collection.insert_one(chat_data)
    
    return {
        "chat_id": chat_id,
        "response": ai_response,
        "remaining_chats": limit - chat_count - 1
    }

@app.post("/api/chat/test")
async def test_chat_message(message: TestChatMessage, current_user: dict = Depends(get_current_user)):
    """Test chat message without saving to history or counting towards limit"""
    # Get bot configuration
    bot = bot_configs_collection.find_one({"bot_id": message.bot_id})
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Prepare AI settings
    ai_settings = {
        "provider": bot.get("ai_provider", DEFAULT_AI_PROVIDER),
        "model": bot.get("ai_model", "gemini-2.0-flash"),
        "api_key": bot.get("ai_api_key", DEFAULT_AI_KEY),
        "system_message": bot.get("system_message", "You are a helpful assistant.")
    }
    
    # Send message to AI
    session_id = f"test_{current_user['user_id']}_{message.bot_id}"
    ai_response = await send_ai_message(message.message, ai_settings, session_id)
    
    return {
        "response": ai_response,
        "is_test": True
    }

@app.get("/api/chat/history/{bot_id}")
async def get_chat_history(bot_id: str, current_user: dict = Depends(get_current_user)):
    history = list(chat_history_collection.find(
        {"bot_id": bot_id, "user_id": current_user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(100))
    
    return {"history": history}

@app.post("/api/phone/verify")
async def verify_phone_number(verification: PhoneNumberVerification, current_user: dict = Depends(get_current_user)):
    """Verify phone number for WhatsApp Business API"""
    # This is a placeholder - in real implementation, you would verify with WhatsApp API
    if not validate_phone_number(verification.phone_number):
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    
    # Simulate verification process
    if verification.verification_code == "123456":
        # Save verified phone number
        users_collection.update_one(
            {"user_id": current_user["user_id"]},
            {"$set": {"verified_phone": verification.phone_number}}
        )
        return {"message": "Phone number verified successfully", "verified": True}
    else:
        raise HTTPException(status_code=400, detail="Invalid verification code")

@app.get("/api/phone/send-code/{phone_number}")
async def send_verification_code(phone_number: str, current_user: dict = Depends(get_current_user)):
    """Send verification code to phone number"""
    if not validate_phone_number(phone_number):
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    
    # This is a placeholder - in real implementation, you would send SMS via WhatsApp API
    return {"message": "Verification code sent", "code": "123456"}  # Only for demo

# Webhook endpoints for different platforms
@app.post("/api/webhooks/whatsapp/{bot_id}")
async def whatsapp_webhook(bot_id: str, request: Request):
    """WhatsApp webhook endpoint"""
    body = await request.body()
    
    # Log webhook
    webhook_logs_collection.insert_one({
        "webhook_id": str(uuid.uuid4()),
        "platform": "whatsapp",
        "bot_id": bot_id,
        "payload": body.decode(),
        "created_at": datetime.utcnow()
    })
    
    # Process WhatsApp message (implement based on WhatsApp API)
    return {"status": "received"}

@app.post("/api/webhooks/telegram/{bot_id}")
async def telegram_webhook(bot_id: str, request: Request):
    """Telegram webhook endpoint"""
    body = await request.body()
    
    # Log webhook
    webhook_logs_collection.insert_one({
        "webhook_id": str(uuid.uuid4()),
        "platform": "telegram",
        "bot_id": bot_id,
        "payload": body.decode(),
        "created_at": datetime.utcnow()
    })
    
    # Process Telegram message (implement based on Telegram API)
    return {"status": "received"}

@app.post("/api/webhooks/line/{bot_id}")
async def line_webhook(bot_id: str, request: Request):
    """LINE webhook endpoint"""
    body = await request.body()
    
    # Log webhook
    webhook_logs_collection.insert_one({
        "webhook_id": str(uuid.uuid4()),
        "platform": "line",
        "bot_id": bot_id,
        "payload": body.decode(),
        "created_at": datetime.utcnow()
    })
    
    # Process LINE message (implement based on LINE API)
    return {"status": "received"}

@app.post("/api/webhooks/instagram/{bot_id}")
async def instagram_webhook(bot_id: str, request: Request):
    """Instagram webhook endpoint"""
    body = await request.body()
    
    # Log webhook
    webhook_logs_collection.insert_one({
        "webhook_id": str(uuid.uuid4()),
        "platform": "instagram",
        "bot_id": bot_id,
        "payload": body.decode(),
        "created_at": datetime.utcnow()
    })
    
    # Process Instagram message (implement based on Instagram API)
    return {"status": "received"}

@app.get("/api/webhooks/logs/{bot_id}")
async def get_webhook_logs(bot_id: str, current_user: dict = Depends(get_current_user)):
    """Get webhook logs for a bot"""
    logs = list(webhook_logs_collection.find(
        {"bot_id": bot_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(50))
    
    return {"logs": logs}

# AI Provider settings
@app.post("/api/ai/settings")
async def update_ai_settings(settings: AISettings, current_user: dict = Depends(get_current_user)):
    """Update user's default AI settings"""
    users_collection.update_one(
        {"user_id": current_user["user_id"]},
        {"$set": {
            "ai_provider": settings.provider,
            "ai_model": settings.model,
            "ai_api_key": settings.api_key,
            "ai_system_message": settings.system_message
        }}
    )
    
    return {"message": "AI settings updated successfully"}

@app.get("/api/ai/models")
async def get_ai_models():
    """Get available AI models for each provider"""
    models = {
        "openai": ["gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "o4-mini", "o3-mini", "o3", "o1-mini", "gpt-4o-mini", "gpt-4.5-preview", "gpt-4o", "o1", "o1-pro"],
        "anthropic": ["claude-sonnet-4-20250514", "claude-opus-4-20250514", "claude-3-7-sonnet-20250219", "claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022"],
        "gemini": ["gemini-2.5-flash-preview-04-17", "gemini-2.5-pro-preview-05-06", "gemini-2.0-flash", "gemini-2.0-flash-preview-image-generation", "gemini-2.0-flash-lite", "gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro"],
        "deepseek": ["deepseek-chat", "deepseek-coder"],
        "qwen": ["qwen-turbo", "qwen-max"],
        "kimi": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]
    }
    
    return {"models": models}

# Admin endpoints
@app.get("/api/admin/users")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """Get all users (superadmin only)"""
    if current_user["role"] != "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    users = list(users_collection.find(
        {},
        {"_id": 0, "password": 0}
    ).sort("created_at", -1))
    
    return {"users": users}

@app.get("/api/admin/bots")
async def get_all_bots(current_user: dict = Depends(get_current_user)):
    """Get all bots (superadmin only)"""
    if current_user["role"] != "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    pipeline = [
        {
            "$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "user_id",
                "as": "user"
            }
        },
        {
            "$project": {
                "_id": 0,
                "api_key": 0,
                "ai_api_key": 0,
                "user.password": 0
            }
        }
    ]
    
    bots = list(bot_configs_collection.aggregate(pipeline))
    
    return {"bots": bots}

@app.get("/api/admin/stats")
async def get_admin_stats(current_user: dict = Depends(get_current_user)):
    """Get admin statistics (superadmin only)"""
    if current_user["role"] != "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    # Count users by plan
    user_stats = list(users_collection.aggregate([
        {"$group": {"_id": "$plan", "count": {"$sum": 1}}}
    ]))
    
    # Count bots by platform
    bot_stats = list(bot_configs_collection.aggregate([
        {"$group": {"_id": "$platform", "count": {"$sum": 1}}}
    ]))
    
    # Total counts
    total_users = users_collection.count_documents({})
    total_bots = bot_configs_collection.count_documents({})
    total_chats = chat_history_collection.count_documents({})
    
    return {
        "total_users": total_users,
        "total_bots": total_bots,
        "total_chats": total_chats,
        "user_stats": user_stats,
        "bot_stats": bot_stats
    }

# Superadmin endpoints for Xendit settings
@app.post("/api/admin/xendit/settings")
async def update_xendit_settings(settings: XenditSettings, current_user: dict = Depends(get_current_user)):
    """Update Xendit settings (superadmin only)"""
    if current_user["role"] != "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    # Store Xendit settings in database
    db.xendit_settings.update_one(
        {"type": "settings"},
        {"$set": {
            "api_key": settings.api_key,
            "public_key": settings.public_key,
            "callback_token": settings.callback_token,
            "updated_at": datetime.utcnow()
        }},
        upsert=True
    )
    
    return {"message": "Xendit settings updated successfully"}

@app.get("/api/admin/xendit/settings")
async def get_xendit_settings(current_user: dict = Depends(get_current_user)):
    """Get Xendit settings (superadmin only)"""
    if current_user["role"] != "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    settings = db.xendit_settings.find_one({"type": "settings"})
    if not settings:
        return {"message": "No Xendit settings found"}
    
    return {
        "api_key": settings.get("api_key", ""),
        "public_key": settings.get("public_key", ""),
        "callback_token": settings.get("callback_token", ""),
        "updated_at": settings.get("updated_at")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)