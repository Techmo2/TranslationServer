# GmTranslateServer

A translation API server compatible with [LibreTranslate](https://libretranslate.com/), powered by `facebook/nllb-200-distilled-600M` and `lingua-language-detector`.

## Features
- **/detect**: Detect language of input text (supporting ISO 639-1 and 639-3).
- **/translate**: Translate text between languages.
- Asynchronous request processing with background workers.

## Setup

### Prerequisites
- Python 3.9+ (Python 3.12 recommended)
- CUDA-capable GPU recommended for performance (Torch will use CPU otherwise).

### 1. Create a Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

```bash
# Create venv
python -m venv .venv

# Activate venv (Linux/MacOS)
source .venv/bin/activate

# Activate venv (Windows)
.venv\Scripts\activate
```

### 2. Install Dependencies

Install the required packages using `pip`.

```bash
pip install -r requirements.txt
```

**Note**: If you want to use GPU acceleration, ensure you have the correct version of PyTorch installed for your CUDA version. The `requirements.txt` contains a standard `torch` version which might default to CPU-only on some systems or CUDA 12.1 on others. Refere to [pytorch.org](https://pytorch.org/) for specific installation commands.

### 3. Run the Server

Start the FastAPI server using `uvicorn`.

```bash
# Run server (defaults to port 5000)
python main.py
```

Or run uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

## API Usage

### Detect Language

```bash
curl -X POST -F "q=Hello World" http://localhost:5000/detect
```

Response:
```json
[
  {
    "confidence": 100.0,
    "language": "en"
  }
]
```

### Translate

```bash
curl -X POST \
  -F "q=Hello World" \
  -F "source=auto" \
  -F "target=fr" \
  http://localhost:5000/translate
```

Response:
```json
{
  "translatedText": "Bonjour le monde"
}
```
