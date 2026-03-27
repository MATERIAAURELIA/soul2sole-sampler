#!/usr/bin/env python3
"""Upload James's sampler tracks to Wix Media Manager."""
import json, urllib.request, os, time

WIX_KEY = "IST.eyJraWQiOiJQb3pIX2FDMiIsImFsZyI6IlJTMjU2In0.eyJkYXRhIjoie1wiaWRcIjpcImI0ODBhNTBmLWEwYmQtNGRhMy04YmNiLTNmMzQ5NDM1NmIxM1wiLFwiaWRlbnRpdHlcIjp7XCJ0eXBlXCI6XCJhcHBsaWNhdGlvblwiLFwiaWRcIjpcImM3MDQ0Y2Y5LThjZmYtNGZiNy04NWZlLWE1MGI3NWUwYTBhNVwifSxcInRlbmFudFwiOntcInR5cGVcIjpcImFjY291bnRcIixcImlkXCI6XCJlY2I2OTdlZC0yY2EyLTRjYWQtYWQzYy02MGYwN2YwNzhhYjhcIn19IiwiaWF0IjoxNzc0NTU4MzMwfQ.ejAu0DWuLA6KlWVWFpXMk_Y-zEIyGXZHd4ptaujGz9uiMk6X1gMv4p1SfQjAnDvf6SryAzKoyKN5B261fDCIs8JGjqW-bVpLE8_z5s1i5IPYGD4lAybUBVNNq2rMgLvq92fOMF9cSYdtCQ19v5byBYOR_UytWqhwFN6LAU90pgVSvLNFia8Jc5DeuXldC42yyjAAK-6oO2ksdtSsCFcsabbvYl9FqnyBfv6orAtnKCEXe_Jf0XrbbCUD07cNWCBF9j3449TU-23tZibt_K9mLUK7VriFg35MT54mr93zpx8mbsgAGzk7xjs0qD9HW18puT0UhpgO0zFtge-n9jicRA"
SITE_ID = "f0f604ad-2eb7-4e1f-8095-33b7acc4b9d8"

BASE_DIR = os.path.expanduser("~/Dropbox/MUSIC LIBRARY/Miracle Tones/Miracle Tones Massage & Reiki")

# James sampler tracks - display name → actual filename
TRACKS = {
    "Mother Nurture": "E  - Mother Nurture  432.mp3",
    "Blossoms": "27 - Blossoms - Ambient Piano Series.mp3",
    "The Return Home": "E  -The Return Home.mp3",
    "Patience": "D - Patience  01 - Ambient Bliss Series 432.mp3",
    "Self Mastery": "12 Effortless Self Mastery   528hz.mp3",
    "My Rest is Always Healing": "10 My Rest is Always Healing  528hz.mp3",
    "Radical Acceptance": "17  Radical Acceptance.mp3",
    "Awakening the Higher Self": "15 Awakening the Higher Self.mp3",
    "Rise": "28 - Rise  - Ambient Piano Series 432hz .mp3",
    "You Are Welcome Here": "01 You are Welcome Here 528hz.mp3",
    "Spirit": "E  -Spirit.mp3",
    "Innocence": "26 - Innocence - Ambient Piano Series.mp3",
    "Sweetness": "25 - Sweetness - Ambient Piano Series.mp3",
    "Terra Nova": "E  -Terra Nova.mp3",
    "Angelic": "E  -Angelic.mp3",
    "Awakening the Dreamer": "13 Awakening the Dreamer.mp3",
}

def get_upload_url(display_name):
    safe_name = display_name.replace(" ", "-").lower() + ".mp3"
    payload = json.dumps({
        "mimeType": "audio/mpeg",
        "fileName": f"james-sampler-{safe_name}"
    }).encode()
    req = urllib.request.Request(
        "https://www.wixapis.com/site-media/v1/files/generate-upload-url",
        data=payload,
        headers={
            "Authorization": WIX_KEY,
            "wix-site-id": SITE_ID,
            "Content-Type": "application/json"
        }
    )
    resp = urllib.request.urlopen(req, timeout=30)
    return json.loads(resp.read())["uploadUrl"]

def upload_file(upload_url, file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    req = urllib.request.Request(upload_url, data=data, method="PUT",
                                 headers={"Content-Type": "audio/mpeg"})
    resp = urllib.request.urlopen(req, timeout=120)
    return json.loads(resp.read())

results = {}
for display_name, filename in TRACKS.items():
    file_path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(file_path):
        print(f"❌ MISSING: {display_name} → {filename}")
        continue
    size = os.path.getsize(file_path)
    if size < 1000:
        print(f"⚠️  CLOUD-ONLY (0 bytes): {display_name}")
        continue
    
    print(f"⬆️  Uploading: {display_name} ({size/1024/1024:.1f} MB)...", end=" ", flush=True)
    try:
        url = get_upload_url(display_name)
        result = upload_file(url, file_path)
        wix_url = result.get("file", {}).get("url", "???")
        results[display_name] = wix_url
        print(f"✅ {wix_url}")
        time.sleep(1)  # rate limit courtesy
    except Exception as e:
        print(f"❌ Error: {e}")
        results[display_name] = None

# Save results
output_path = os.path.join(os.path.dirname(__file__), "wix-urls.json")
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\n📁 URLs saved to {output_path}")
print(f"✅ {sum(1 for v in results.values() if v)} / {len(TRACKS)} uploaded")
