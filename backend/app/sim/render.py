import io
import numpy as np
from PIL import Image

def render_raster_png(arr: np.ndarray) -> bytes:
    arr = np.clip(arr, 0.0, 1.0)
    # grayscale 0..255
    im = Image.fromarray((arr*255).astype("uint8"), mode="L")
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
