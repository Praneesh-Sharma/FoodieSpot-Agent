from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv, find_dotenv
import os

# Load environment variables
env_path = find_dotenv()
if not env_path:
    raise FileNotFoundError("⚠️ .env file not found! Ensure it exists in the project root.")

load_dotenv(env_path)

# Read database credentials
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Debugging - Print values to check if they are loaded
print(f"DB_NAME={DB_NAME}, DB_USER={DB_USER}, DB_HOST={DB_HOST}, DB_PORT={DB_PORT}")

# Ensure all variables are loaded
if not all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT]):
    raise ValueError("Missing one or more required database environment variables!")

# PostgreSQL Connection URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create an engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(bind=engine)

# Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
