import io
import numpy as np
from PIL import Image

def norm01(a: np.ndarray) -> np.ndarray:
    mn = float(np.nanmin(a))
    mx = float(np.nanmax(a))
    if mx - mn < 1e-9:
        return np.zeros_like(a, dtype=np.float32)
    return ((a - mn) / (mx - mn)).astype(np.float32)

def arr_to_png_gray(arr: np.ndarray, out_size=(512,512)) -> bytes:
    a = np.clip(norm01(arr), 0, 1)
    img = Image.fromarray((a*255.0).astype(np.uint8), mode="L")
    if out_size:
        img = img.resize(out_size, resample=Image.BILINEAR)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
