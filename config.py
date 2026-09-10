from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Moodle API Configuration
MOODLE_API_URL = os.getenv('MOODLE_API_URL')
MOODLE_API_TOKEN = os.getenv('MOODLE_API_TOKEN')

# Power Automate Configuration
POWER_AUTOMATE_URL = os.getenv('POWER_AUTOMATE_URL')

# Database Configuration
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

# Flask Application Configurations
DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1']
PORT = int(os.getenv('FLASK_PORT', 5000))

# Additional Settings
TIMEOUT = int(os.getenv('TIMEOUT', 30))
