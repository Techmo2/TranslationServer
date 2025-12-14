# TranslateServer

A simple translation server with an api similar to [LibreTranslate](https://libretranslate.com/).

## Setup

### Prerequisites
- Python 3.9+
- CUDA-capable GPU recommended for performance

### 1. Create a Virtual Environment

```bash
# Create venv
python -m venv .venv

# Activate venv (Linux/MacOS)
source .venv/bin/activate

# Activate venv (Windows)
.venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Server

```bash
# Run server (defaults to port 5000)
python main.py
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
        "confidence": 14.372545558597471,
        "language": "en"
    },
    {
        "confidence": 6.843209870000674,
        "language": "tl"
    },
    {
        "confidence": 6.677430046744076,
        "language": "cy"
    },
    {
        "confidence": 4.767848182534421,
        "language": "st"
    },
    ...
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
