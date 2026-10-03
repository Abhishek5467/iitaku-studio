"""Refine an unseen watertight low mesh. OBJ output has NO retained UVs/rig.
This 64³ pilot is limited to coarse geometry; no 2D texture restoration."""
import argparse
from pathlib import Path
import numpy as np
import torch
import trimesh
from model import Refiner
from prepare_pairs import sdf
from evaluate import mesh
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--mesh",required=True);p.add_argument("--checkpoint",required=True);p.add_argument("--out",required=True);p.add_argument("--size",type=int,default=64);a=p.parse_args()
    source=trimesh.load(a.mesh,force="scene").to_geometry()
    if not source.is_watertight:raise ValueError("A watertight mesh is required")
    center=source.bounds.mean(axis=0);scale=1.6/np.ptp(source.bounds,axis=0).max();source.apply_translation(-center);source.apply_scale(scale)
    grid=sdf(source,a.size);cp=torch.load(a.checkpoint,map_location="cpu",weights_only=False);model=Refiner(cp["width"]);model.load_state_dict(cp["model"]);model.eval()
    with torch.inference_mode():result=model(torch.from_numpy(grid)[None,None])[0,0].numpy()
    output=mesh(result);output.apply_scale(1/scale);output.apply_translation(center);Path(a.out).parent.mkdir(parents=True,exist_ok=True);output.export(a.out);print("Exported inferred geometry. Inspect it; original textures, UVs, rigs and animations are not transferred.")
