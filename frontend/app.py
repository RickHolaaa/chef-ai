import logging
from typing import List, Dict, Any, Optional
from werkzeug.datastructures import FileStorage
from flask import Flask, render_template, request, jsonify
import requests
from requests.exceptions import RequestException, Timeout
from PIL import Image
from io import BytesIO

from config import Config, INGREDIENTS_TEMPLATE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('app.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

try:
    Config.validate_config()
    logger.info("Configuration validated successfully")
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    raise

app.config['MAX_CONTENT_LENGTH'] = Config.MAX_FILE_SIZE
CONFIDENCE_THRESHOLD = Config.CONFIDENCE_THRESHOLD

def validate_image_file(file: FileStorage) -> Optional[str]:
    if not file or not file.filename:
        return "No file selected"
    
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if file_ext not in Config.ALLOWED_EXTENSIONS:
        return f"Unsupported format. Accepted formats: {', '.join(Config.ALLOWED_EXTENSIONS)}"
    
    if hasattr(file, 'content_length') and file.content_length > Config.MAX_FILE_SIZE:
        return f"File too large. Maximum size: {Config.MAX_FILE_SIZE // (1024*1024)}MB"
    
    return None

def validate_image_url(url: str) -> Optional[str]:
    if not url or not url.strip():
        return "Missing URL"
    
    if not url.startswith(('http://', 'https://')):
        return "Invalid URL (must start with http:// or https://)"
    
    return None

def detect_ingredients_from_url(image_url: str) -> List[Dict[str, Any]]:
    headers = {
        "Prediction-Key": Config.CUSTOM_VISION_KEY,
        "Content-Type": "application/json"
    }
    payload = {"Url": image_url}
    
    try:
        logger.info(f"Analyzing image from URL: {image_url[:50]}...")
        response = requests.post(Config.CUSTOM_VISION_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        predictions = result.get("predictions", [])
        
        detected_ingredients = [
            {"name": pred["tagName"], "probability": pred["probability"]}
            for pred in predictions if pred["probability"] >= CONFIDENCE_THRESHOLD
        ]
        
        logger.info(f"Ingredients detected: {len(detected_ingredients)}")
        return detected_ingredients
        
    except (Timeout, RequestException) as e:
        logger.error(f"Error calling Custom Vision: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during ingredient detection: {e}")
        return []

def detect_ingredients_from_file(image_file: FileStorage) -> List[Dict[str, Any]]:
    headers = {
        "Prediction-Key": Config.CUSTOM_VISION_KEY,
        "Content-Type": "application/octet-stream"
    }
    
    try:
        logger.info(f"Analyzing uploaded image: {image_file.filename}")
        image_data = image_file.read()
        
        try:
            Image.open(BytesIO(image_data)).verify()
        except Exception:
            logger.warning("Uploaded file is not a valid image")
            return []
        
        file_url = (Config.CUSTOM_VISION_URL.replace("/url", "/image") 
                   if "/url" in Config.CUSTOM_VISION_URL 
                   else f"{Config.CUSTOM_VISION_URL.rstrip('/')}/image")
        
        response = requests.post(file_url, data=image_data, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        predictions = result.get("predictions", [])
        
        detected_ingredients = [
            {"name": pred["tagName"], "probability": pred["probability"]}
            for pred in predictions if pred["probability"] >= CONFIDENCE_THRESHOLD
        ]
        
        logger.info(f"Ingredients detected: {len(detected_ingredients)}")
        return detected_ingredients
        
    except (Timeout, RequestException) as e:
        logger.error(f"Error calling Custom Vision: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during ingredient detection: {e}")
        return []

def create_ingredients_dict(detected_ingredients: List[Dict[str, Any]]) -> Dict[str, Any]:
    ingredients_dict = INGREDIENTS_TEMPLATE.copy()
    
    for ingredient in detected_ingredients:
        ingredient_name = ingredient["name"].lower()
        if ingredient_name in ingredients_dict:
            ingredients_dict[ingredient_name] = 1
    
    active_ingredients = sum(v for v in ingredients_dict.values() if isinstance(v, (int, float)))
    logger.info(f"Ingredients dictionary created with {active_ingredients} active ingredients")
    return ingredients_dict

def get_recipe_predictions(ingredients_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    try:
        logger.info("Generating local recipe suggestions")
        
        active_ingredients = [ingredient for ingredient, value in ingredients_dict.items() 
                            if isinstance(value, (int, float)) and value == 1]
        
        logger.info(f"Active ingredients for suggestion: {active_ingredients}")
        
        recipe_database = {
            "Tomato Salad": {
                "ingredients": ["tomato", "olive oil", "salt", "onion"],
                "description": "Fresh tomato salad"
            },
            "Vegetable Omelet": {
                "ingredients": ["egg", "tomato", "onion", "salt", "oil"],
                "description": "Nutritious omelet with fresh vegetables"
            },
            "Stir-fried Vegetables": {
                "ingredients": ["carrot", "broccoli", "onion", "garlic", "oil"],
                "description": "Asian-style sautéed vegetables"
            },
            "Fruit Salad": {
                "ingredients": ["apple", "banana", "orange", "mango"],
                "description": "Fresh fruit medley"
            },
            "Vegetable Curry": {
                "ingredients": ["potato", "carrot", "onion", "garlic", "coconut"],
                "description": "Spicy vegetarian curry"
            },
            "Guacamole": {
                "ingredients": ["avocado", "tomato", "onion", "garlic", "lemon"],
                "description": "Mexican avocado sauce"
            },
            "Green Salad": {
                "ingredients": ["spinach", "cucumber", "tomato", "olive oil"],
                "description": "Light and refreshing salad"
            },
            "Vegetable Soup": {
                "ingredients": ["carrot", "potato", "onion", "garlic", "salt"],
                "description": "Comforting vegetable soup"
            },
            "Tropical Smoothie": {
                "ingredients": ["mango", "pineapple", "banana", "coconut"],
                "description": "Exotic fruit beverage"
            },
            "Ratatouille": {
                "ingredients": ["eggplant", "zucchini", "tomato", "onion", "garlic"],
                "description": "Traditional French vegetable dish"
            },
            "Fried Rice": {
                "ingredients": ["rice", "egg", "carrot", "peas", "onion"],
                "description": "Stir-fried rice with vegetables"
            },
            "Chicken Salad": {
                "ingredients": ["chicken", "tomato", "cucumber", "olive oil"],
                "description": "Protein-rich chicken salad"
            }
        }
        
        recipe_scores = []
        for recipe_name, recipe_data in recipe_database.items():
            recipe_ingredients = recipe_data["ingredients"]
            matching_ingredients = len(set(active_ingredients) & set(recipe_ingredients))
            
            if matching_ingredients > 0:
                score = matching_ingredients / len(recipe_ingredients)
                recipe_scores.append((recipe_name, score, matching_ingredients, recipe_data["description"]))
        
        recipe_scores.sort(key=lambda x: (x[1], x[2]), reverse=True)
        
        formatted_recipes = [
            {
                "position": i + 1,
                "name": recipe_name,
                "score": score,
                "matching_ingredients": matching_count,
                "description": description
            }
            for i, (recipe_name, score, matching_count, description) in enumerate(recipe_scores[:10])
        ]
        
        logger.info(f"Suggested recipes: {len(formatted_recipes)}")
        return formatted_recipes
        
    except Exception as e:
        logger.error(f"Error generating recipe suggestions: {e}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manual')
def manual():
    return render_template('manual.html')

@app.route('/get_ingredients', methods=['GET'])
def get_ingredients():
    try:
        ingredients = [key for key in INGREDIENTS_TEMPLATE.keys()]
        logger.info(f"Ingredients list requested: {len(ingredients)} ingredients")
        return jsonify({"ingredients": sorted(ingredients)})
    except Exception as e:
        logger.error(f"Error retrieving ingredients: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/analyze_manual', methods=['POST'])
def analyze_manual():
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
            
        data = request.get_json()
        selected_ingredients = data.get('ingredients', [])
        
        if not selected_ingredients:
            return jsonify({"error": "No ingredients selected"}), 400
        
        if not isinstance(selected_ingredients, list):
            return jsonify({"error": "Invalid ingredients format"}), 400
        
        logger.info(f"Manual analysis for {len(selected_ingredients)} ingredients")
        
        ingredients_dict = INGREDIENTS_TEMPLATE.copy()
        valid_ingredients = []
        for ingredient in selected_ingredients:
            if ingredient in ingredients_dict:
                ingredients_dict[ingredient] = 1
                valid_ingredients.append(ingredient)
        
        if not valid_ingredients:
            return jsonify({"error": "No valid ingredients selected"}), 400
        
        recipe_predictions = get_recipe_predictions(ingredients_dict)
        
        if not recipe_predictions:
            return jsonify({"error": "No recipes found for these ingredients"}), 404
        
        return jsonify({
            "selected_ingredients": valid_ingredients,
            "recipe_predictions": recipe_predictions
        })
    
    except Exception as e:
        logger.error(f"Error during manual analysis: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'file' in request.files:
            image_file = request.files['file']
            validation_error = validate_image_file(image_file)
            if validation_error:
                return jsonify({"error": validation_error}), 400
            detected_ingredients = detect_ingredients_from_file(image_file)
            
        elif request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
            if not (data and 'url' in data and data['url']):
                return jsonify({"error": "Missing image URL"}), 400
            
            validation_error = validate_image_url(data['url'])
            if validation_error:
                return jsonify({"error": validation_error}), 400
            detected_ingredients = detect_ingredients_from_url(data['url'])
        else:
            return jsonify({"error": "No image provided (file or URL)"}), 400
        
        if not detected_ingredients:
            return jsonify({"error": "No ingredients detected with current confidence threshold"}), 404
        
        ingredients_dict = create_ingredients_dict(detected_ingredients)
        recipe_predictions = get_recipe_predictions(ingredients_dict)
        
        if not recipe_predictions:
            return jsonify({"error": "No recipes found for these ingredients"}), 404
        
        return jsonify({
            "ingredients": detected_ingredients,
            "recipes": recipe_predictions
        })
    
    except Exception as e:
        logger.error(f"Error during image analysis: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/config', methods=['GET', 'POST'])
def config():
    global CONFIDENCE_THRESHOLD
    
    if request.method == 'GET':
        return jsonify({
            "confidence_threshold": CONFIDENCE_THRESHOLD,
            "confidence_threshold_percent": f"{CONFIDENCE_THRESHOLD*100:.0f}%",
            "description": "Minimum confidence threshold for ingredient detection",
            "max_file_size_mb": Config.MAX_FILE_SIZE // (1024*1024),
            "allowed_extensions": list(Config.ALLOWED_EXTENSIONS)
        })
    
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
            
        data = request.get_json()
        new_threshold = data.get('threshold')
        
        if new_threshold is None:
            return jsonify({"error": "Missing 'threshold' parameter"}), 400
        
        try:
            new_threshold = float(new_threshold)
        except (ValueError, TypeError):
            return jsonify({"error": "Threshold must be a number"}), 400
            
        if not (0.0 <= new_threshold <= 1.0):
            return jsonify({"error": "Threshold must be between 0.0 and 1.0"}), 400
        
        old_threshold = CONFIDENCE_THRESHOLD
        CONFIDENCE_THRESHOLD = new_threshold
        
        logger.info(f"Confidence threshold updated: {old_threshold} -> {new_threshold}")
        
        return jsonify({
            "message": "Confidence threshold updated",
            "old_threshold": old_threshold,
            "new_threshold": CONFIDENCE_THRESHOLD,
            "new_threshold_percent": f"{CONFIDENCE_THRESHOLD*100:.0f}%"
        })
        
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health')
def health():
    try:
        return jsonify({
            "status": "healthy",
            "confidence_threshold": CONFIDENCE_THRESHOLD,
            "confidence_threshold_percent": f"{CONFIDENCE_THRESHOLD*100:.0f}%",
            "custom_vision_configured": bool(Config.CUSTOM_VISION_URL and Config.CUSTOM_VISION_KEY),
            "recipe_system": "local",
            "max_file_size_mb": Config.MAX_FILE_SIZE // (1024*1024),
            "allowed_extensions": list(Config.ALLOWED_EXTENSIONS)
        })
    except Exception as e:
        logger.error(f"Error during health check: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": "Configuration error"
        }), 500

@app.errorhandler(413)
def file_too_large(error):
    logger.warning("Attempt to upload a file that is too large")
    return jsonify({"error": f"File too large. Maximum size: {Config.MAX_FILE_SIZE // (1024*1024)}MB"}), 413

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Malformed request"}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info("Starting Chef AI application")
    logger.info(f"Configuration: Debug={Config.DEBUG}, Host={Config.HOST}, Port={Config.PORT}")
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
