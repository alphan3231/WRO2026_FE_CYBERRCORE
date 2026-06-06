from PIL import Image, ImageOps, ImageDraw

def make_circle(img_path, output_path, border_width=10, border_color=(0, 0, 0)):
    # Open the image
    img = Image.open(img_path).convert("RGBA")
    
    # Square crop (center)
    width, height = img.size
    min_dim = min(width, height)
    left = (width - min_dim) / 2
    top = (height - min_dim) / 2
    right = (width + min_dim) / 2
    bottom = (height + min_dim) / 2
    img = img.crop((left, top, right, bottom))
    img = img.resize((500, 500), Image.LANCZOS)
    
    # Create circular mask
    size = (500, 500)
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    
    # Apply mask
    output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    
    # Add border
    if border_width > 0:
        draw_border = ImageDraw.Draw(output)
        # Draw ellipse for border (slightly inside to not get cut off)
        # Note: draw.ellipse doesn't have a width param in old PIL, so we use coordinate thickness
        for i in range(border_width):
            draw_border.ellipse((i, i, 500-i, 500-i), outline=border_color)

    output.save(output_path)
    print(f"Circular logo saved to {output_path}")

if __name__ == "__main__":
    make_circle("logo.jpg", "logo_circular.png", border_width=15)
