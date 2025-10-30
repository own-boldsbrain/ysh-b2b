import csv
import os
from urllib.parse import urlparse

# Directory containing the CSV files
data_dir = "haas/data"

# Output file for slugs
output_file = "aneel_slugs.txt"

slugs = set()


# Function to extract slug from href
def get_slug(href):
    path = urlparse(href).path
    return path.split("/")[-1]


# Read all CSV files
for filename in os.listdir(data_dir):
    if filename.endswith(".csv"):
        filepath = os.path.join(data_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                href = row.get("dataset-heading href")
                if href:
                    slug = get_slug(href)
                    # Check if CSV is available
                    if "CSV" in row.values():
                        slugs.add(slug)

# Write slugs to file
with open(output_file, "w", encoding="utf-8") as f:
    for slug in sorted(slugs):
        f.write(slug + "\n")

print(f"Extracted {len(slugs)} unique slugs with CSV downloads.")
