# DefendRebuttalGenerator


## 🔗 Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/jyotsanakhatri24/DefendRebuttalGenerator.git
    cd DefendRebuttalGenerator
    ```

2.  **Activate virtual environment:**
    ```bash
    python -m venv myenv
    source myenv/bin/activate
    pip3 install -r reqs.txt
    ```
    

4.  **Set Environment Variables:**
    Setup your API keys:
    ```bash
    export MODEL_NAME="gemini-2.0-flash"
    export SEMANTIC_SCHOLAR_API_KEY="your_semantic_scholar_api_key" 
    export GEMINI_API_KEY="your_google_gemini_api_key" 
    ```

## 🖥️ Running the Application

Ensure your virtual environment is activated, then run:

```bash
python3 app.py
```

## 📋 Requirements

- Semantic Scholar API Key
- LLM API Key for any openai (gpt-4o-mini) or gemini (gemini-2.0-flash)
- ai2-scholarqa-lib: https://github.com/allenai/ai2-scholarqa-lib
```
