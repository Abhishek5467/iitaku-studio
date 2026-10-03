# Low-poly → inferred high-detail geometry: first experiment

This is a research pipeline, not a released reconstruction model. A low-poly surface loses information; several different high-detail objects can have the same low-poly input. The network learns a prior and may invent detail. Increasing triangle count alone does not demonstrate reconstruction quality.

## Dataset requirements

Start with **200–500 reviewed source objects for a pipeline pilot**, then target **1,000–2,000** if preparation and GPU timing fit the quota. These are planning estimates, not a guarantee of useful quality. Prefer your own Blender meshes: anime-style static props with a consistent art direction. Separate later character, hair, clothing, texture and rig datasets.

Each training example needs:

- A valid, triangulated, watertight high-detail mesh and a decimated low version in the same orientation and scale.
- Stable `object_id`, source URL/filename, creator, per-object licence, source hash and optional family identifier. Review whether the licence and content permit the intended use.
- Consistent normal direction, no degenerate faces, sensible bounds and enough surface resolution to retain the feature being learned.
- A recorded high/low face count and shared normalized coordinate frame. This pilot creates 64³ signed-distance grids. That grid limits recoverable detail even if the output has many triangles.
- Train/validation/test separation by source object/family. All LODs and augmented versions of an object stay in the same split. Remove identical files and near-duplicate families before splitting.

`prepare_pairs.py` accepts only `own-work` and `CC0` by default, rejects non-watertight meshes and logs rejections. Broad Objaverse objects are a possible starting point; they are not an anime-specific dataset. The optional downloader selects objects annotated CC0, but you must still inspect provenance and content. Dataset/database licensing is separate from each model’s licence. A future CC-BY pipeline must preserve attribution; do not silently add NC, unclear or restricted models to a commercial experiment.

Input manifest example:

```json
[
  {"path":"models/prop-high.glb","object_id":"my-prop-001","license":"own-work","source":"My original Blender scene"}
]
```

## Model and baseline

Input: truncated signed distance of a decimated mesh. Target: signed distance of the normalized high mesh. Model: small residual 3D encoder/decoder, initially the identity mapping. Loss: surface-weighted L1. It is a bounded pilot, not a from-scratch diffusion foundation model.

Evaluate held-out objects with symmetric Chamfer distance and nearest-surface normal consistency. Compare the unchanged input and geometry-preserving subdivision. Inspect silhouettes, sharp edges, thin structures and topology in Blender. Use smooth subdivision as an additional production comparison before releasing a feature; the supplied subdivision baseline preserves the original surface and is explicitly named that way. Measure category-specific improvements, failure rates and inference time. Do not announce success just because training loss falls.

The local analytic smoke test validates training/checkpoint/export plumbing only. Its hidden phase is ambiguous, so it is not evidence that the model can reconstruct real detail. No Kaggle production weights are included. The pipeline outputs geometry without original UVs, texture maps, rigs or animations; UV transfer/baking and rig validation are separate upgrades.

## Use the 30-hour budget

Kaggle’s available quota and accelerator types depend on your account and current availability. Check the notebook settings; do not assume an unconditional 30-hour allowance. Prepare meshes on CPU with GPU disabled, upload the paired grids as a private dataset, and activate a GPU only for training/evaluation.

| Work | Planned GPU hours |
|---|---:|
| Pipeline smoke and memory test | 1 |
| Throughput / batch-size benchmark | 2 |
| Main training in resumable chunks | 18 |
| Held-out evaluation / useful ablations | 4 |
| Buffer | 5 |
| Total | 30 |

Use 3.5-hour chunks with saved `last.pt`, `best.pt` and `metrics.jsonl`. Save notebook output after each chunk and attach it to the next session as input. Resume optimizer, scaler and RNG state from your own checkpoint. A time limit can stop a partial epoch; the next run starts at the next epoch, so it does not replay every sample exactly. Benchmark first and adjust epochs to measured time. Kaggle is an experiment environment, not the always-on paid Studio processor.

## Commands and notebook

Create a Python environment and install `training/requirements.txt`; install the correct torch wheel locally (Kaggle already supplies torch).

```bash
python training/synthetic_pairs.py --out training/pairs/smoke --count 24 --size 32
python training/train.py --pairs training/pairs/smoke --out training/runs/smoke --epochs 2 --hours 0.1
python training/evaluate.py --pairs training/pairs/smoke --checkpoint training/runs/smoke/best.pt --out training/runs/smoke-eval

python training/prepare_pairs.py --source my-meshes.json --out training/pairs/props --size 64 --ratio 0.15
python training/train.py --pairs training/pairs/props --out training/runs/props --hours 3.5
python training/train.py --pairs training/pairs/props --out training/runs/props --hours 3.5 --resume training/runs/props/last.pt
python training/evaluate.py --pairs training/pairs/props --checkpoint training/runs/props/best.pt --out training/runs/props-eval
python training/infer.py --mesh my-low.glb --checkpoint training/runs/props/best.pt --out refined.obj
```

Import `training/kaggle_refinement.ipynb` in Kaggle, attach the source ZIP and your prepared pair dataset, edit the paths, then run the smoke cell before the real training cell. This project has no access to your Kaggle account and does not start a remote run automatically.

## Release gate

Release only after improvement over useful baselines on unseen original meshes, acceptable visual results and measured inference cost. Add UV/texture baking separately. Multi-view reconstruction, characters, rig transfer and animation belong in later versions; they need distinct evaluation data and budget.

Primary references: [Objaverse annotations](https://objaverse.allenai.org/docs/objaverse-1.0/), [Open3D signed distance](https://www.open3d.org/docs/release/tutorial/geometry/distance_queries.html), [Kaggle GPU usage](https://www.kaggle.com/docs/efficient-gpu-usage).
