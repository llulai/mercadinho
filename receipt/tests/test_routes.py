import json
import pytest
from flask.testing import FlaskClient
from io import BytesIO
from app import create_app
from datetime import datetime
from rapidfuzz import fuzz


# Function to check if two strings are similar
def are_strings_similar(str1, str2, threshold=85):
    """Return True if two strings are sufficiently similar based on the threshold."""
    similarity = fuzz.ratio(str1, str2)
    return similarity >= threshold


def check_store(expected, actual):
    if expected["cnpj"] != actual["cnpj"]:
        return False, f"CNPJ mismatch: expected {expected['cnpj']}, got {actual['cnpj']}"

    for key in ["name", "address"]:
        if not are_strings_similar(expected[key], actual[key],  50):
            return False, f"{key.capitalize()} mismatch: expected {expected[key]}, got {actual[key]}"

    return True, None


def are_skus_similar(sku1, sku2, threshold=90):
    """Check if two SKUs are similar with a slight difference, allowing up to one character difference."""
    similarity = fuzz.ratio(sku1, sku2)
    return similarity >= threshold


def check_product(expected_product, actual_product):
    # Check if SKU matches exactly or is close enough (allowing one character difference)
    if not are_skus_similar(expected_product["sku"], actual_product["sku"]):
        return False, f"SKU mismatch: expected {expected_product['sku']}, got {actual_product['sku']}"

    # Exact matches for key attributes
    for key in ["unit_price", "quantity", "total_price", "quantity_measure", "idx"]:
        if expected_product[key] != actual_product[key]:
            return False, f"{key.capitalize()} mismatch: expected {expected_product[key]}, got {actual_product[key]}"

    # Fuzzy matching for the product description
    if not are_strings_similar(expected_product["description"], actual_product["description"], 50):
        return False, f"Description mismatch: expected {expected_product['description']}, got {actual_product['description']}"

    return True, None


def check_products(expected_products, actual_products):
    successful_matches = 0
    total_products = len(expected_products)

    for expected_product, actual_product in zip(expected_products, actual_products):
        result, error = check_product(expected_product, actual_product)
        if result:
            successful_matches += 1
        else:
            print(f"Product mismatch: {error}")  # Adjust this to handle errors as needed

    return successful_matches / total_products > 0.8


def compare_dates(expected_datetime_str, actual_datetime_str):
    """Compare only the date portions of two datetime strings."""
    try:
        expected_date = datetime.fromisoformat(expected_datetime_str).date()
        actual_date = datetime.fromisoformat(actual_datetime_str).date()
    except ValueError:
        return False, f"Invalid date format: expected {expected_datetime_str}, actual {actual_datetime_str}"

    if expected_date != actual_date:
        return False, f"Date mismatch: expected {expected_date}, got {actual_date}"

    return True, None

def compare_parsed_data(expected, actual):
    """Compare two parsed data from receipts with fuzzy matching and detailed explanations."""
    if not isinstance(expected, dict) or not isinstance(actual, dict):
        return False, "Data types are not dictionaries"

    required_keys = ["receipt_datetime", "store", "products"]
    missing_keys = [key for key in required_keys if key not in expected]
    if missing_keys:
        return False, f"Missing required keys in expected data: {missing_keys}"

    # Compare only the date part of receipt_datetime
    date_match, date_error = compare_dates(expected["receipt_datetime"], actual["receipt_datetime"])
    if not date_match:
        return False, date_error

    # Check store information
    store_match, store_error = check_store(expected["store"], actual["store"])
    if not store_match:
        return False, f"Store mismatch: {store_error}"

    # Check product information
    products_match = check_products(expected["products"], actual["products"])
    if not products_match:
        return False, "Products do not match by 80% threshold"

    return True, None


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# Helper function to load an example image from the file system
def load_test_image(image_path):
    with open(image_path, 'rb') as image_file:
        return image_file.read()

def load_json_file(json_path):
    with open(json_path) as json_file:
        return json.load(json_file)


@pytest.mark.parametrize('idx', [
    (0),
    (1),
    (2)
])
def test_flask_api_extract(idx, client: FlaskClient):

    # Load an actual image file for the test
    image_path = f'data/img/{idx}.jpeg'
    json_path = f'data/json/{idx}.json'

    image_data = load_test_image(image_path)
    json_data = load_json_file(json_path)

    # Simulate file upload using the real image data
    data = {
        'receipt': (BytesIO(image_data), 'receipt_example.jpeg')
    }

    response = client.post('/extract', content_type='multipart/form-data', data=data)

    # the api call succeeded
    assert response.status_code == 200
    json_response = json.loads(response.get_json())

    # the data was correctly parsed
    result, message = compare_parsed_data(json_data, json_response)
    assert result, message
