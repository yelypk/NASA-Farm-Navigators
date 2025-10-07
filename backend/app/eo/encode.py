import io
import numpy as np
from PIL import Image

def to_grayscale_png(arr: np.ndarray, vmin: float, vmax: float) -> bytes:
    """Scale arr -> uint8 0..255 and encode PNG (L-mode)."""
    a = np.clip((arr - vmin) / (vmax - vmin + 1e-9), 0, 1)
    u8 = (a * 255.0 + 0.5).astype(np.uint8)
    im = Image.fromarray(u8, mode="L")
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
