import json
import os

DEFAULT_CONFIG = {
    "lingua": {

        "use_preloaded_language_models": True,
        "use_low_accuracy_mode": False
    },
    "translator": {
        "model_id": "facebook/nllb-200-distilled-600M",
        "cpu_only": False
    },
    "server": {
        "host": "0.0.0.0",
        "port": 5000,
        "use_ssl": False,
        "workers": 1
    }
}

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Config file not found. Creating default {CONFIG_FILE}...")
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            return DEFAULT_CONFIG
        except Exception as e:
            print(f"Error creating config file: {e}")
            return DEFAULT_CONFIG
            
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Basic validation or merge with default could go here
            return config
    except Exception as e:
        print(f"Error reading config file: {e}")
        return DEFAULT_CONFIG
