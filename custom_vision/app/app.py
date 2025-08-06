import io
import json
import logging
from flask import Flask, request, jsonify
from PIL import Image
from predict import initialize, predict_image, predict_url

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

@app.route('/')
def index():
    return 'CustomVision.ai model host harness'

@app.route('/image', methods=['POST'])
@app.route('/<project>/image', methods=['POST'])
@app.route('/<project>/image/nostore', methods=['POST'])
@app.route('/<project>/classify/iterations/<publishedName>/image', methods=['POST'])
@app.route('/<project>/classify/iterations/<publishedName>/image/nostore', methods=['POST'])
@app.route('/<project>/detect/iterations/<publishedName>/image', methods=['POST'])
@app.route('/<project>/detect/iterations/<publishedName>/image/nostore', methods=['POST'])
def predict_image_handler(project=None, publishedName=None):
    try:
        if 'imageData' in request.files:
            imageData = request.files['imageData']
        elif 'imageData' in request.form:
            imageData = request.form['imageData']
        else:
            imageData = io.BytesIO(request.get_data())

        img = Image.open(imageData)
        results = predict_image(img)
        return jsonify(results)
    except Exception as e:
        print('IMAGE PROCESSING EXCEPTION:', str(e))
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

@app.route('/url', methods=['POST'])
@app.route('/<project>/url', methods=['POST'])
@app.route('/<project>/url/nostore', methods=['POST'])
@app.route('/<project>/classify/iterations/<publishedName>/url', methods=['POST'])
@app.route('/<project>/classify/iterations/<publishedName>/url/nostore', methods=['POST'])
@app.route('/<project>/detect/iterations/<publishedName>/url', methods=['POST'])
@app.route('/<project>/detect/iterations/<publishedName>/url/nostore', methods=['POST'])
def predict_url_handler(project=None, publishedName=None):
    try:
        raw_data = request.get_data().decode('utf-8')
        print(f'Incoming URL request data: {raw_data}')
        
        data = json.loads(raw_data)
        print(f'Parsed JSON data: {data}')
        
        image_url = data.get('url') or data.get('Url')
        print(f'Extracted image URL: {image_url}')
        
        if not image_url:
            return jsonify({'error': 'Missing url or Url field in request'}), 400
            
        results = predict_url(image_url)
        print(f'Prediction results: {len(results.get("predictions", []))} predictions')
        return jsonify(results)
    except json.JSONDecodeError as e:
        print('JSON DECODE ERROR:', str(e))
        return jsonify({'error': 'Invalid JSON format'}), 400
    except Exception as e:
        print('EXCEPTION:', str(e))
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    initialize()
    app.run(host='0.0.0.0', port=80)
