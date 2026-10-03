# Validation — 3 October 2026

- Portable frontend TypeScript check passed.
- Production Vite build passed at `/` and `/iitaku-portfolio/` bases.
- Repository-base generated HTML references and free download ZIP integrity passed.
- Original hosted frontend TypeScript and production build passed.
- Five processing tests passed: actual optical-flow encode/duration, invalid plan/clip limits, paid access rejection, plan-bound one-use key and output-token access, scene-cut guard.
- Official anime-6B weights loaded with strict state-dict matching; actual 16x16 -> 64x64 neural inference passed. This tiny run is not a full 2K/4K/8K quality or performance benchmark.
- Real watertight-mesh decimation + Open3D signed-distance pair preparation passed at 16 cubed.
- Small local residual-geometry training saved checkpoints and exported held-out predicted OBJ surfaces. It did not show a useful quality improvement over unchanged input. No trained production mesh model is shipped.
- Python sources and every notebook code cell parsed; notebook format validated.
- Public output excludes premium full packs, uploads, keys and model weights.

No browser visual/interaction QA was available in the managed preview environment. Blender export/material scripts were syntax-checked but not executed in Blender. No Kaggle remote run, merchant checkout, GPU hosting or GitHub account deployment was performed. Those setup steps are documented.
