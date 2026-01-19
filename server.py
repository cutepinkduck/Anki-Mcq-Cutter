import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import uuid
import asyncio
import httpx
import logging
import json
import re
import base64
import os
import io
import shutil
import fitz  # PyMuPDF
from PIL import Image

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AnkiTurboServer")

# 임시 파일 저장소
TEMP_DIR = "./temp_pdfs"
os.makedirs(TEMP_DIR, exist_ok=True)

# --- FastAPI 앱 초기화 (이 부분이 먼저 실행되어야 함) ---
app = FastAPI(title="Anki Turbo PRO Server (High Quality)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"❌ 데이터 검증 에러 (422): {exc.errors()}")
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

# --- 상태 관리 ---
PDF_JOBS: Dict[str, Dict[str, Any]] = {}
BATCH_JOBS: Dict[str, Dict[str, Any]] = {}

# --- 모델 ---
class BatchItem(BaseModel):
    custom_id: str
    prompt: str
    image_base64: str

class BatchRequest(BaseModel):
    api_key: str
    model: str
    items: List[BatchItem]
    temperature: float = 0.0

class SingleRequest(BaseModel):
    api_key: str
    model: str
    prompt: str
    images: List[str]
    provider: str
    base_url: Optional[str] = None
    temperature: float = 0.0

class CropItem(BaseModel):
    id: str
    bbox: List[float]

class CropRequest(BaseModel):
    job_id: str
    page_num: int
    items: List[CropItem]
    dpi: int = 144

# [신규] 수정 모드용 고화질 페이지 요청
class PageImageRequest(BaseModel):
    job_id: str
    page_num: int
    dpi: int = 200

# --- 헬퍼 함수 ---
def clean_base64(b64: str) -> str:
    if "," in b64: return b64.split(",")[1]
    return b64

def extract_json(text_content: str):
    try:
        text_content = re.sub(r'^```json\s*', '', text_content, flags=re.MULTILINE)
        text_content = re.sub(r'^```\s*', '', text_content, flags=re.MULTILINE)
        text_content = text_content.strip()
        start = text_content.find('{')
        end = text_content.rfind('}') + 1
        if start != -1 and end != 0:
            return json.loads(text_content[start:end])
        return json.loads(text_content)
    except Exception as e:
        logger.error(f"JSON Parse Error: {text_content[:100]}...")
        return {"error": "JSON Parsing Failed", "raw": text_content}

# [수정됨] Job 복구 시도 헬퍼 함수
def ensure_job_exists(job_id: str):
    # 이미 메모리에 있으면 패스
    if job_id in PDF_JOBS:
        return True
    
    # 메모리에 없으면 디스크 확인
    file_path = os.path.join(TEMP_DIR, f"{job_id}.pdf")
    if os.path.exists(file_path):
        try:
            # 파일이 있으면 메모리에 정보 복구
            logger.info(f"🔄 Job ID {job_id} 복구 중 (디스크에서 로드)...")
            doc = fitz.open(file_path)
            PDF_JOBS[job_id] = {
                "status": "done",
                "filename": "restored_session.pdf",
                "file_path": file_path,
                "pages": [], # 페이지 썸네일은 필요할 때 다시 생성되거나 비워둠
                "total_pages": len(doc)
            }
            doc.close()
            return True
        except Exception as e:
            logger.error(f"Job 복구 실패: {e}")
            return False
    return False

def process_pdf_task(job_id: str, file_path: str, filename: str, dpi: int = 72):
    try:
        doc = fitz.open(file_path)
        total_pages = len(doc)
        logger.info(f"📂 PDF 시작: {filename} (총 {total_pages}쪽, DPI={dpi})")
        PDF_JOBS[job_id]["total_pages"] = total_pages
        for i in range(total_pages):
            page = doc.load_page(i)
            # 썸네일 생성 (사용자 설정 DPI 적용)
            pix = page.get_pixmap(dpi=dpi)
            img_bytes = pix.tobytes("jpg", jpg_quality=80)
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            page_data = {
                "id": f"p_{job_id}_{i+1}",
                "pageNum": i + 1,
                "thumb": f"data:image/jpeg;base64,{img_b64}",
                "fileName": filename,
                "is_server_processed": True
            }
            if job_id in PDF_JOBS: PDF_JOBS[job_id]["pages"].append(page_data)
        doc.close()
        if job_id in PDF_JOBS:
            PDF_JOBS[job_id]["status"] = "done"
            logger.info(f"✅ PDF 완료: {filename}")
    except Exception as e:
        logger.error(f"❌ PDF 실패: {e}")
        if job_id in PDF_JOBS:
            PDF_JOBS[job_id]["status"] = "failed"
            PDF_JOBS[job_id]["error"] = str(e)

async def call_gemini(client, api_key, model, prompt, images, base_url=None, temperature=0.0):
    if not base_url or "generativelanguage.googleapis.com" in base_url:
        base_url = "https://generativelanguage.googleapis.com/v1beta/models/"
    if not base_url.endswith("/"): base_url += "/"
    url = f"{base_url}{model}:generateContent?key={api_key}"
    parts = [{"text": prompt}]
    for img in images: parts.append({"inlineData": {"mimeType": "image/jpeg", "data": clean_base64(img)}})
    payload = {
        "contents": [{"role": "user", "parts": parts}], 
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": temperature
        }
    }
    resp = await client.post(url, json=payload, timeout=120.0)
    resp.raise_for_status()
    return resp.json()['candidates'][0]['content']['parts'][0]['text']

async def call_openai(client, api_key, model, prompt, images, base_url=None, temperature=0.0):
    url = base_url if base_url else "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    if "openrouter" in url:
        headers["HTTP-Referer"] = "http://localhost:8000"
        headers["X-Title"] = "Anki Turbo"
    content = [{"type": "text", "text": prompt + "\nJSON Output Only."}]
    for img in images: content.append({"type": "image_url", "image_url": {"url": img}})
    payload = {
        "model": model, 
        "messages": [{"role": "user", "content": content}], 
        "response_format": {"type": "json_object"},
        "temperature": temperature
    }
    resp = await client.post(url, headers=headers, json=payload, timeout=120.0)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']

async def call_anthropic(client, api_key, model, prompt, images, base_url=None, temperature=0.0):
    url = "https://api.anthropic.com/v1/messages"
    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    content = []
    for img in images: content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": clean_base64(img)}})
    content.append({"type": "text", "text": prompt + "\nOutput strictly standard JSON."})
    payload = {
        "model": model, 
        "max_tokens": 4096, 
        "messages": [{"role": "user", "content": content}],
        "temperature": temperature
    }
    resp = await client.post(url, headers=headers, json=payload, timeout=120.0)
    resp.raise_for_status()
    return resp.json()['content'][0]['text']

# --- API ---
@app.get("/")
async def health_check(): return {"status": "running", "msg": "Anki Turbo PRO Server (High Quality)"}

@app.post("/upload_pdf")
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...), dpi: int = 72):
    job_id = str(uuid.uuid4())
    file_path = os.path.join(TEMP_DIR, f"{job_id}.pdf")
    with open(file_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
    PDF_JOBS[job_id] = {"status": "processing", "filename": file.filename, "file_path": file_path, "pages": [], "total_pages": 0}
    background_tasks.add_task(process_pdf_task, job_id, file_path, file.filename, dpi)
    return {"job_id": job_id, "status": "started"}

@app.get("/check_pdf_job/{job_id}")
async def check_pdf_job(job_id: str, last_index: int = 0):
    if job_id not in PDF_JOBS: raise HTTPException(status_code=404, detail="Job not found")
    job = PDF_JOBS[job_id]
    return {"status": job["status"], "total_pages": job.get("total_pages", 0), "processed_count": len(job["pages"]), "new_pages": job["pages"][last_index:], "next_index": len(job["pages"])}

@app.post("/process_single")
async def process_single(req: SingleRequest):
    async with httpx.AsyncClient() as client:
        try:
            raw = ""
            if req.provider == 'gemini': raw = await call_gemini(client, req.api_key, req.model, req.prompt, req.images, req.base_url, req.temperature)
            elif 'openai' in req.provider: raw = await call_openai(client, req.api_key, req.model, req.prompt, req.images, req.base_url, req.temperature)
            elif req.provider == 'anthropic': raw = await call_anthropic(client, req.api_key, req.model, req.prompt, req.images, req.base_url, req.temperature)
            return extract_json(raw)
        except Exception as e:
            logger.error(f"AI Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# [수정됨] 배치 크롭 함수 (복구 로직 적용)
@app.post("/crop_batch_items")
async def crop_batch_items(req: CropRequest):
    # 1. Job ID 검사 및 복구 시도
    if not ensure_job_exists(req.job_id):
        raise HTTPException(status_code=404, detail="Job ID not found (Please Re-upload PDF)")

    file_path = PDF_JOBS[req.job_id].get("file_path")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF File missing on server")

    try:
        doc = fitz.open(file_path)
        if req.page_num < 1 or req.page_num > len(doc):
            doc.close()
            raise HTTPException(status_code=400, detail="Page number out of range")
            
        page = doc.load_page(req.page_num - 1)
        scale = req.dpi / 72
        mat = fitz.Matrix(scale, scale)
        page_rect = page.rect
        width, height = page_rect.width, page_rect.height
        
        results = []
        for item in req.items:
            # 좌표 유효성 검사
            if not item.bbox or len(item.bbox) != 4:
                results.append({"id": item.id, "img": None})
                continue
            
            y1, x1, y2, x2 = item.bbox
            rx1 = (x1 / 1000) * width
            ry1 = (y1 / 1000) * height
            rx2 = (x2 / 1000) * width
            ry2 = (y2 / 1000) * height

            if rx2 <= rx1 or ry2 <= ry1:
                results.append({"id": item.id, "img": None})
                continue
            
            try:
                clip = fitz.Rect(rx1, ry1, rx2, ry2)
                pix = page.get_pixmap(matrix=mat, clip=clip)
                img_data = pix.tobytes("png")
                
                # WebP 변환
                pil_img = Image.open(io.BytesIO(img_data))
                with io.BytesIO() as output:
                    pil_img.save(output, format="WEBP", lossless=True, quality=100)
                    b64 = base64.b64encode(output.getvalue()).decode("utf-8")
                
                results.append({"id": item.id, "img": f"data:image/webp;base64,{b64}"})
            except Exception as e:
                logger.error(f"Crop Item Error: {e}")
                results.append({"id": item.id, "img": None})
        
        doc.close()
        return {"results": results}
    except Exception as e:
        logger.error(f"Server Crop Critical Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# [수정됨] 단일 페이지 이미지 요청 (수정 모드용 - 복구 로직 적용)
@app.post("/get_page_image")
async def get_page_image(req: PageImageRequest):
    if not ensure_job_exists(req.job_id):
        raise HTTPException(status_code=404, detail="Job missing")
        
    file_path = PDF_JOBS[req.job_id].get("file_path")
    try:
        doc = fitz.open(file_path)
        page = doc.load_page(req.page_num - 1)
        # 편집용이므로 너무 크지 않게 DPI 조절 (기본 200)
        scale = req.dpi / 72
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
        img_data = pix.tobytes("jpg", jpg_quality=95) # 편집 배경은 JPG 95%면 충분
        b64 = base64.b64encode(img_data).decode("utf-8")
        doc.close()
        return {"img": f"data:image/jpeg;base64,{b64}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submit_batch")
async def submit_batch(request: BatchRequest, background_tasks: BackgroundTasks):
    batch_id = str(uuid.uuid4())
    BATCH_JOBS[batch_id] = {"state": "PROCESSING", "results": [], "total": len(request.items)}
    async def process_job():
        sem = asyncio.Semaphore(5)
        async with httpx.AsyncClient() as client:
            async def worker(item):
                async with sem:
                    try:
                        res = await call_gemini(client, request.api_key, request.model, item.prompt, [item.image_base64], temperature=request.temperature)
                        return {"custom_id": item.custom_id, "response": {"body": {"candidates": [{"content": {"parts": [{"text": res}]}}]}}} 
                    except Exception as e:
                        return {"custom_id": item.custom_id, "error": str(e)}
            tasks = [worker(item) for item in request.items]
            results = await asyncio.gather(*tasks)
            BATCH_JOBS[batch_id]["results"] = results
            BATCH_JOBS[batch_id]["state"] = "COMPLETED"
    background_tasks.add_task(process_job)
    return {"batch_id": batch_id}

@app.get("/check_batch/{batch_id}")
async def check_batch(batch_id: str):
    if batch_id not in BATCH_JOBS: raise HTTPException(status_code=404)
    return BATCH_JOBS[batch_id]

@app.delete("/clear_temp_pdfs")
async def clear_temp_pdfs():
    """임시 PDF 파일들을 모두 삭제"""
    try:
        deleted_count = 0
        if os.path.exists(TEMP_DIR):
            for filename in os.listdir(TEMP_DIR):
                file_path = os.path.join(TEMP_DIR, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    deleted_count += 1
        # 메모리 상태도 정리
        PDF_JOBS.clear()
        logger.info(f"🗑️ 임시 파일 {deleted_count}개 삭제 완료")
        return {"success": True, "deleted_count": deleted_count}
    except Exception as e:
        logger.error(f"❌ 임시 파일 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/temp_pdf_count")
async def get_temp_pdf_count():
    """현재 저장된 임시 PDF 파일 개수 반환"""
    try:
        count = 0
        if os.path.exists(TEMP_DIR):
            count = len([f for f in os.listdir(TEMP_DIR) if os.path.isfile(os.path.join(TEMP_DIR, f))])
        return {"count": count}
    except Exception as e:
        return {"count": 0, "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)