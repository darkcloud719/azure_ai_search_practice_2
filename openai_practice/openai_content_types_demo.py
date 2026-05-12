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

openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.azure_endpoint = os.getenv("AZURE_OPENAI_API_ENDPOINT")
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
openai.api_type = "azure"

# TEXT + IMAGE example
# This example demonstrates how to send a message that includes both text and an image URL. The model will process the text and the image together to generate a response.
def test_text_and_image():
    print("\n=== TEXT + IMAGE EXAMPLE ===")
    
    response = openai.chat.completions.create(
        model = os.getenv("AZURE_OPENAI_API_DEPLOYMENT"),
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe what you see in this image."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://api.nga.gov/iiif/a2e6da57-3cd1-4235-b20e-95dcaefed6c8/full/!800,800/0/default.jpg"
                        }
                    }
                ]
            }
        ]
    )

    print("Model Output:")
    print(response.choices[0].message.content)

# AUDIO INPUT example
# This example demonstrates how to structure a message that includes an audio input. The audio data must be base64 encoded, and the model will process the audio content accordingly. Note that this is a schema demonstration and does not include actual audio data or processing.
def test_input_audio():
    print("\n=== AUDIO INPUT EXAMPLE ===")

    # NOTE:
    # input_audio requires base64 encoded audio data
    # This is only a schema demonstration

    

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": "BASE64_ENCODED_AUDIO_DATA",
                        "format": "wav"
                    }
                }
            ]
        }
    ]

    print("Input audio message structure:")
    print(messages)

def test_file_input():
    print("\n=== FILE INPUT EXAMPLE ===")

    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_API_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION
    )

    # file = client.files.create(
    #     file=open("test.pdf", "rb"),
    #     purpose="assistants"
    # )

    # print(file.id)

    # files = client.files.list()

    # for f in files.data:
    #     print(f.id, f.filename)

    files = client.files.list()

    for f in files.data:
        print(f"Deleting file: {f.id} - {f.filename}")

        response = client.files.delete(f.id)

        print(response)




if __name__ == "__main__":
    # test_text_and_image()
    test_file_input()