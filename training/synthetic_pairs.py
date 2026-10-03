"""Small analytic shape pairs for pipeline smoke tests, not an anime dataset."""
import argparse
import json
from pathlib import Path
import numpy as np

def generate(out,count=24,size=32,seed=42):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);rng=np.random.default_rng(seed);manifest=[]
    xyz=np.stack(np.meshgrid(*[np.linspace(-1,1,size)]*3,indexing="ij"),-1)
    r=np.linalg.norm(xyz,axis=-1);theta=np.arctan2(xyz[...,1],xyz[...,0]);phi=np.arccos(np.clip(xyz[...,2]/np.maximum(r,1e-6),-1,1))
    for i in range(count):
        radius=rng.uniform(.42,.70);amplitude=rng.uniform(.008,.035);freq=int(rng.integers(3,8));phase=rng.uniform(0,6.28)
        low=np.clip((r-radius)/.15,-1,1).astype("float32")
        high=np.clip((r-radius-amplitude*np.sin(theta*freq+phase)*np.sin(phi*freq))/.15,-1,1).astype("float32")
        split="train" if i<int(count*.7) else "val" if i<int(count*.85) else "test"
        file=f"synthetic-{i:04d}.npz";np.savez_compressed(out/file,low=low,high=high)
        manifest.append({"file":file,"object_id":f"synthetic-{i}","split":split,"license":"CC0","source":"Analytic synthetic smoke-test pair; phase/detail is ambiguous from low input."})
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2))
    print(f"Wrote {count} object-disjoint analytic pairs at {size}³.")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",default="training/pairs/synthetic");p.add_argument("--count",type=int,default=24);p.add_argument("--size",type=int,default=32);a=p.parse_args();generate(a.out,a.count,a.size)
