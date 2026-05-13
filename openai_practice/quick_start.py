"""
FILE: quick_start.py
DESCRIPTION: This file contains quick start examples for using the Azure OpenAI client to send messages with different content 
    types, including text, images, and files. The examples demonstrate how to structure the input messages and how to handle
    the responses from the model. The code also includes examples of how to upload files directly to the Azure OpenAI service
    and use them as input in messages.
USAGE: 
    1. Ensure you have the necessary environment variables set for Azure OpenAI API key, endpoint, version, and deployment.
"""
import openai
import os
import base64
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_API_DEPLOYMENT = os.getenv("AZURE_OPENAI_API_DEPLOYMENT")
AZURE_OPENAI_API_ENDPOINT = os.getenv("AZURE_OPENAI_API_ENDPOINT")

client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_API_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2025-03-01-preview"
)

# This example demonstrates how to send a message that includes both text and an image URL. The model will process the text and the image together to generate a response.
def upload_image_by_url():
    
    response = client.responses.create(
        model=AZURE_OPENAI_API_DEPLOYMENT,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "What teams are playing in this image?"
                    },
                    {
                        "type": "input_image",
                        "image_url": "https://api.nga.gov/iiif/a2e6da57-3cd1-4235-b20e-95dcaefed6c8/full/!800,800/0/default.jpg"
                    }
                ]
            }
        ]
    )

    print(response.output_text)

# This example demonstrates how to send a message that includes both text and a file URL. The model will process the text and the file together to generate a response.
def upload_file_by_image():
    
    response = client.responses.create(
        model=AZURE_OPENAI_API_DEPLOYMENT,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Analyze the letter and provide a summary of the key points."
                    },
                    {
                        "type": "input_file",
                        "file_url": "https://www.berkshirehathaway.com/letters/2024ltr.pdf"
                    }
                ]
            }
        ]
    )

    print(response.output_text)

# This example demonstrates how to upload a file directly to the Azure OpenAI service and use it as input in a message. The file will be processed by the model, and the response will be generated based on the content of the uploaded file.
def upload_own_files():

    file = client.files.create(
        file=open("test.pdf", "rb"),
        purpose="assistants"
    )

    response = client.responses.create(
        model=AZURE_OPENAI_API_DEPLOYMENT,
        input=[
            {
                "role":"user",
                "content":[
                    {
                        "type":"input_file",
                        "file_id":file.id
                    },
                    {
                        "type":"input_text",
                        "text":"What's the answer to question seventeen?"
                    }
                ]
            }
        ]
    )

    print(response.output_text)

def upload_own_files_by_base64():

    with open("test.pdf", "rb") as f:
        data = f.read()

    base64_string = base64.b64encode(data).decode("utf-8")

    response = client.responses.create(
        model=AZURE_OPENAI_API_DEPLOYMENT,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "filename": "test.pdf",
                        "file_data": f"data:application/pdf;base64,{base64_string}",
                    },
                    {
                        "type":"input_text",
                        "text":"What's the answer to question seventeen?"
                    }
                ]
            }
        ]
    )

    print(response.output_text)
    


if __name__ == "__main__":
    # upload_image_by_url()
    # upload_file_by_image()
    # upload_own_files()
    upload_own_files_by_base64()