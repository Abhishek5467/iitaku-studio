# IITaku Studio — Abhishek Singh / Itsuki

Portable portfolio + creator toolkit source. The public frontend uses React, TypeScript, Vite and Tailwind CSS. It has no proprietary hosting dependency. A separate Python/FastAPI worker runs AI image restoration and FFmpeg/OpenCV video retiming. The project also includes original downloadable starter materials/props, Blender integration scripts and a Kaggle geometry-learning experiment.

No technology is literally future-proof. Standard browser APIs, glTF/GLB, typed React components, a separate HTTP processor and ordinary source-controlled files make this project maintainable and portable.

## Included

| Feature | Launch option | What works now |
|---|---|---|
| Image workspace | Local 2K free; AI 2K free / 4K ₹29 / 8K ₹99 | Browser crop, rotate, colour adjustments and resize; AI worker source included |
| Motion workspace | Free 1280 px long edge, 2×, up to 5 seconds | Trim selection and real optical-flow backend |
| Paid motion | ₹9: 1080p/2×/10s; ₹29: 1080p/4×/20s; ₹99: 4K/4×/30s | Plan limits and one-use server entitlements; payment is manual |
| Textures | Two free; fabric ₹29 / neon panels ₹49 | PNG map ZIP downloads; private premium pack generator |
| Static assets | Crate/platform free; lantern ₹49 / portal ₹79 | Original GLB + geometry-only OBJ; browser orbit preview |
| Blender bridge | Free local viewer | GLB loader, animation playback, export script and folder watcher |
| Reconstruction | Future experimental version | Paired SDF preparation, compact residual network, training, metrics and inference scripts |

2K, 4K and 8K mean **2560, 3840 and 7680 px on the long edge**, preserving aspect ratio. Video plan names use the corresponding maximum long edge. These are output sizes, not guaranteed recovered detail. Launch prices are editable proposals, not validated margins. Current video exports are silent and use an independent Farnebäck baseline, not the proprietary Twixtor plugin. See the processor guide for working-resolution and frame-rate limits.

## Run the frontend

Requirements: Node.js 22.13+ and npm. Python 3.11/3.12 is recommended for the processor/training tools; FFmpeg is required for video. Blender is optional for exporting your work.

```bash
cd frontend
npm ci
npm run dev
```

The default config is a portfolio with a disabled Studio demonstration. For a commercial Studio on a suitable host, copy `.env.example` to `.env`, set `VITE_SHOWCASE_ONLY=false`, leave `VITE_STUDIO_URL` blank to use the internal Studio, and set `VITE_PROCESSOR_URL` to your HTTPS API. Rebuild after changing the config. VITE variables are public; never put keys or merchant secrets in them.

```bash
npm run typecheck
npm run build
npm run preview
```

The internal Studio route is `/#/studio?tab=upscale`. Hash routing avoids static-host refresh errors. Assets use Vite’s base URL so they work under repository paths.

## GitHub Pages

GitHub’s [Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits) exclude sites primarily providing paid commercial SaaS/e-commerce. Use Pages for **your personal portfolio and service showcase**, with the commercial Studio hosted separately. GitHub Pages also cannot execute this Python backend.

1. Extract this ZIP, keeping the root `README.md`, `.github/`, `frontend/`, `backend/`, `training/`, `tools/` and `docs/` structure.
2. Create your GitHub repository, then commit/push these files to its `main` branch. Do not include node_modules, uploads, paid full packs, weights, secrets or training data.
3. Open repository Settings → Pages → Build and deployment → Source → **GitHub Actions**. The included `.github/workflows/pages.yml` builds and deploys the portfolio automatically.
4. Set repository Settings → Secrets and variables → Actions → Variables → `STUDIO_URL` to your separately hosted Studio URL, including its `/studio` or `/#/studio` route. The services section links there. A blank value opens a clearly disabled demonstration instead.
5. For a custom domain, configure it in Pages and set the repository variable `PAGES_CUSTOM_DOMAIN` to that domain so the workflow uses `/` as the asset base. Ordinary project repositories use `/<repository>/`; `username.github.io` repositories use `/` automatically.

Local project-path build example (Linux/macOS):

```bash
BASE_PATH=/my-portfolio/ npm run build
```

Windows PowerShell: `$env:BASE_PATH='/my-portfolio/'; npm run build`. Upload the contents of `frontend/dist/` only if you deploy manually. The source ZIP itself is not a ready-to-serve webpage. No deployment has been made into your GitHub account by this package.

## Where to edit

- Your identity, social links, projects, artwork records, skills and resume labels: `frontend/data/portfolio.ts`.
- Prices, clip limits, texture/asset entries and roadmap: `frontend/data/studio.ts`. Keep backend `PLANS` aligned with price/limit changes.
- Portfolio presentation and dated channel statistics: `frontend/components/portfolio.tsx`.
- Editing workspace: `frontend/components/studio.tsx`.
- Artwork: `frontend/public/art/`; keep filenames to replace screenshot crops directly. [Image guide](docs/IMAGE_GUIDE.md).
- Original `.glb` exports: `frontend/public/models/`. [Blender guide](docs/BLENDER_GUIDE.md).
- Processing and payment-key setup: [Processor guide](docs/PROCESSOR_SETUP.md).
- Mesh dataset needs, 30-hour budget and notebook: [Training plan](docs/TRAINING_PLAN.md).

## Processor, assets and experiments

From the project root, install `backend/requirements.txt`, install FFmpeg and start `python -m uvicorn backend.server:app --workers 1`. Add torch and run `python -m backend.download_weights` for anime AI restoration. The full setup, limits and paid-key issuing process are in `docs/PROCESSOR_SETUP.md`. Checkout is not integrated; requests compose an email and require your confirmation. Paid keys are plan-bound, time-limited and checked on the server.

To regenerate starter packs, install `tools/requirements.txt` and run `python tools/generate_starter_assets.py`. In the portable project, it writes free files to `frontend/public/` and premium source packs to `backend/private_products/`. Free packs have CC0 declarations. Premium delivery files are never inside the static frontend. Source for generating simple starter packs is supplied; these are starter materials/props, not finished hero-quality assets.

Import `training/kaggle_refinement.ipynb` into Kaggle and follow the dataset paths. There is no connected Kaggle account or remote run here. The included tiny local training smoke test establishes plumbing only; it did not outperform the unchanged-input baseline. Do not use it as a production reconstruction claim. Textures, UVs, rigs and animations are not transferred by the pilot mesh network.

## Licence

Project-authored code is MIT. Free generated starter asset packs are CC0; premium generated packs carry their own buyer-use licence. Your resumes, artwork, third-party images/content and brand marks are not automatically relicensed by the code licence. Review `THIRD_PARTY_NOTICES.md` and upstream model/dataset terms before a public commercial release.
