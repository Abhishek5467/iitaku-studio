"""Self-hosted GPU/CPU processor. Start from repository root:
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000 --workers 1
Use one process: the executor and SQLite queue are intentionally single-worker."""
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import secrets
import shutil
import sqlite3
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image
from backend import processing

ROOT=Path(__file__).resolve().parents[1]
DATA=Path(os.getenv("DATA_DIR",str(ROOT/"backend/jobs")));DATA.mkdir(parents=True,exist_ok=True)
DB=DATA/"studio.sqlite3"
WEIGHTS=Path(os.getenv("ANIME_WEIGHTS",str(ROOT/"backend/weights/RealESRGAN_x4plus_anime_6B.pth")))
PRODUCTS=Path(os.getenv("PRODUCT_DIR",str(ROOT/"backend/private_products")))
PLANS={"sr_2k":{"kind":"sr","edge":2560,"price":0},"sr_4k":{"kind":"sr","edge":3840,"price":29},"sr_8k":{"kind":"sr","edge":7680,"price":99},
       "flow_free":{"kind":"flow","edge":1280,"factor":2,"seconds":5,"price":0},"flow_9":{"kind":"flow","edge":1920,"factor":2,"seconds":10,"price":9},"flow_29":{"kind":"flow","edge":1920,"factor":4,"seconds":20,"price":29},"flow_99":{"kind":"flow","edge":3840,"factor":4,"seconds":30,"price":99}}
PREMIUM={"fabric","neon-panel","portal","lantern"}
pool=ThreadPoolExecutor(max_workers=1)
app=FastAPI(title="IITaku Studio processor",version="1.0.0")
origins=os.getenv("ALLOWED_ORIGINS","http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(CORSMiddleware,allow_origins=[s.strip() for s in origins if s.strip()],allow_methods=["GET","POST","DELETE"],allow_headers=["Authorization","Content-Type","X-Job-Token"])

def db():
    c=sqlite3.connect(DB,timeout=15);c.row_factory=sqlite3.Row;return c

def initialise():
    with db() as c:
        c.execute("CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, token_hash TEXT, status TEXT, progress REAL, error TEXT, output TEXT, created REAL, ip TEXT, plan TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS keys(token_hash TEXT PRIMARY KEY, plan TEXT, expires REAL, consumed_by TEXT)")

initialise()

@app.on_event("startup")
def recover_worker():
    with db() as c:
        c.execute("UPDATE keys SET consumed_by=NULL WHERE consumed_by IN (SELECT id FROM jobs WHERE status IN ('queued','running'))")
        c.execute("UPDATE jobs SET status='failed',error='Worker restarted; submit again with your export key.' WHERE status IN ('queued','running')")

def digest(s):return hashlib.sha256(s.encode()).hexdigest()

def paid_key(c, authorization, plan, job_id):
    token=authorization.removeprefix("Bearer ") if authorization.startswith("Bearer ") else ""
    row=c.execute("SELECT * FROM keys WHERE token_hash=?",(digest(token),)).fetchone()
    if not row or row["plan"]!=plan or row["expires"]<time.time() or row["consumed_by"]:raise HTTPException(403,"A valid, unused key for this plan is required.")
    c.execute("UPDATE keys SET consumed_by=? WHERE token_hash=?",(job_id,digest(token)))

def job_row(job_id, token):
    with db() as c:row=c.execute("SELECT * FROM jobs WHERE id=?",(job_id,)).fetchone()
    if not row or not secrets.compare_digest(row["token_hash"],digest(token or "")):raise HTTPException(404,"Export not found.")
    return row

def update(job_id, **values):
    with db() as c:
        if values.get("status")=="completed":
            c.execute("UPDATE jobs SET status='completed',progress=100 WHERE id=? AND status='running'",(job_id,))
        else:c.execute("UPDATE jobs SET "+",".join(f"{k}=?" for k in values)+" WHERE id=?",(*values.values(),job_id))

def run_job(job_id, source, output, plan, options):
    deadline=time.monotonic()+int(os.getenv("MAX_JOB_SECONDS","900"))
    def cancel():
        if time.monotonic()>deadline:raise ValueError("Processing time limit reached; try a smaller input. Your paid key has been released.")
        with db() as c:r=c.execute("SELECT status FROM jobs WHERE id=?",(job_id,)).fetchone()
        return not r or r[0]=="cancelled"
    def progress(value):
        with db() as c:c.execute("UPDATE jobs SET progress=? WHERE id=? AND status='running'",(value,job_id))
    try:
        if cancel():raise processing.Cancelled()
        with db() as c:c.execute("UPDATE jobs SET status='running' WHERE id=? AND status='queued'",(job_id,))
        if plan["kind"]=="sr":processing.upscale(source,output,plan["edge"],options,WEIGHTS,progress,cancel)
        else:processing.optical_flow(source,output,plan,options,progress,cancel)
        if cancel():raise processing.Cancelled()
        update(job_id,status="completed")
    except processing.Cancelled:
        update(job_id,status="cancelled")
        output.unlink(missing_ok=True)
    except Exception as e:
        update(job_id,status="failed",error=str(e)[:300] if isinstance(e,ValueError) else "Processing failed. Contact the studio and retry; your paid key has been released.")
    finally:
        source.unlink(missing_ok=True)
        with db() as c:
            c.execute("UPDATE keys SET consumed_by=NULL WHERE consumed_by=? AND (SELECT status FROM jobs WHERE id=?) IN ('failed','cancelled')",(job_id,job_id))

def cleanup():
    with db() as c:
        rows=c.execute("SELECT id FROM jobs WHERE created<? AND status NOT IN ('queued','running')",(time.time()-86400,)).fetchall()
        for r in rows:shutil.rmtree(DATA/r[0],ignore_errors=True)
        c.execute("DELETE FROM jobs WHERE created<? AND status NOT IN ('queued','running')",(time.time()-86400,))
        c.execute("DELETE FROM keys WHERE expires<?",(time.time(),))

@app.get("/v1/health")
def health():
    return {"status":"ok","optical_flow":bool(shutil.which("ffmpeg") and shutil.which("ffprobe")),"anime_sr":WEIGHTS.is_file() and importlib.util.find_spec("torch") is not None,"retention_hours":24}

@app.post("/v1/jobs",status_code=202)
async def create_job(request:Request,file:UploadFile=File(...),plan_id:str=Form(...),retime:str=Form("slow"),start:float=Form(0),end:float=Form(5),brightness:float=Form(100),contrast:float=Form(100),saturation:float=Form(100),rotation:int=Form(0),crop:str=Form("original"),format:str=Form("png"),authorization:str=Header("")):
    if plan_id not in PLANS:raise HTTPException(400,"Unknown plan.")
    plan=PLANS[plan_id]
    values=[start,end,brightness,contrast,saturation]
    if not all(math.isfinite(v) for v in values) or not all(0<=v<=200 for v in [brightness,contrast,saturation]) or rotation not in [0,90,180,270] or crop not in ["original","square","portrait","landscape"] or format not in ["png","jpg"] or retime not in ["slow","smooth"]:raise HTTPException(400,"Invalid edit options.")
    if plan["kind"]=="flow" and (start<0 or end<=start or end-start>plan["seconds"]+.001):raise HTTPException(400,"Clip exceeds this plan's duration limit.")
    if plan["kind"]=="sr" and not health()["anime_sr"]:raise HTTPException(503,"AI model is not installed on this worker.")
    if plan["kind"]=="flow" and not health()["optical_flow"]:raise HTTPException(503,"FFmpeg is not installed on this worker.")
    cleanup();job_id=uuid.uuid4().hex;folder=DATA/job_id;folder.mkdir();source=folder/"input";size=0
    try:
        with source.open("wb") as dest:
            while chunk:=await file.read(1024*1024):
                size+=len(chunk)
                if size>40*1024*1024:raise HTTPException(413,"Maximum upload size is 40 MB.")
                dest.write(chunk)
        if not size:raise HTTPException(400,"Empty file.")
        try:
            if plan["kind"]=="sr":
                with Image.open(source) as im:
                    if im.format not in ["PNG","JPEG","WEBP"] or im.width*im.height>18_000_000:raise ValueError("Use PNG, JPEG or WebP up to 18 megapixels.")
                    im.verify()
            else:
                duration,_=processing.probe_video(source)
                if end>duration+.05:raise ValueError("Selected clip exceeds source duration.")
        except Exception as e:raise HTTPException(400,str(e) if isinstance(e,ValueError) else "Could not decode this file.")
        token=secrets.token_urlsafe(32);output=folder/("output.mp4" if plan["kind"]=="flow" else f"output.{format}")
        # Never accept paid status or limits from the browser. Reserve entitlement atomically.
        ip=digest(request.client.host if request.client else "unknown");day=time.time()-86400
        with db() as c:
            c.execute("BEGIN IMMEDIATE")
            queued=c.execute("SELECT count(*) FROM jobs WHERE status IN ('queued','running')").fetchone()[0]
            if queued>=int(os.getenv("MAX_QUEUE","8")):raise HTTPException(429,"The processor queue is full. Try later.")
            if plan["price"]:paid_key(c,authorization,plan_id,job_id)
            else:
                local=c.execute("SELECT count(*) FROM jobs WHERE ip=? AND created>? AND plan IN ('sr_2k','flow_free')",(ip,day)).fetchone()[0]
                total=c.execute("SELECT count(*) FROM jobs WHERE created>? AND plan IN ('sr_2k','flow_free')",(day,)).fetchone()[0]
                if local>=int(os.getenv("FREE_IP_DAILY","3")) or total>=int(os.getenv("FREE_GLOBAL_DAILY","20")):raise HTTPException(429,"Today's free processing allowance has been reached.")
            c.execute("INSERT INTO jobs VALUES(?,?,?,?,?,?,?,?,?)",(job_id,digest(token),"queued",0,"",str(output),time.time(),ip,plan_id))
        options=dict(retime=retime,start=start,end=end,brightness=brightness,contrast=contrast,saturation=saturation,rotation=rotation,crop=crop)
        pool.submit(run_job,job_id,source,output,plan,options)
        return {"id":job_id,"token":token,"status":"queued","progress":0}
    except Exception:
        shutil.rmtree(folder,ignore_errors=True);raise
    finally:await file.close()

@app.get("/v1/jobs/{job_id}")
def status(job_id:str,x_job_token:str=Header("")):
    row=job_row(job_id,x_job_token)
    return {k:row[k] for k in ["id","status","progress","error"]}

@app.get("/v1/jobs/{job_id}/output")
def output(job_id:str,x_job_token:str=Header("")):
    row=job_row(job_id,x_job_token);path=Path(row["output"])
    if row["status"]!="completed" or not path.is_file():raise HTTPException(409,"Export is not ready or has expired.")
    return FileResponse(path,filename=f"iitaku-{job_id[:8]}{path.suffix}")

@app.delete("/v1/jobs/{job_id}")
def cancel(job_id:str,x_job_token:str=Header("")):
    row=job_row(job_id,x_job_token)
    if row["status"] in ["queued","running"]:
        with db() as c:c.execute("UPDATE jobs SET status='cancelled' WHERE id=? AND status IN ('queued','running')",(job_id,))
    return {"status":"cancelled" if row["status"] in ["queued","running"] else row["status"]}

@app.get("/v1/products/{product}/download")
def product_download(product:str,authorization:str=Header("")):
    if product not in PREMIUM or not (PRODUCTS/f"{product}.zip").is_file():raise HTTPException(404,"Pack unavailable.")
    with db() as c:
        c.execute("BEGIN IMMEDIATE");paid_key(c,authorization,f"product:{product}",f"download:{uuid.uuid4().hex}")
    return FileResponse(PRODUCTS/f"{product}.zip",filename=f"{product}.zip")
