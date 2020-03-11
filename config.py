# Database connection variables
from dotenv import load_dotenv
load_dotenv()
import os

# Database connetion
HOST=os.getenv('HOST')
DATABASE=os.getenv('DATABASE')
PASSWORD=os.getenv('PASSWORD')
USER=os.getenv('USER')
