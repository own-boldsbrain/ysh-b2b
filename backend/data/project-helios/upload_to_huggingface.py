from huggingface_hub import HfApi
import os

# Initialize the API
api = HfApi()

# Create the dataset repo
repo_id = "fernando-bold/aneel-datasets"
try:
    api.create_repo(repo_id, repo_type="dataset", private=False)
    print(f"Created dataset repo: {repo_id}")
except Exception as e:
    print(f"Repo might already exist: {e}")

# Upload the folder (using upload_large_folder for large datasets)
folder_path = "aneel_datasets"
if os.path.exists(folder_path):
    print(f"Starting upload of large folder from {folder_path} to {repo_id}...")
    print("This may take several minutes. Please wait...")

    try:
        # Use upload_large_folder for folders with many files
        api.upload_large_folder(
            folder_path=folder_path,
            repo_id=repo_id,
            repo_type="dataset",
            num_workers=4,  # Parallel uploads
            allow_patterns="*.csv",  # Only upload CSV files
        )
        print(f"✅ Successfully uploaded files from {folder_path} to {repo_id}")
    except Exception as e:
        print(f"❌ Error during upload: {e}")
        print("Attempting alternative upload method...")
        # Fallback to regular upload_folder
        try:
            api.upload_folder(
                folder_path=folder_path,
                repo_id=repo_id,
                repo_type="dataset",
                allow_patterns="*.csv",
            )
            print(f"✅ Successfully uploaded using fallback method")
        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")
else:
    print(f"❌ Folder {folder_path} does not exist")

print("\n" + "=" * 60)
print("Upload process completed.")
print(f"Dataset URL: https://huggingface.co/datasets/{repo_id}")
print("=" * 60)
