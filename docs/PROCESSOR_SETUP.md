# Run the Studio processor

The frontend and processor are independent. Static hosting cannot run PyTorch or FFmpeg. Deploy this Python worker behind HTTPS on your own CPU/GPU machine; start with one Uvicorn process. This release uses a bounded, single-worker queue and SQLite on persistent local storage. It is not a distributed billing/job system.

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
# Install FFmpeg (both ffmpeg and ffprobe must be on PATH).
python -m uvicorn backend.server:app --host 127.0.0.1 --port 8000 --workers 1
```

Optical flow works on CPU. AI image restoration additionally needs torch and the official anime-6B checkpoint:

```bash
# CPU example; use the official PyTorch installer for your CUDA version:
pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m backend.download_weights
```

The image model runs genuine 4× RRDB inference, then fits the requested long edge using Lanczos. Input restoration is capped at a 1920 px working edge to bound memory; output options are 2560, 3840 and 7680 px long edge. This is not a guarantee of native 8K recovered detail. AI output is RGB; transparency is flattened by the current pipeline. Videos are silent, normalize source timing to at most 30 FPS, interpolate 2×/4× and use approximate bidirectional Farnebäck warping with a simple cut guard. Difficult anime linework, occlusion and cuts need visual review. Twixtor is a separate proprietary product; no Twixtor code or claim of equivalence is included.

Set `VITE_PROCESSOR_URL` in `frontend/.env` to the public HTTPS worker URL, then rebuild. Set `ALLOWED_ORIGINS` on the worker to the exact frontend origin (no wildcard). `GET /v1/health` reports installed capabilities. Set `DATA_DIR` to persistent storage and `ANIME_WEIGHTS` / `PRODUCT_DIR` as needed.

Defaults: 40 MB upload, 18 MP input, 3 free jobs per IP/day, 20 free jobs globally/day, queue capacity 8, a 900-second cooperative processing limit (`MAX_JOB_SECONDS`), output retention 24 hours. Change `FREE_IP_DAILY`, `FREE_GLOBAL_DAILY` and `MAX_QUEUE` after measuring costs. Cleanup runs on new submissions, so a disk that receives no new traffic may retain files longer; add a scheduled cleanup if strict deletion timing is required. No account-based history is retained. Do not put this worker behind a proxy that makes every customer appear as one IP unless you add trusted proxy handling. Internet-scale abuse controls and merchant billing are later work.

## Paid exports and packs

Prices are launch experiments, not validated profit estimates. The frontend’s **Request export/pack** link composes an email; it does not charge a customer. Confirm the file, price and delivery manually. After you verify payment, run on the worker:

```bash
python -m backend.issue_key --plan sr_4k --days 7
python -m backend.issue_key --plan flow_9 --days 7
python -m backend.issue_key --plan product:neon-panel --days 7
```

Send the one-use key to that buyer through your normal fulfilment process. The website accepts export keys for paid jobs; the API validates plan, expiry and use, ignoring client-supplied price/paid flags. Failed or cancelled processing releases an export key for retry. Keys for completed outputs are consumed. Product downloads are an authenticated API endpoint (`Authorization: Bearer <key>`) and can also be delivered manually. Do not issue keys through an unauthenticated HTTP admin endpoint.

Real automated checkout requires your chosen payment provider, server-side order amounts, verified signed webhooks, refunds and tax/receipt rules. No merchant credentials are included. Keep premium ZIPs, keys, uploads and weights out of GitHub and the public frontend. A public static URL does not protect a premium file. `tools/generate_starter_assets.py` can regenerate the supplied private starter packs locally.

## Cost check before expanding

Measure wall time, GPU memory and output quality for each plan. Compute a minimum sustainable price from compute cost + storage/transfer + payment fees + support time. A ₹9 plan has little room for overhead: retain short clips and a daily free budget until the measurements support expansion. Offer recurring subscriptions only after usage limits and fulfilment reliability are measured.

The Dockerfile ships CPU optical flow. Add the correct torch/CUDA environment and mount weights/data for GPU SR; do not assume the CPU image activates CUDA. Back up SQLite outside the public repository. Test CORS, tokens, file deletion and failure retries before accepting paid orders.

References: [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN), [PyTorch installation](https://pytorch.org/get-started/locally/), [OpenCV optical flow](https://docs.opencv.org/4.x/d4/dee/tutorial_optical_flow.html).
