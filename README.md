# Matt - PDF to Text Transformer Bot

A lightweight production Telegram Bot written in Python using native async loops for reliable PDF conversion architectures.

## Local Installation Setup
1. Mount system dependencies (e.g., `sudo apt install tesseract-ocr`)
2. Run `pip install -r requirements.txt`
3. Export environment configuration token: `export BOT_TOKEN="your_token_here"`
4. Start via command entry: `python bot.py`

## Render.com Native Deployment Pipeline Steps

Because this service depends on binary packages outside the Python runtime environment (`tesseract-ocr`), you must configure Render to inject the binaries using an environment Native Docker construct, or more simply, a custom Shell Build script.

### Option 1: Native Ubuntu Binary Auto-Pull (Recommended)
1. In the Render Dashboard, click **New +** and select **Background Worker**.
2. Link your GitHub project repository.
3. Set **Runtime** to `Python`.
4. Set your **Start Command** box to exactly: `python bot.py`

### Option 2: Inject Native Binary Paths
Go directly to your Background Worker service tab ➔ **Environment** and create the following key-value bindings:

| Environment Key | Value / Token Path Reference |
| :--- | :--- |
| `BOT_TOKEN` | *[Your Private Telegram Token String from @BotFather]* |
