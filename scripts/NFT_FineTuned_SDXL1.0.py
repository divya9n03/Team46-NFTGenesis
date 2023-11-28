import requests
import io
from PIL import Image

API_URL = "https://api-inference.huggingface.co/models/sarathAI/NFT-Genesis"
headers = {"Authorization": "Bearer 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"}
input="" #add prompt here
def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

image_bytes = query({
    "inputs": input,
})

if image_bytes.startswith(b'\xff\xd8'): 
    print("JPEG image detected")
elif image_bytes.startswith(b'\x89PNG\r\n\x1a\n'): 
    print("PNG image detected")
else:
    print("The response might not be an image or is in an unrecognized format.")

try:
    image = Image.open(io.BytesIO(image_bytes))
    image.save("output_image.jpg")
    print("Image saved as output_image.jpg. Please open this file to view the image.")
except IOError:
    print("Cannot open the image. The file might be corrupted or in an unsupported format.")

