import openai
import os
import base64
from dotenv import load_dotenv
from openai import AzureOpenAI
from PIL import Image



load_dotenv()

AZURE_OPENAI_API_IMG_KEY = os.getenv("AZURE_OPENAI_API_IMG_KEY")
AZURE_OPENAI_API_IMG_VERSION = os.getenv("AZURE_OPENAI_API_IMG_VERSION")
AZURE_OPENAI_API_IMG_DEPLOYMENT = os.getenv("AZURE_OPENAI_API_IMG_DEPLOYMENT")
AZURE_OPENAI_API_IMG_ENDPOINT = os.getenv("AZURE_OPENAI_API_IMG_ENDPOINT")

print(AZURE_OPENAI_API_IMG_KEY)
print(AZURE_OPENAI_API_IMG_VERSION)
print(AZURE_OPENAI_API_IMG_DEPLOYMENT)
print(AZURE_OPENAI_API_IMG_ENDPOINT)

client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_API_IMG_ENDPOINT,
    api_key=AZURE_OPENAI_API_IMG_KEY,
    api_version="2024-02-01"
)

def create_images():

    # response = client.responses.create(
    #     model=AZURE_OPENAI_API_DEPLOYMENT,
    #     input="Generate an image of gray tabby cat hugging an otterwith an organge scarf",
    #     tools=[{"type":"image_generation"}]
    # )

    # image_data = [
    #     output.result
    #     for output in response.output
    #     if output.type == "image_generation_call"
    # ]

    # if image_data:
    #     image_base64 = image_data[0]
    #     with open("cat_and_otter.png", "wb") as f:
    #         f.write(base64.b64decode(image_base64))

    result = client.images.generate(
        model=AZURE_OPENAI_API_IMG_DEPLOYMENT,
        prompt="a close-up of a bear walking through the forest",
        n=1,
        size="1024x1024",
        quality="high",
        output_format="png"
    )

    image_dir = os.path.join(os.curdir,"images")

    if not os.path.isdir(image_dir):
        os.mkdir(image_dir)

    image_path = os.path.join(image_dir, "generated_image.png")

    image_base64 = result.data[0].b64_json
    generated_image = base64.b64decode(image_base64)
    with open(image_path, "wb") as image_file:
        image_file.write(generated_image)

    image = Image.open(image_path)
    image.show()


if __name__ == "__main__":
    create_images()
    
