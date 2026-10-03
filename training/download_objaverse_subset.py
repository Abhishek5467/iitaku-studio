"""Optional small CC0-only subset; record per-object rights and attribution.
Prefer your own meshes. Objaverse is broad, noisy and not anime-specific."""
import argparse
import json
from pathlib import Path
import objaverse
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--limit",type=int,default=100);p.add_argument("--out",default="training/objaverse-source.json");a=p.parse_args()
    if not 1<=a.limit<=2000:p.error("Use a small reviewed subset (1–2000)")
    annotations=objaverse.load_annotations();uids=sorted(uid for uid,record in annotations.items() if record.get("license")=="cc0")[:a.limit]
    paths=objaverse.load_objects(uids=uids,download_processes=2)
    rows=[{"path":str(Path(paths[uid]).resolve()),"object_id":uid,"license":"CC0","source":annotations[uid].get("uri",""),"creator":annotations[uid].get("user",{}),"review_required":True} for uid in uids]
    Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(rows,indent=2));print("Downloaded candidate CC0 objects. Verify provenance, mesh validity and unwanted content before pairing.")
