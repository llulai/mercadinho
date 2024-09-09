import os
from google.cloud import documentai_v1beta3 as documentai
from google.oauth2 import service_account
from dotenv import load_dotenv
from models import Receipt
from openai import OpenAI

load_dotenv('.env')

# google cloud setup
location = 'us' 
project_id = os.getenv('GOOGLE_DOC_AI_PROJECT')
processor_id = os.getenv('GOOGLE_DOC_AI_ID')
service_account_path = os.getenv("GOOGLE_SERVICE_KEY_PATH")
credentials = service_account.Credentials.from_service_account_file(service_account_path)
gcp_client = documentai.DocumentProcessorServiceClient(credentials=credentials)

# open ai setup
api_key = os.getenv('OPENAI_API_KEY')
open_ai_client = OpenAI(api_key=api_key)


def extract_text_from_receipt(image_content):
    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"
    document = {"content": image_content, "mime_type": "image/jpeg"}  # Change mime_type based on input
    request = {"name": name, "raw_document": document}
    result = gcp_client.process_document(request=request)
    return result.document.text


def extract_json_from_text(text):
    completion = open_ai_client.beta.chat.completions.parse(
        model='gpt-4o-mini',
        # model='gpt-4o-2024-08-06',
        messages=[
            {"role": "system",
             "content": "You are an expert at structured data extraction. You will be given unstructured text from a supermarket receipt and should convert it into the given structure. The receipt has two rows per product, the first row contains the number of the item on the list, the sku and the description, the second row contains the quantity, quantity measurement, unit price, tare and total price. Parse the datetime in yyyy-mm-ddTHH:mm:ss format to determine the date and time.",},
            {"role": "user", "content": text}
        ],
        response_format=Receipt,
        max_tokens=1000
    )

    receipt = completion.choices[0].message.parsed
    return receipt.model_dump_json()
