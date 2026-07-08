"""
image_moderator.py
-------------------
Analyzes IMAGE uploads and decides: approved / flagged / rejected.

IMPORTANT, READ THIS FIRST:
Detecting actual inappropriate image *content* (nudity, gore, violence)
requires a trained computer-vision model. In the original design this is
Azure AI Vision. Running a full vision model locally (e.g. via PyTorch)
needs large downloads and a GPU for speed, which isn't practical for a demo
project you'll run in VS Code.

So, this module does several things:
1. Real, working checks that don't need any ML model:
     - file type / format validation
     - file size checks (very large/small files are suspicious)
     - image dimension checks (e.g. 1x1 tracking pixels)
     - basic corruption check (can the file even be opened as an image?)
     - filename check: flags images with names containing keywords like 
       "offensive", "nsfw", "adult", "explicit", etc. (useful for testing)
2. Placeholder for content analysis (_analyze_image_content):
     - Currently empty but ready for Azure AI Vision integration
     - Can be enhanced with histogram analysis or ML models
3. A ready-made hook (`analyze_with_azure_vision`) where you drop in your
   Azure AI Vision key to get REAL content-safety analysis (adult/racy/gory
   content detection) with just a few lines of code.

HOW TO TEST:
To test offensive image detection, rename your test image to include keywords:
  - offensive_image.jpg       -> will be flagged as "offensive"
  - nsfw_photo.png            -> will be flagged as "nsfw"
  - adult_content.jpg         -> will be flagged as "adult"
  - any_normal_image.jpg      -> will be approved

This keeps the project honest: it clearly shows what's really implemented
vs. what's a placeholder for the full Azure service, which is exactly the
kind of thing you can explain confidently in your presentation/viva.
"""

from PIL import Image
import os
import re


ALLOWED_FORMATS = {"JPEG", "PNG", "GIF", "WEBP"}

# Keywords that suggest the image is offensive/NSFW
OFFENSIVE_KEYWORDS = {
    "offensive", "nsfw", "adult", "nude", "porn", "explicit", "xxx",
    "sexual", "violence", "gore", "violent", "illegal", "banned",
    "restricted", "inappropriate", "mature", "graphic"
}


def _check_filename_for_offensive_content(filename: str) -> list:
    """
    Check if the filename contains keywords suggesting offensive content.
    Returns a list of matched keywords.
    """
    matched = []
    filename_lower = filename.lower()
    
    for keyword in OFFENSIVE_KEYWORDS:
        # Use word boundaries to match whole words
        if re.search(r'\b' + re.escape(keyword) + r'\b', filename_lower):
            matched.append(f"filename_contains_{keyword}")
    
    return matched


def _analyze_image_content(img: Image.Image) -> list:
    """
    Perform basic content analysis on image using PIL.
    This is a placeholder for real content detection (which would use Azure AI Vision).
    
    Can detect:
    - Very dark/bright images (suspicious)
    - Extreme saturation patterns
    - Specific color distributions
    
    For now, returns empty list (no additional flagging beyond filename check).
    Real implementation would use Azure AI Vision or a trained ML model.
    """
    categories = []
    
    # Convert to RGB if needed
    if img.mode != "RGB":
        try:
            img = img.convert("RGB")
        except:
            pass
    
    # TODO: Add real content detection using:
    # - Azure AI Vision (adult/racy/gory content detection)
    # - Or a lightweight model from transformers/huggingface
    # - Or advanced histogram analysis
    
    # Placeholder: No content-based detection yet
    return categories


def analyze_image(file_path: str, size_flag_mb: float = 8.0) -> dict:
    """
    Main entry point. Analyzes an image file on disk and returns:

    {
        "decision": "approved" | "flagged" | "rejected",
        "confidence_score": float,
        "categories": [list of reasons],
    }
    """
    categories = []

    if not os.path.exists(file_path):
        return {
            "decision": "rejected",
            "confidence_score": 1.0,
            "categories": ["file_not_found"],
        }

    # Get the filename (last part of path)
    filename = os.path.basename(file_path)
    
    # Check for offensive keywords in filename
    offensive_in_filename = _check_filename_for_offensive_content(filename)
    if offensive_in_filename:
        categories.extend(offensive_in_filename)

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

    # 1. Try to open the image - catches corrupted / fake image files
    try:
        with Image.open(file_path) as img:
            img.verify()  # checks the file isn't broken
        with Image.open(file_path) as img:  # reopen after verify()
            fmt = img.format
            width, height = img.size
            # Perform content analysis on the image
            content_categories = _analyze_image_content(img)
            categories.extend(content_categories)
    except Exception:
        return {
            "decision": "rejected",
            "confidence_score": 0.95,
            "categories": ["corrupted_or_invalid_image"],
        }

    # 2. Format check
    if fmt not in ALLOWED_FORMATS:
        categories.append("unsupported_format")

    # 3. Suspicious dimensions (e.g. 1x1 tracking pixels used for spam/abuse)
    if width <= 2 or height <= 2:
        categories.append("suspicious_dimensions")

    # 4. Large file size -> flag for manual review (bandwidth/abuse concern)
    if file_size_mb > size_flag_mb:
        categories.append("large_file_size")

    # ---- Decision logic ----
    if "corrupted_or_invalid_image" in categories or "unsupported_format" in categories:
        decision = "rejected"
        confidence = 0.9
    elif categories:
        decision = "flagged"
        confidence = 0.6
    else:
        decision = "approved"
        confidence = 0.95

    return {
        "decision": decision,
        "confidence_score": round(confidence, 2),
        "categories": categories,
        "metadata": {"format": fmt, "width": width, "height": height, "size_mb": round(file_size_mb, 2)},
    }



def analyze_with_azure_vision(file_path: str) -> dict:
    """
    STUB / PLACEHOLDER for real Azure AI Vision content-safety analysis.

    To use this for real:
    1. pip install azure-ai-vision-imageanalysis
    2. Fill in AZURE_VISION_KEY / AZURE_VISION_ENDPOINT in config.py
    3. Uncomment and complete the code below.

    from azure.ai.vision.imageanalysis import ImageAnalysisClient
    from azure.core.credentials import AzureKeyCredential

    client = ImageAnalysisClient(
        endpoint=AZURE_VISION_ENDPOINT,
        credential=AzureKeyCredential(AZURE_VISION_KEY),
    )
    with open(file_path, "rb") as f:
        result = client.analyze(image_data=f.read(), visual_features=["Adult"])
    # map result.adult.is_adult_content / is_gory_content / is_racy_content
    # to a decision dict with the same shape as analyze_image() above.
    """
    raise NotImplementedError(
        "Azure Vision integration not configured. Using analyze_image() instead."
    )
