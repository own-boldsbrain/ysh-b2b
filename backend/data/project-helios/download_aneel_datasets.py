import requests
import json
import os
from urllib.parse import urlparse

# Load slugs from aneel_slugs.txt
with open("aneel_slugs.txt", "r") as f:
    slugs = [line.strip() for line in f if line.strip()]

# Create directory for downloads
os.makedirs("aneel_datasets", exist_ok=True)

for slug in slugs:
    print(f"Processing dataset: {slug}")
    api_url = f"https://dadosabertos.aneel.gov.br/api/3/action/package_show?id={slug}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            resources = data["result"].get("resources", [])
            for res in resources:
                if res.get("format", "").upper() == "CSV":
                    download_url = res.get("url")
                    if download_url:
                        # Extract filename from URL
                        parsed = urlparse(download_url)
                        filename = os.path.basename(parsed.path)
                        if not filename:
                            filename = f"{slug}_{res.get('id', 'unknown')}.csv"
                        filepath = os.path.join("aneel_datasets", filename)
                        print(f"Downloading {filename} from {download_url}")
                        try:
                            csv_response = requests.get(download_url)
                            csv_response.raise_for_status()
                            with open(filepath, "wb") as f:
                                f.write(csv_response.content)
                            print(f"Downloaded {filename}")
                        except Exception as e:
                            print(f"Failed to download {filename}: {e}")
        else:
            print(f"API call failed for {slug}: {data.get('error')}")
    except Exception as e:
        print(f"Error processing {slug}: {e}")

print("Download process completed.")
