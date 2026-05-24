"""Test: Post a single image to Instagram via instagrapi."""

from instagrapi import Client
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import time

USERNAME = "with_opus"
PASSWORD = "OPUS@2526"
TEST_DIR = Path(__file__).parent / "test_post"
TEST_DIR.mkdir(exist_ok=True)

def create_test_image():
    """Create a simple branded test image."""
    img = Image.new("RGB", (1080, 1080), color=(15, 15, 15))
    draw = ImageDraw.Draw(img)

    # Draw centered text
    try:
        font_large = ImageFont.truetype("arial.ttf", 72)
        font_small = ImageFont.truetype("arial.ttf", 36)
    except OSError:
        font_large = ImageFont.load_default()
        font_small = font_large

    # Title
    title = "OPUS"
    bbox = draw.textbbox((0, 0), title, font=font_large)
    tw = bbox[2] - bbox[0]
    draw.text(((1080 - tw) // 2, 400), title, fill=(255, 180, 60), font=font_large)

    # Subtitle
    sub = "Autopilot Test Post"
    bbox2 = draw.textbbox((0, 0), sub, font=font_small)
    sw = bbox2[2] - bbox2[0]
    draw.text(((1080 - sw) // 2, 500), sub, fill=(180, 180, 180), font=font_small)

    # Accent line
    draw.rectangle([440, 480, 640, 484], fill=(255, 180, 60))

    path = TEST_DIR / "test_post.jpg"
    img.save(path, "JPEG", quality=95)
    print(f"[OK] Test image created: {path}")
    return path


def main():
    # Create test image
    img_path = create_test_image()

    # Login
    cl = Client()
    cl.delay_range = [2, 5]

    print("[*] Logging in...")
    cl.login(USERNAME, PASSWORD)
    print("[OK] Logged in as with_opus")

    # Post single photo
    caption = (
        "Testing the Opus Autopilot system.\n\n"
        "This post was created automatically.\n\n"
        "#opus #automation #test"
    )

    print("[*] Uploading photo...")
    try:
        media = cl.photo_upload(
            path=str(img_path),
            caption=caption,
        )
        print(f"[SUCCESS] Posted! Media ID: {media.pk}")
        print(f"[SUCCESS] URL: https://www.instagram.com/p/{media.code}/")
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
