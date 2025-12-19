from PIL import Image
import io

def _estimate_dpi(page) -> int:
    """Estimate DPI from page images"""
    try:
        images = page.get_images()
        if not images:
            return None
        
        # Get first image
        xref = images[0][0]
        base_image = page.parent.extract_image(xref)
        
        img = Image.open(io.BytesIO(base_image["image"]))
        
        # Estimate DPI
        page_width = page.rect.width / 72  # Convert points to inches
        img_dpi = int(img.width / page_width)
        
        return img_dpi
    except:
        return None