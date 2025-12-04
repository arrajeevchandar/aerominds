import requests
import os

# Path to the sample image
image_path = r"C:\Users\arras\.gemini\antigravity\brain\fd00c44b-4e57-477f-bfbb-1d731bbd1341\sample_drone_view_1764868661498.png"
url = "http://127.0.0.1:8000/upload"

if not os.path.exists(image_path):
    print(f"Error: Image not found at {image_path}")
    exit(1)

print(f"Testing upload to {url}...")
try:
    with open(image_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
    
    print(f"Status Code: {response.status_code}")
    if response.ok:
        print("Response JSON:", response.json())
    else:
        print("Response Text:", response.text)

except Exception as e:
    print(f"Exception occurred: {e}")
