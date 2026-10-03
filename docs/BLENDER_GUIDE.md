# Connect Blender to IITaku Studio

The viewer supports GLB geometry, standard glTF materials and animation clips. A .blend file is an editable source project, not a browser asset. Keep that source separately.

## Quick path

1. In Blender, select the objects you want to publish, apply scale/rotation, check metre units and remove unused objects.
2. Use Principled BSDF with image textures. Bake procedural toon/neon effects to texture maps where necessary. Blender-only shader nodes do not automatically run in a browser.
3. File → Export → glTF 2.0 → format **GLB**. Export selected objects, materials and any required animation tracks. Check shape keys and armature weights when exporting a character.
4. Open the Studio’s Blender tab and load your GLB. This previews it locally. The model viewer includes an animation selector when clips exist.
5. Put the finished file in `frontend/public/models/my-model.glb`. Add an entry in `frontend/data/studio.ts`, following the free crate entry. For portfolio case studies, add an entry to `frontend/data/portfolio.ts` and a render in `frontend/public/art/`.
6. Commit and push the changed files. GitHub Actions rebuilds the portfolio. Deploy commercial Studio changes on your Studio host.

## Export script

From the project root, with Blender installed:

```bash
blender -b my-scene.blend --python tools/export_blender.py -- --out frontend/public/models/my-scene.glb
```

Add `--selected` to export only selected objects saved in the .blend scene. Test the file in the browser after each material/rig change. The script does not bake arbitrary procedural shaders.

## Keep an export folder connected

Export to a local folder such as `D:/Blender/WebExports`. In another terminal:

```bash
python tools/watch_blender.py --source D:/Blender/WebExports --target frontend/public/models
```

The watcher waits for files to become stable, then copies changed `.glb` files into the website. It neither edits a catalogue entry nor pushes to GitHub. Add each model’s catalogue entry once, then use normal Git commits for later updates. Paid full models belong in `backend/private_products`, not in public models.

## Shaders, rigging and performance

`tools/blender_materials.py` creates reusable Principled, toon-ramp and neon material templates inside Blender. Run it from Blender’s scripting editor or with `--python`. The toon template uses Shader to RGB and is intended for Eevee. Bake it before glTF export. A Blender shader is not a JavaScript shader bundle.

For games, include documented triangle counts, clean normals, collision meshes if needed and LODs. Keep downloadable rigs/animation in a separately reviewed pack. The included props are static; no character rig or motion library is advertised as complete.

Prefer preview GLBs below 10–20 MB; the local viewer permits up to 50 MB. Compress textures, remove unused material slots and check the output with [Khronos glTF Validator](https://github.com/KhronosGroup/glTF-Validator). Private GLBs selected from disk use object URLs; the viewer does not upload them. Online environments/decoder resources may still make browser network requests.

References: [Blender glTF exporter](https://github.com/KhronosGroup/glTF-Blender-IO), [glTF standard](https://www.khronos.org/gltf/), [model-viewer](https://modelviewer.dev/).
