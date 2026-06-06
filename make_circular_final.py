from PIL import Image, ImageOps, ImageDraw

def make_circular_padded(img_path, output_path, size=800, border_width=15, border_color=(0, 0, 0)):
    # Open the image
    img = Image.open(img_path).convert("RGBA")
    
    # Calculate padding to make it square without cropping
    width, height = img.size
    max_dim = max(width, height)
    
    # Create a new square transparent image
    square_img = Image.new("RGBA", (max_dim, max_dim), (255, 255, 255, 0))
    
    # Paste original image in the center
    upper = (max_dim - height) // 2
    left = (max_dim - width) // 2
    square_img.paste(img, (left, upper))
    
    # Resize to target size (800x800)
    square_img = square_img.resize((size, size), Image.Resampling.LANCZOS)
    
    # Create circular mask
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    
    # Apply mask
    output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    output.paste(square_img, (0, 0), mask=mask)
    
    # Add border
    if border_width > 0:
        draw_border = ImageDraw.Draw(output)
        for i in range(border_width):
            draw_border.ellipse((i, i, size - i, size - i), outline=border_color)

    output.save(output_path)
    print(f"Padded circular logo saved to {output_path}")

if __name__ == "__main__":
    make_circular_padded("logo.jpg", "logo_circular_final.png", size=600, border_width=15)
