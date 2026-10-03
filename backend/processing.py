import json
import math
import subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageOps

class Cancelled(Exception): pass

def check(cancel):
    if cancel():raise Cancelled()

def edit_image(path, options):
    Image.MAX_IMAGE_PIXELS=18_000_000
    with Image.open(path) as source:
        if source.width*source.height>18_000_000:raise ValueError("Input image exceeds 18 megapixels.")
        source.load();image=ImageOps.exif_transpose(source).convert("RGB")
    ratio={"square":1,"portrait":9/16,"landscape":16/9}.get(options["crop"])
    if ratio:
        w,h=image.size
        if w/h>ratio:left=(w-h*ratio)/2;image=image.crop((round(left),0,round(w-left),h))
        else:top=(h-w/ratio)/2;image=image.crop((0,round(top),w,round(h-top)))
    for cls,key in [(ImageEnhance.Brightness,"brightness"),(ImageEnhance.Contrast,"contrast"),(ImageEnhance.Color,"saturation")]:image=cls(image).enhance(options[key]/100)
    return image.rotate(-options["rotation"],expand=True)

def upscale(path, output, edge, options, weights, progress, cancel):
    import torch
    from backend.rrdb import AnimeRRDB
    check(cancel);image=edit_image(path,options)
    # Inputs above the target are resized before restoration to bound memory.
    working_edge=min(edge,1920)
    if max(image.size)>working_edge:image.thumbnail((working_edge,working_edge),Image.Resampling.LANCZOS)
    device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model=AnimeRRDB().to(device).eval()
    checkpoint=torch.load(weights,map_location="cpu",weights_only=True)
    model.load_state_dict(checkpoint.get("params_ema",checkpoint.get("params",checkpoint)),strict=True)
    rgb=np.asarray(image);h,w=rgb.shape[:2];result=np.empty((h*4,w*4,3),dtype=np.uint8)
    tile=192;pad=16;total=math.ceil(h/tile)*math.ceil(w/tile);done=0
    with torch.inference_mode():
        for y in range(0,h,tile):
            for x in range(0,w,tile):
                check(cancel);x2=min(x+tile,w);y2=min(y+tile,h);a=max(x-pad,0);b=max(y-pad,0);c=min(x2+pad,w);d=min(y2+pad,h)
                tensor=torch.from_numpy(rgb[b:d,a:c].copy().transpose(2,0,1)).float().unsqueeze(0).to(device)/255
                patch=model(tensor).clamp(0,1)[0].permute(1,2,0).cpu().numpy()
                result[y*4:y2*4,x*4:x2*4]=np.rint(patch[(y-b)*4:(y2-b)*4,(x-a)*4:(x2-a)*4]*255).astype(np.uint8)
                done+=1;progress(5+done/total*88)
    image=Image.fromarray(result);scale=edge/max(image.size);image=image.resize(tuple(max(1,round(v*scale)) for v in image.size),Image.Resampling.LANCZOS)
    image.save(output,quality=95);progress(99)

def probe_video(path):
    result=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_type,width,height,avg_frame_rate","-of","json",str(path)],capture_output=True,text=True,timeout=15,check=True)
    info=json.loads(result.stdout);streams=[s for s in info["streams"] if s["codec_type"]=="video"]
    if not streams:raise ValueError("No video stream found.")
    s=streams[0];duration=float(info.get("format",{}).get("duration",0));a,b=map(float,s.get("avg_frame_rate","0/1").split("/"));fps=a/b if b else 0
    if not math.isfinite(duration) or duration<=0 or not 1<=fps<=120:raise ValueError("Unsupported video duration or frame rate.")
    if s["width"]*s["height"]>18_000_000:raise ValueError("Video input exceeds 18 megapixels.")
    return duration,min(fps,30)

def interpolate(a,b,fraction):
    """Approximate inverse warp with bidirectional dense flow, not Twixtor code."""
    ga=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY);gb=cv2.cvtColor(b,cv2.COLOR_BGR2GRAY)
    cut=np.mean(np.abs(ga.astype(np.float32)-gb.astype(np.float32)))>48
    if cut:return a.copy()
    ab=cv2.calcOpticalFlowFarneback(ga,gb,None,.5,3,21,3,5,1.2,0)
    ba=cv2.calcOpticalFlowFarneback(gb,ga,None,.5,3,21,3,5,1.2,0)
    y,x=np.mgrid[0:a.shape[0],0:a.shape[1]].astype(np.float32)
    wa=cv2.remap(a,x-fraction*ab[...,0],y-fraction*ab[...,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    wb=cv2.remap(b,x-(1-fraction)*ba[...,0],y-(1-fraction)*ba[...,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    return cv2.addWeighted(wa,1-fraction,wb,fraction,0)

def optical_flow(path, output, plan, options, progress, cancel):
    duration,fps=probe_video(path);start=options["start"];end=options["end"]
    if end>duration+.05:raise ValueError("Selected clip exceeds the source duration.")
    normal=output.parent/"normalised.mp4";temp=output.parent/"interpolated.mp4"
    # CFR conversion and silent output are deliberate. Cap source frames at 30 FPS.
    edge=plan["edge"]
    scale=f"scale=w='if(gte(iw,ih),min(iw,{edge}),-2)':h='if(lt(iw,ih),min(ih,{edge}),-2)':force_divisible_by=2"
    subprocess.run(["ffmpeg","-v","error","-nostdin","-y","-ss",str(start),"-i",str(path),"-t",str(end-start),"-an","-vf",f"fps={fps},{scale}","-c:v","libx264","-preset","fast","-crf","18",str(normal)],timeout=180,check=True)
    cap=cv2.VideoCapture(str(normal));count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if count<2:cap.release();raise ValueError("Clip needs at least two frames.")
    factor=plan["factor"];output_fps=fps if options["retime"]=="slow" else fps*factor
    writer=cv2.VideoWriter(str(temp),cv2.VideoWriter_fourcc(*"mp4v"),output_fps,(width,height))
    if not writer.isOpened():cap.release();raise ValueError("Video encoder unavailable.")
    try:
        ok,previous=cap.read();index=0
        while ok:
            check(cancel);next_ok,next_frame=cap.read();writer.write(previous)
            if next_ok:
                for n in range(1,factor):check(cancel);writer.write(interpolate(previous,next_frame,n/factor))
            else:
                for _ in range(1,factor):writer.write(previous)
            previous=next_frame;ok=next_ok;index+=1;progress(8+index/count*82)
    finally:cap.release();writer.release()
    check(cancel)
    subprocess.run(["ffmpeg","-v","error","-nostdin","-y","-i",str(temp),"-an","-c:v","libx264","-preset","fast","-crf","19","-pix_fmt","yuv420p","-movflags","+faststart",str(output)],timeout=180,check=True)
    normal.unlink(missing_ok=True);temp.unlink(missing_ok=True);progress(99)
