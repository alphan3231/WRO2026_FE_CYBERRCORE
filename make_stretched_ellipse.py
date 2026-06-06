from PIL import Image, ImageOps, ImageDraw

def make_stretched_ellipse(img_path, output_path, border_width=15, border_color=(0, 0, 0)):
    # Open the image
    img = Image.open(img_path).convert("RGBA")
    
    # Use the original dimensions
    width, height = img.size
    
    # Create elliptical mask based on full dimensions
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, width, height), fill=255)
    
    # Apply mask
    output = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    output.paste(img, (0, 0), mask=mask)
    
    # Add border
    if border_width > 0:
        draw_border = ImageDraw.Draw(output)
        for i in range(border_width):
            # Slightly inset the border to avoid clipping
            draw_border.ellipse((i, i, width - i, height - i), outline=border_color)

    output.save(output_path)
    print(f"Stretched elliptical logo saved to {output_path} (Size: {width}x{height})")

if __name__ == "__main__":
    make_stretched_ellipse("logo.jpg", "logo_circular_final.png", border_width=15)
