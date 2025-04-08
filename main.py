from fastapi import FastAPI, Depends, HTTPException, status, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import User, Role
from auth import create_access_token, verify_password, decode_token, get_password_hash
from database import SessionLocal, engine
from typing import List
import logging
import aio_pika
# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI and create tables
app = FastAPI()

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User Pydantic models
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    full_name: str
    password: str


# Publish message to RabbitMQ
async def publish_message_to_rabbitmq(message: str):
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")  # Change with your credentials
    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=message.encode()),
            routing_key="user.registration",
        )

# User Registration
@app.post("/register")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if the user already exists
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash the password and create the user
        hashed_password = get_password_hash(user.password)
        db_user = User(email=user.email, hashed_password=hashed_password, full_name=user.full_name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logging.info(f"User {user.email} registered successfully")
        # Publish a message to RabbitMQ queue after registration
        await publish_message_to_rabbitmq(f"New user registered: {user.email}")
        return {"message": "User registered successfully"}
    except Exception as e:
        logging.error(f"Error during user registration: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# User Login
@app.post("/login")
async def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.email == form_data.email).first()
        if db_user is None or not verify_password(form_data.password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token(data={"sub": db_user.email})
        logging.info(f"User {form_data.email} logged in successfully")
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logging.error(f"Error during user login: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Profile Retrieval
@app.get("/profile")
async def get_user_profile(token: str = Depends(decode_token), db: Session = Depends(get_db)):
    try:
        if token is None:
            raise HTTPException(status_code=403, detail="Invalid token")
        
        db_user = db.query(User).filter(User.email == token['sub']).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        logging.info(f"User profile retrieved for {token['sub']}")
        return db_user
    except Exception as e:
        logging.error(f"Error retrieving user profile: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Profile Update
@app.put("/profile")
async def update_user_profile(user: UserUpdate, token: str = Depends(decode_token), db: Session = Depends(get_db)):
    try:
        if token is None:
            raise HTTPException(status_code=403, detail="Invalid token")
        
        db_user = db.query(User).filter(User.email == token['sub']).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        db_user.full_name = user.full_name
        db_user.hashed_password = get_password_hash(user.password)
        db.commit()
        db.refresh(db_user)
        logging.info(f"User {token['sub']} profile updated successfully")
        return db_user
    except Exception as e:
        logging.error(f"Error updating user profile for {token['sub']}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
