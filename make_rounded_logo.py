from PIL import Image, ImageOps, ImageDraw

def make_rounded(img_path, output_path, radius=80, border_width=10, border_color=(0, 0, 0)):
    # Open the image
    img = Image.open(img_path).convert("RGBA")
    
    # Original aspect ratio preservation or slight padding
    width, height = img.size
    # Instead of square cropping, let's keep it rectangular but add padding if needed
    # or just use the original size and apply rounded corners.
    
    # Let's resize to a manageable size while keeping aspect ratio
    max_size = 800
    if width > height:
        new_width = max_size
        new_height = int(height * (max_size / width))
    else:
        new_height = max_size
        new_width = int(width * (max_size / height))
    
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Create mask for rounded rectangle
    mask = Image.new('L', (new_width, new_height), 0)
    draw = ImageDraw.Draw(mask)
    # Draw rounded rectangle mask
    draw.rounded_rectangle((0, 0, new_width, new_height), radius=radius, fill=255)
    
    # Apply mask
    output = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))
    output.paste(img, (0, 0), mask=mask)
    
    # Add border
    if border_width > 0:
        draw_border = ImageDraw.Draw(output)
        # Draw rounded rectangle border
        for i in range(border_width):
            draw_border.rounded_rectangle(
                (i, i, new_width - i, new_height - i), 
                radius=radius, 
                outline=border_color
            )

    output.save(output_path)
    print(f"Rounded logo saved to {output_path}")

if __name__ == "__main__":
    # Setting radius to 500 for maximum roundness
    make_rounded("logo.jpg", "logo_rounded.png", radius=500, border_width=12)
