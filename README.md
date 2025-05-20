# AI Flaw Report Form

### Setup

```bash
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
```

### To set up HuggingFace:
```bash
export HF_TOKEN=your_huggingface_token
export HF_REPO_ID=coordinated-flaw-disclosures/ai-flaw-reports
```

You can get a token from [Hugging Face settings](https://huggingface.co/settings/tokens).

### Main Application

To run the main application:

```bash
streamlit run main.py
```

### Viewing Reports

Reports are stored in:

1. **Local Storage (fallback)**: 
   - JSON files in the `reports/` directory
   - Uploaded files in the `uploads/` directory

2. **HuggingFace**:
   - Dataset at [https://huggingface.co/datasets/coordinated-flaw-disclosures/ai-flaw-reports](https://huggingface.co/datasets/coordinated-flaw-disclosures/ai-flaw-reports)
   - Files at [https://huggingface.co/datasets/coordinated-flaw-disclosures/ai-flaw-reports/tree/main/uploads](https://huggingface.co/datasets/coordinated-flaw-disclosures/ai-flaw-reports/tree/main/uploads)