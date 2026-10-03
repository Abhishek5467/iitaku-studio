"""Held-out normalized symmetric Chamfer and normal consistency.
Baseline: unchanged low surface and geometry-preserving subdivision. Subdivision
increases triangle count but adds no lost geometric information."""
import argparse
import json
from pathlib import Path
import numpy as np
import torch
import trimesh
from scipy.spatial import cKDTree
from skimage.measure import marching_cubes
from model import Refiner

def mesh(grid):
    if not grid.min()<0<grid.max():raise ValueError("No zero surface in grid")
    vertices,faces,_,_=marching_cubes(grid,level=0,spacing=(2/(grid.shape[0]-1),)*3)
    return trimesh.Trimesh(vertices=vertices-1,faces=faces,process=False)

def compare(a,b,seed=42):
    p,pi=trimesh.sample.sample_surface(a,4096,seed=seed);q,qi=trimesh.sample.sample_surface(b,4096,seed=seed+1)
    d1,i1=cKDTree(q).query(p);d2,i2=cKDTree(p).query(q)
    normal=(np.abs((a.face_normals[pi]*b.face_normals[qi[i1]]).sum(1)).mean()+np.abs((b.face_normals[qi]*a.face_normals[pi[i2]]).sum(1)).mean())/2
    return {"chamfer_distance":float((d1.mean()+d2.mean())/2),"normal_consistency":float(normal)}

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--pairs",required=True);p.add_argument("--checkpoint",required=True);p.add_argument("--out",default="training/runs/evaluation");a=p.parse_args();root=Path(a.pairs);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    cp=torch.load(a.checkpoint,map_location="cpu",weights_only=False);model=Refiner(cp["width"]);model.load_state_dict(cp["model"]);model.eval();rows=[]
    for row in json.loads((root/"manifest.json").read_text()):
        if row["split"]!="test":continue
        with np.load(root/row["file"]) as pair:low=pair["low"];high=pair["high"]
        with torch.inference_mode():pred=model(torch.from_numpy(low.copy())[None,None])[0,0].numpy()
        target=mesh(high);original=mesh(low);refined=mesh(pred);subdivided=original.subdivide()
        refined.export(out/f"{Path(row['file']).stem}-predicted.obj")
        rows.append({"object_id":row["object_id"],"identity":compare(original,target),"subdivision":compare(subdivided,target),"refiner":compare(refined,target)})
    if not rows:raise ValueError("No held-out test objects")
    (out/"metrics.json").write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
