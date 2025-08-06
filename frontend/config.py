import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5000))
    
    CUSTOM_VISION_URL = os.getenv('CUSTOM_VISION_URL')
    CUSTOM_VISION_KEY = os.getenv('CUSTOM_VISION_KEY')
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.1))
    
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 5242880))
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'jpg,jpeg,png,webp').split(','))
    
    @classmethod
    def validate_config(cls):
        required_vars = ['CUSTOM_VISION_URL', 'CUSTOM_VISION_KEY']
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")

        return True

INGREDIENTS_TEMPLATE = {
    "apple": 0, "asparagus": 0, "avocado": 0, "banana": 0, "beef": 0,
    "beetroot": 0, "blueberry": 0, "bokchoy": 0, "broccoli": 0, "brown sugar": 0,
    "cabbage": 0, "cantaloupe": 0, "capsicum": 0, "carrot": 0, "cauliflower": 0,
    "cherry": 0, "chicken": 0, "chickpeas": 0, "chili pepper": 0, "coconut": 0,
    "corn": 0, "cucumber": 0, "egg": 0, "eggplant": 0, "fish": 0,
    "garlic": 0, "lemon": 0, "mango": 0, "oil": 0, "olive": 0,
    "olive oil": 0, "onion": 0, "orange": 0, "pasta": 0, "peach": 0,
    "peas": 0, "pineapple": 0, "potato": 0, "rice": 0, "salt": 0,
    "scallop": 0, "shrimp": 0, "spinach": 0, "sweet potato": 0, "tomato": 0,
    "watermelon": 0, "zucchini": 0
}
