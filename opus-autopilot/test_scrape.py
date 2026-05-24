"""Test script for scraped content generation."""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from text_generator import generate_from_scraped
from scraper import scrape_source_accounts

posts = scrape_source_accounts()
if posts:
    print(f"Found {len(posts)} posts")
    post = posts[0]
    source = post["source"]
    caption = post["caption"]
    print(f"Source: @{source}")
    print(f"Caption preview: {caption[:100].encode('utf-8', errors='replace').decode('utf-8')}...")
    
    data = generate_from_scraped(caption, source, 6)
    if data:
        print(f"\nGenerated: {data['title']}")
        print(f"Slides: {len(data['slides'])}")
        for slide in data["slides"][:2]:
            text = slide["text"]
            visual = slide["visual_direction"]
            num = slide["slide_number"]
            print(f"\nSlide {num}: {text[:80]}...")
            print(f"Visual: {visual}")
    else:
        print("Failed to generate from scraped content")
else:
    print("No posts found")
