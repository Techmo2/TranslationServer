from fastapi import FastAPI, Form, HTTPException, BackgroundTasks, Body, Request, Depends
from pydantic import BaseModel
from typing import List, Optional, Union
import asyncio
from translator import Translator
import uvicorn
from contextlib import asynccontextmanager
from config_loader import load_config

# Global instances
translator_instance = None
translation_queue = None
CONFIG = load_config()

async def translation_worker():
    """Background worker to process translation requests."""
    global translator_instance
    print("Worker started")
    while True:
        future, text, source, target = await translation_queue.get()
        try:
            # Offload heavy model work to thread if necessary, but here we run directly 
            # (or use run_in_executor if blocking). 
            # The generate method is blocking on CPU/GPU.
            # Ideally we use a thread pool for the blocking call.
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, translator_instance.translate_text, text, source, target)
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)
        finally:
            translation_queue.task_done()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global translator_instance, translation_queue
    print("Loading model...")
    translator_instance = Translator(CONFIG)
    print("Model loaded.")
    
    translation_queue = asyncio.Queue()
    worker_task = asyncio.create_task(translation_worker())
    yield
    # Shutdown
    worker_task.cancel()

class DetectRequest(BaseModel):
    q: str

class TranslateRequest(BaseModel):
    q: str
    source: str
    target: str
    format: str = "text"

async def get_detect_params(request: Request):
    content_type = request.headers.get("Content-Type", "")
    if "application/json" in content_type:
        try:
            data = await request.json()
            return DetectRequest(**data)
        except Exception:
             raise HTTPException(status_code=400, detail="Invalid JSON")
    else:
         form = await request.form()

         q = form.get("q")
         if not q:
              # Return empty/partial model or raise? 
              # Better to return object and let endpoint validate
              return DetectRequest(q="") 
         return DetectRequest(q=q)

async def get_translate_params(request: Request):
    content_type = request.headers.get("Content-Type", "")
    if "application/json" in content_type:
         try:
            data = await request.json()
            return TranslateRequest(**data)
         except Exception:
             raise HTTPException(status_code=400, detail="Invalid JSON")
    else:
         form = await request.form()
         return TranslateRequest(
            q=form.get("q", ""),
            source=form.get("source", ""),
            target=form.get("target", ""),
            format=form.get("format", "text")
         )

app = FastAPI(lifespan=lifespan)

@app.post("/detect")
async def detect(params: DetectRequest = Depends(get_detect_params)):
    request_q = params.q
        
    if not request_q:
        raise HTTPException(status_code=422, detail="Missing parameter: q")
    if not translator_instance:
        raise HTTPException(status_code=503, detail="Server initializing")
    
    # Use LanguageManager from translator instance
    try:
        results = translator_instance.language_manager.detect_language(request_q)
        
        response = []
        for code, conf in results:
            response.append({
                "confidence": conf * 100, # Convert to percentage
                "language": code
            })
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate")
async def translate(params: TranslateRequest = Depends(get_translate_params)):
    req_q = params.q
    req_source = params.source
    req_target = params.target
    
    if not req_q or not req_source or not req_target:
        raise HTTPException(status_code=422, detail="Missing parameters: q, source, or target")

    if not translator_instance:
        raise HTTPException(status_code=503, detail="Server initializing")

    future = asyncio.get_running_loop().create_future()
    await translation_queue.put((future, req_q, req_source, req_target))
    
    try:
        translated_text = await future
        return {"translatedText": translated_text}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    host = CONFIG["server"]["host"]
    port = CONFIG["server"]["port"]

    uvicorn.run(app, host=host, port=port)
