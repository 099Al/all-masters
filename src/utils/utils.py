import math
from io import BytesIO

from PIL import Image


import hashlib


def make_collage(images, cols=2, rows=3, cell_size=(400, 400), margin=12, bg_color=(255, 255, 255)):
    """Create a collage from up to rows*cols PIL images arranged in a grid, trimming empty space at the bottom."""
    if not images:
        raise ValueError("No images provided.")

    # Use at most rows*cols images
    images = images[: rows * cols]
    n = len(images)

    cell_w, cell_h = cell_size

    # How many rows are actually needed?
    rows_used = max(1, min(rows, math.ceil(n / cols)))

    # Canvas size with outer margins and gutters — only for used rows
    canvas_w = cols * cell_w + (cols + 1) * margin
    canvas_h = rows_used * cell_h + (rows_used + 1) * margin
    canvas = Image.new("RGB", (canvas_w, canvas_h), color=bg_color)

    # Paste each image
    for i, im in enumerate(images):
        im = im.convert("RGB")
        scale = min(cell_w / im.width, cell_h / im.height)
        new_size = (max(1, int(im.width * scale)), max(1, int(im.height * scale)))

        # Pillow ≥10
        resample = getattr(Image, "Resampling", Image).LANCZOS
        im_resized = im.resize(new_size, resample)

        r, c = divmod(i, cols)   # row, col within the used rows
        x0 = margin + c * (cell_w + margin) + (cell_w - new_size[0]) // 2
        y0 = margin + r * (cell_h + margin) + (cell_h - new_size[1]) // 2
        canvas.paste(im_resized, (x0, y0))

    # Output buffer
    out = BytesIO()
    canvas.save(out, format="JPEG")
    out.seek(0)
    return out



def digit_hash(text: str, *, salt: str = "") -> str:
    """
    Deterministic, digits-only hash in format XXXX_XXXX_XXXX_XXXX.
    - Uses SHA-256 over (salt + text).
    - Produces 16 decimal digits, zero-padded, grouped by 4.
    - Not reversible; collisions are possible (like any short hash).
    """
    h = hashlib.sha256((salt + text).encode("utf-8")).digest()
    n = int.from_bytes(h, "big")          # big integer from digest
    dec = str(n)                           # decimal string of the big int
    last16 = dec[-16:].rjust(16, "0")      # keep last 16 digits, pad if needed
    return "_".join(last16[i:i+4] for i in range(0, 16, 4))
