import os
import uuid
from dotenv import load_dotenv
from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision.models.segmentation import deeplabv3_resnet50
from flask import Flask, request, render_template, session, redirect, url_for
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, template_folder="templates")
CORS(app)

# Load secrets securely from environment variables
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))  # Use a secret key from the environment or generate a random one

# Directory to save masks (use environment variable or default path)
MASKS_FOLDER = os.getenv("MASKS_FOLDER", os.path.join("static", "masks"))
os.makedirs(MASKS_FOLDER, exist_ok=True)

# Define device (CPU or GPU if available)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the DeepLabV3 model
model = deeplabv3_resnet50(pretrained=True).to(device)
model.eval()

@app.route("/")
def index():
    """Displays the homepage with the upload form."""
    return render_template("index.html")

@app.route("/waiting", methods=["POST"])
def waiting():
    """Processes the uploaded image and generates a segmentation mask."""

    if "image" not in request.files:
        return "No image received.", 400

    file = request.files["image"]
    if file.filename == "":
        return "Empty file.", 400

    # Load the image
    input_image = Image.open(file).convert("RGB")
    input_image = input_image.resize((600, 400))  # Resize for faster processing

    # Preprocessing
    preprocess = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    input_tensor = preprocess(input_image).unsqueeze(0).to(device)

    # Perform segmentation
    with torch.no_grad():
        output = model(input_tensor)['out'][0]
        output_predictions = output.argmax(0).byte().cpu().numpy()

    # Convert to image
    mask_image = Image.fromarray(output_predictions * 10).resize(input_image.size)

    # Save the mask
    mask_filename = f"{uuid.uuid4()}.png"
    mask_path = os.path.join(MASKS_FOLDER, mask_filename)
    mask_image.save(mask_path)

    # Store the mask filename in session
    session["mask_file"] = mask_filename
    return render_template("waiting.html")

@app.route("/response")
def response():
    """Displays the generated mask."""
    mask_filename = session.get("mask_file")
    if not mask_filename:
        return redirect(url_for("index"))

    mask_url = url_for("static", filename=f"masks/{mask_filename}")
    return render_template("response.html", mask_url=mask_url)

if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", 5005)),
        debug=os.getenv("FLASK_DEBUG", "False").lower() == "true"
    )
