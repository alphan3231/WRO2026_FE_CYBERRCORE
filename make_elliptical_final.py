from PIL import Image, ImageOps, ImageDraw

def make_elliptical_padded(img_path, output_path, target_width=550, target_height=500, border_width=15, border_color=(0, 0, 0)):
    # Open the image
    img = Image.open(img_path).convert("RGBA")
    
    # Create a new transparent canvas of the target size
    canvas = Image.new("RGBA", (target_width, target_height), (255, 255, 255, 0))
    
    # Calculate resizing to fit within the canvas while maintaining aspect ratio
    img_w, img_h = img.size
    ratio = min(target_width / img_w, target_height / img_h)
    new_w = int(img_w * ratio)
    new_h = int(img_h * ratio)
    img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Paste resized image in the center of the canvas
    offset_x = (target_width - new_w) // 2
    offset_y = (target_height - new_h) // 2
    canvas.paste(img_resized, (offset_x, offset_y))
    
    # Create elliptical mask
    mask = Image.new('L', (target_width, target_height), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, target_width, target_height), fill=255)
    
    # Apply mask
    output = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
    output.paste(canvas, (0, 0), mask=mask)
    
    # Add elliptical border
    if border_width > 0:
        draw_border = ImageDraw.Draw(output)
        for i in range(border_width):
            draw_border.ellipse((i, i, target_width - i, target_height - i), outline=border_color)

    output.save(output_path)
    print(f"Elliptical logo saved to {output_path}")

if __name__ == "__main__":
    make_elliptical_padded("logo.jpg", "logo_circular_final.png", target_width=550, target_height=500, border_width=15)
