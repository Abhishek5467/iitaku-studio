"""Run inside Blender: blender -b file.blend --python tools/export_blender.py -- --out path.glb"""
import argparse
import sys
from pathlib import Path
import bpy
arguments=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
p=argparse.ArgumentParser();p.add_argument("--out",required=True);p.add_argument("--selected",action="store_true");a=p.parse_args(arguments)
out=Path(a.out).resolve();out.parent.mkdir(parents=True,exist_ok=True)
if out.suffix.lower()!=".glb":p.error("Output must be .glb")
bpy.ops.export_scene.gltf(filepath=str(out),export_format="GLB",use_selection=a.selected,export_animations=True)
print(f"Exported {out}; preview materials and animation before publishing.")
