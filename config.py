# config.py
# class Config:
#     OPENAI_API_KEY = "sk-proj-lMwVjk4HbsoAmI3Am0j2T3BlbkFJPg7N5ehkLOiFxTzQHzme s"

# class Config:
#     SECRET_KEY = 'your_secret_key_here'
#     SQLALCHEMY_DATABASE_URI = 'sqlite:///your_database.db'
#     OPENAI_API_KEY = 'sk-proj-lMwVjk4HbsoAmI3Am0j2T3BlbkFJPg7N5ehkLOiFxTzQHzme'
    
import os

class Config:
    # Secret key for sessions and CSRF protection, it should be set in the environment
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_default_secret_key_here')

    # Database URI, typically set as an environment variable for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///your_database.db')
    
    # Disables modification tracking for the database (optional, but can reduce overhead)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OpenAI API key, which should be set in the environment for security
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'sk-proj-lMwVjk4HbsoAmI3Am0j2T3BlbkFJPg7N5ehkLOiFxTzQHzme')

    UPLOAD_FOLDER = 'uploads/'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}  # Define allowed file extensions
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max file size (16 MB)
