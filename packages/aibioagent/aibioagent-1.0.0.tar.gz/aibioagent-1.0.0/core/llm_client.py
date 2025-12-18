# core/llm_client.py
from langchain_openai import ChatOpenAI
from config.settings import OPENAI_API_KEY, LLM_MODEL, VISION_LLM_MODEL
from core.usage_tracker import get_tracker
import base64, io
import tifffile
from pathlib import Path
import numpy as np
from PIL import Image

def get_llm(temperature=0.2, track_usage=True):
    """
    Return a ready-to-use LLM client with optional usage tracking.
    
    Parameters
    ----------
    temperature : float
        Model temperature (0.0 to 1.0)
    track_usage : bool
        If True, tracks token usage and costs
    """
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model=LLM_MODEL,
        temperature=temperature
    )
    
    if track_usage:
        # Wrap invoke to track usage
        original_invoke = llm.invoke
        def tracked_invoke(*args, **kwargs):
            result = original_invoke(*args, **kwargs)
            # Extract token usage from response
            if hasattr(result, 'response_metadata'):
                usage = result.response_metadata.get('token_usage', {})
                if usage:
                    tracker = get_tracker()
                    tracker.track_llm_call(
                        model=LLM_MODEL,
                        input_tokens=usage.get('prompt_tokens', 0),
                        output_tokens=usage.get('completion_tokens', 0)
                    )
            return result
        llm.invoke = tracked_invoke
    
    return llm

def get_vision_llm(temperature=0.2, track_usage=True):
    """
    Return a vision-capable LLM client with optional usage tracking.
    
    Parameters
    ----------
    temperature : float
        Model temperature (0.0 to 1.0)
    track_usage : bool
        If True, tracks token usage and costs
    """
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model=VISION_LLM_MODEL,              # must be a vision-capable model
        temperature=temperature
    )
    
    # Add helper method for image encoding
    def invoke_with_image(prompt_text: str, image_path: str):
        """
        Call the vision model with both text and image input.
        """
        image_b64 = _encode_image(image_path)
        message = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                ],
            }
        ]
        result = llm.invoke(message)
        
        # Track usage for vision calls
        if track_usage and hasattr(result, 'response_metadata'):
            usage = result.response_metadata.get('token_usage', {})
            if usage:
                tracker = get_tracker()
                tracker.track_vision_call(
                    model=VISION_LLM_MODEL,
                    input_tokens=usage.get('prompt_tokens', 0),
                    output_tokens=usage.get('completion_tokens', 0)
                )
        
        return result
    
    return llm, invoke_with_image

def _encode_image(image_path: str) -> str:
    """
    Load any microscopy image (TIFF, PNG, JPG, etc.),
    convert to a representative RGB PNG,
    and return its base64-encoded string for OpenAI Vision models.
    """
    """Convert an image file to a base64 string for API upload."""
    image_path = Path(image_path)
    ext = image_path.suffix.lower()
    try:
        if ext in [".tif", ".tiff"]:
            img = _load_tiff_as_rgb(image_path)
        else:
            # handle standard formats like PNG, JPG, BMP
            pil_img = Image.open(image_path)
            img = np.array(pil_img)
        # Ensure we have RGB
        if img.ndim == 2:
            img = np.stack([img]*3, axis=-1)
        elif img.ndim > 3:
            img = img[..., :3]
        # Normalize to 0-255 uint8
        img = _normalize_to_uint8(img)
        pil_img = Image.fromarray(img)
        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG")
        img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return img_b64
    except Exception as e:
        raise RuntimeError(f"Failed to encode image {image_path}: {e}")
    
def _load_tiff_as_rgb(image_path: Path) -> np.ndarray:
    """Load TIFF file and generate representative RGB image."""
    img = tifffile.imread(str(image_path))

    # Handle multi-dimensional data
    if img.ndim == 2:
        return img
    elif img.ndim == 3:
        # Choose strategy based on shape meaning (Z, Y, X) or (Y, X, C)
        if img.shape[-1] <= 4:
            # (Y, X, C)
            return img
        else:
            # (Z, Y, X)
            mip = np.max(img, axis=0)
            return mip
    elif img.ndim == 4:
        # (Z, Y, X, C)
        mip = np.max(img, axis=0)
        return mip
    else:
        raise ValueError(f"Unsupported TIFF dimensions: {img.shape}")


def _normalize_to_uint8(img: np.ndarray) -> np.ndarray:
    """Scale any image array to uint8 [0,255]."""
    img = img.astype(np.float32)
    img -= img.min()
    if img.max() > 0:
        img /= img.max()
    return (img * 255).astype(np.uint8)

# Quick Test
def main():
    # llm = get_llm()
    # question = "who is julia roberts."
    # response = llm.invoke(question)
    # print("Question:", question)
    # print("Response:", response.content)

    print("\n👁️ Testing vision model...")
    vision_llm, call_with_image = get_vision_llm()
    text_prompt = "Describe what you see in this image."
    test_img = "test_images/hela-cells.jpg"
    try:
        vision_response = call_with_image(text_prompt, test_img)
        print("Vision response:", vision_response.content)
    except FileNotFoundError:
        print("⚠️ No test image found, skipping vision test.")

if __name__ == "__main__":
    main()

