"""Build 64³ low/high SDF pairs from YOUR watertight high meshes.
Input JSON: [{"path":".../mesh.glb","object_id":"unique-id","license":"CC0","source":"..."}]
Strict default: CC0 or own-work only. See TRAINING_PLAN.md for licence review."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import trimesh

def sdf(mesh,size):
    import open3d as o3d
    legacy=o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(mesh.vertices),o3d.utility.Vector3iVector(mesh.faces))
    scene=o3d.t.geometry.RaycastingScene();scene.add_triangles(o3d.t.geometry.TriangleMesh.from_legacy(legacy))
    grid=np.stack(np.meshgrid(*[np.linspace(-1,1,size,dtype=np.float32)]*3,indexing="ij"),-1)
    values=scene.compute_signed_distance(o3d.core.Tensor(grid)).numpy()
    return np.clip(values/.15,-1,1).astype("float32")

def prepare(source,out,size=64,ratio=.15):
    source=Path(source);out=Path(out);out.mkdir(parents=True,exist_ok=True);records=json.loads(source.read_text());manifest=[];seen=set();seen_hashes=set();rejected=[]
    for record in records:
        uid=record["object_id"]
        if uid in seen:raise ValueError("Duplicate object_id; variants must stay in the same split.")
        seen.add(uid)
        if record.get("license") not in ["CC0","own-work"]:rejected.append({"object_id":uid,"reason":"Default licence filter"});continue
        path=Path(record["path"]);path=path if path.is_absolute() else source.parent/path
        try:
            source_hash=hashlib.sha256(path.read_bytes()).hexdigest()
            if source_hash in seen_hashes:raise ValueError("Identical source file already present; avoid split leakage")
            seen_hashes.add(source_hash)
            scene=trimesh.load(path,force="scene");mesh=scene.to_geometry()
            if not isinstance(mesh,trimesh.Trimesh) or not mesh.is_watertight:raise ValueError("Watertight triangulated mesh required")
            mesh.process(validate=True);mesh.apply_translation(-mesh.bounds.mean(axis=0));mesh.apply_scale(1.6/np.ptp(mesh.bounds,axis=0).max())
            high=sdf(mesh,size);lowmesh=mesh.simplify_quadric_decimation(face_count=max(32,int(len(mesh.faces)*ratio)))
            if not lowmesh.is_watertight:raise ValueError("Decimation broke watertightness")
            low=sdf(lowmesh,size);key=hashlib.sha256(uid.encode()).hexdigest();family_key=hashlib.sha256(record.get("family_id",uid).encode()).hexdigest();bucket=int(family_key[:8],16)%100
            split="train" if bucket<80 else "val" if bucket<90 else "test";file=f"{key[:20]}.npz"
            np.savez_compressed(out/file,low=low,high=high)
            mesh.export(out/f"{key[:20]}-high.ply");lowmesh.export(out/f"{key[:20]}-low.ply")
            manifest.append({**record,"file":file,"split":split,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"high_faces":len(mesh.faces),"low_faces":len(lowmesh.faces),"grid":size})
        except Exception as e:rejected.append({"object_id":uid,"reason":str(e)})
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2));(out/"rejected.json").write_text(json.dumps(rejected,indent=2));print(f"Prepared {len(manifest)} pairs; rejected {len(rejected)}. Inspect manifest and splits before training.")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--out",required=True);p.add_argument("--size",type=int,default=64);p.add_argument("--ratio",type=float,default=.15);a=p.parse_args();prepare(a.source,a.out,a.size,a.ratio)
