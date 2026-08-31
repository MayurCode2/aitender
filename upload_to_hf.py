import os
from huggingface_hub import HfApi, login

print("=== Uploading AI Tender Analyzer to Hugging Face Space ===")

# Check if token is provided or prompt
hf_token = os.environ.get("HF_TOKEN")
if hf_token:
    login(token=hf_token)
else:
    print("Please log in when prompted (or pass HF_TOKEN environment variable).")
    login()

api = HfApi()

repo_id = "mayur2251998/ai-tender"

print(f"Uploading files to Hugging Face Space: {repo_id}...")

api.upload_folder(
    folder_path=".",
    repo_id=repo_id,
    repo_type="space",
    ignore_patterns=[
        "venv/*",
        ".git/*",
        "__pycache__/*",
        "input/*",
        "output/*",
        "*.pdf",
        ".env"
    ]
)

print(f"\n🎉 Success! Your Space is live at: https://huggingface.co/spaces/{repo_id}")
