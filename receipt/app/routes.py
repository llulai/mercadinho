from flask import Blueprint, request, jsonify
from app.services import extract_text_from_receipt, extract_json_from_text

receipt_routes = Blueprint('receipt_routes', __name__)

@receipt_routes.route('/extract', methods=['POST'])
def extract_receipt_info():
    if 'receipt' not in request.files:
        return jsonify({"error": "No receipt file provided"}), 400

    receipt_file = request.files['receipt']
    image_content = receipt_file.read()

    # Step 1: Extract text using Google Cloud Document AI
    extracted_text = extract_text_from_receipt(image_content)

    # Step 2: Parse extracted text using ChatGPT to extract JSON structure
    parsed_json = extract_json_from_text(extracted_text)

    return jsonify(parsed_json)

