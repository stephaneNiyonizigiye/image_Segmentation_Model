# Optimized Flask App for Mask R-CNN Roof Segmentation

import os
import uuid
from dotenv import load_dotenv
from PIL import Image
import torch
import torchvision.transforms as transforms
from flask import Flask, request, render_template, session, redirect, url_for
from flask_cors import CORS
from torchvision.models.detection import MaskRCNN
from torchvision.models.detection.backbone_utils import resnet_fpn_backbone
import torchvision
import numpy as np

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, template_folder="templates")
CORS(app)

app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))
MASKS_FOLDER = os.getenv("MASKS_FOLDER", os.path.join("static", "masks"))
os.makedirs(MASKS_FOLDER, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load trained Mask R-CNN model
backbone = resnet_fpn_backbone('resnet18', pretrained=False)
model = MaskRCNN(backbone, num_classes=2)
model.load_state_dict(torch.load("Segmentation.Keras", map_location=device))
model.to(device)
model.eval()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/waiting", methods=["POST"])
def waiting():
    if "image" not in request.files:
        return "No image received.", 400

    file = request.files["image"]
    if file.filename == "":
        return "Empty file.", 400

    input_image = Image.open(file).convert("RGB")
    resized_image = input_image.resize((256, 256))
    input_tensor = transforms.ToTensor()(resized_image).unsqueeze(0).to(device)

    with torch.no_grad():
        prediction = model(input_tensor)[0]

    mask = torch.zeros_like(prediction['masks'][0][0])
    for i, m in enumerate(prediction['masks']):
        if prediction['scores'][i] > 0.5:
            mask = torch.logical_or(mask, m[0] > 0.5)

    mask_np = mask.cpu().numpy().astype(np.uint8) * 255
    mask_img = Image.fromarray(mask_np).resize(input_image.size)

    mask_filename = f"{uuid.uuid4()}.png"
    mask_path = os.path.join(MASKS_FOLDER, mask_filename)
    mask_img.save(mask_path)

    session["mask_file"] = mask_filename
    return render_template("waiting.html")

@app.route("/response")
def response():
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