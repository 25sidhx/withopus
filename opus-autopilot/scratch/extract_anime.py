import os

source_path = r"C:\Users\Siddhant rahate\.gemini\antigravity\brain\24adfff4-4b31-47db-8852-7c179f1fab67\.system_generated\steps\271\content.md"
dest_dir = r"c:\Users\Siddhant rahate\Downloads\opus-site\js"
dest_path = os.path.join(dest_dir, "anime.min.js")

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

with open(source_path, "r", encoding="utf-8") as f:
    content = f.read()

# The content has a header followed by --- and then the JS file
parts = content.split("---", 1)
if len(parts) > 1:
    js_code = parts[1].strip()
else:
    js_code = content

with open(dest_path, "w", encoding="utf-8") as f:
    f.write(js_code)

print(f"Extracted and saved AnimeJS to {dest_path}")
