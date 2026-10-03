"""Generate original starter materials and static props. No downloaded meshes.
Run: python tools/generate_starter_assets.py (requires numpy, Pillow, trimesh, matplotlib).
Premium full-resolution packs stay outside public/."""
from pathlib import Path
import json
import zipfile
import numpy as np
from PIL import Image, ImageDraw
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "frontend/public" if (ROOT/"frontend").is_dir() else ROOT / "public"
PRIVATE = ROOT / "backend/private_products"
CC0 = "Original IITaku starter asset. Dedicated to the public domain under CC0 1.0.\nhttps://creativecommons.org/publicdomain/zero/1.0/\nNo warranty; inspect topology, scale and maps before production use.\n"
PREMIUM = "IITaku original starter pack: commercial project use permitted by the buyer; redistribution of this pack as a standalone product is not permitted. No exclusivity or warranty.\n"

def png(path, values):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.uint8(np.clip(values, 0, 1) * 255)).save(path)

def material(name, size, paid=False):
    y, x = np.mgrid[0:size, 0:size] / size
    if name == "toon-palette":
        colors = np.array([[.23,.20,.39],[.49,.38,.66],[.88,.65,.71],[1,.87,.67],[.50,.76,.69],[.25,.51,.62],[.94,.43,.47],[.96,.94,.83]])
        base = colors[np.minimum((x * 8).astype(int), 7)]
        height = np.zeros_like(x); rough = np.full_like(x, .8)
    elif name == "stone":
        height = .50+.15*np.sin(2*np.pi*6*x)*np.cos(2*np.pi*8*y)+.06*np.sin(2*np.pi*(19*x+13*y))+.02*np.cos(2*np.pi*43*x)
        base = np.stack([.30+.16*height,.32+.16*height,.38+.18*height], -1)
        rough = .72+.20*height
    elif name == "fabric":
        height = .5+.2*np.sin(2*np.pi*128*x)*np.cos(2*np.pi*128*y)
        base = np.stack([.20+.10*height,.14+.08*height,.36+.13*height], -1)
        rough = np.full_like(x,.9)
    else:
        line = (np.minimum(x% .25,.25-x% .25)<.005)|(np.minimum(y% .25,.25-y% .25)<.005)
        height = np.where(line,.25,.6)
        base = np.tile(np.array([.055,.065,.10]),(size,size,1))
        base[line] = [.22,.85,.65]
        rough = np.where(line,.25,.6)
    dy, dx = np.gradient(height)
    normal = np.stack([-dx*size*.03, -dy*size*.03, np.ones_like(x)], -1)
    normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
    dest = PRIVATE / name if paid else PUBLIC / "textures" / name
    dest.mkdir(parents=True,exist_ok=True)
    for filename, arr in {"basecolor":base,"normal":normal*.5+.5,"roughness":rough,"height":height}.items():
        png(dest / f"{filename}.png",arr)
    if name == "neon-panel":
        png(dest / "emissive.png", np.where(line[...,None],np.array([.22,1,.6]),0))
    (dest / "LICENSE.txt").write_text(PREMIUM if paid else CC0)
    (dest / "README.txt").write_text("Base color: sRGB. Normal/roughness/height: Non-Color. Normal convention: OpenGL (+Y). Tileable starter maps. Use height sparingly; map detail is procedural, not a scan.\n")
    if paid:
        preview = Image.open(dest / "basecolor.png").convert("RGB").resize((640,640))
        draw = ImageDraw.Draw(preview); draw.rectangle((0,590,640,640),fill=(19,21,24)); draw.text((24,610),"IITAKU  /  PREMIUM PREVIEW",fill=(194,253,121))
        path=PUBLIC/"textures"/name/"preview.png";path.parent.mkdir(parents=True,exist_ok=True);preview.save(path)
    pack = PRIVATE / f"{name}.zip" if paid else PUBLIC / "downloads" / f"{name}.zip"
    pack.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(pack,"w",zipfile.ZIP_DEFLATED) as z:
        for file in dest.iterdir(): z.write(file,f"{name}/{file.name}")

def box(extents, pos, color):
    mesh=trimesh.creation.box(extents=extents);mesh.apply_translation(pos)
    mesh.visual=trimesh.visual.ColorVisuals(mesh,vertex_colors=color)
    return mesh

def prop(name, paid=False):
    meshes=[];green=[159,222,128,255];dark=[49,57,65,255];purple=[143,122,220,255]
    if name=="crate":
        meshes=[box([1.2,1.2,1.2],[0,0,.6],dark)]
        for a in [-.48,.48]:
            meshes += [box([.08,1.25,1.25],[a,0,.6],green),box([1.25,.08,1.25],[0,a,.6],green)]
    elif name=="platform":
        meshes=[box([2,2,.24],[0,0,.12],dark),box([1.65,1.65,.10],[0,0,.29],purple)]
        for a in [-.9,.9]: meshes.append(box([.07,1.8,.03],[a,0,.26],green))
    elif name=="portal":
        meshes=[box([2.6,.7,.3],[0,0,.15],dark),box([2.4,.5,.25],[0,0,3.15],dark)]
        for a in [-1.1,1.1]: meshes.extend([box([.3,.5,2.8],[a,0,1.7],purple),box([.08,.55,2.65],[a,0,1.7],green)])
    else:
        meshes=[box([.7,.7,.8],[0,0,1.1],[236,191,102,255]),box([.9,.9,.15],[0,0,1.6],purple),box([.9,.9,.15],[0,0,.6],dark)]
        for a in [-.34,.34]:
            for b in [-.34,.34]: meshes.append(box([.06,.06,.95],[a,b,1.1],dark))
        pole=trimesh.creation.cylinder(radius=.045,height=2.2,sections=12);pole.apply_translation([.8,0,1.1]);pole.visual.vertex_colors=dark;meshes.append(pole)
        meshes += [box([1.1,.08,.08],[.4,0,2.15],dark),box([.08,.08,.55],[0,0,1.9],dark)]
    scene=trimesh.Scene()
    for i,mesh in enumerate(meshes): scene.add_geometry(mesh,node_name=f"{name}_{i}")
    dest = PRIVATE / name if paid else PUBLIC / "models"
    dest.mkdir(parents=True,exist_ok=True)
    (dest/f"{name}.glb").write_bytes(scene.export(file_type="glb"))
    combined=trimesh.util.concatenate(meshes)
    (dest/f"{name}.obj").write_text(trimesh.exchange.obj.export_obj(combined))
    licence=PREMIUM if paid else CC0
    pack=PRIVATE/f"{name}.zip" if paid else PUBLIC/"downloads"/f"{name}.zip"
    pack.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(pack,"w",zipfile.ZIP_DEFLATED) as z:
        for ext in ["glb","obj"]:z.write(dest/f"{name}.{ext}",f"{name}/{name}.{ext}")
        z.writestr(f"{name}/LICENSE.txt",licence)
        z.writestr(f"{name}/README.txt","Original static modular prop. Dimensions are metres. GLB includes vertex colours; OBJ is geometry only. No rig or animation.\n")
    fig=plt.figure(figsize=(6.4,6.4),facecolor="#161b20");ax=fig.add_subplot(111,projection="3d");ax.set_facecolor("#161b20")
    for mesh in meshes:
        col=tuple(float(v)/255 for v in mesh.visual.vertex_colors[0,:3])
        ax.add_collection3d(Poly3DCollection(mesh.vertices[mesh.faces],facecolors=[col],edgecolors=[tuple(v*.65 for v in col)],linewidths=.25,alpha=1))
    bounds=combined.bounds;center=bounds.mean(axis=0);radius=(bounds[1]-bounds[0]).max()*.62
    ax.set_xlim(center[0]-radius,center[0]+radius);ax.set_ylim(center[1]-radius,center[1]+radius);ax.set_zlim(center[2]-radius,center[2]+radius);ax.set_box_aspect([1,1,1]);ax.view_init(24,35);ax.set_axis_off()
    if paid: fig.text(.05,.04,"IITAKU / PREMIUM PREVIEW",color="#c1fc7b",fontsize=11)
    out=PUBLIC/"models"/f"{name}-preview.png";out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,dpi=100,bbox_inches="tight",pad_inches=.08);plt.close(fig)
    return {"name":name,"vertices":len(combined.vertices),"triangles":len(combined.faces),"licence":"premium" if paid else "CC0"}

if __name__=="__main__":
    for name in ["toon-palette","stone"]:material(name,1024)
    for name in ["fabric","neon-panel"]:material(name,2048,True)
    metadata=[prop("crate"),prop("platform"),prop("portal",True),prop("lantern",True)]
    (PUBLIC/"models"/"manifest.json").write_text(json.dumps(metadata,indent=2))
    print("Created 4 texture packs and 4 original props; premium source files are private.")
