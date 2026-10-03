# Replace the artwork

All gallery artwork comes from your supplied portfolio screenshots and is intentionally easy to replace. For a direct replacement, export a clear WebP with the same filename to `frontend/public/art/`. The build copies it without changing the component code. Keep the original full-resolution source outside the website.

| File | Used for |
|---|---|
| `tunnel.webp` | Hero environment and 3D project card |
| `portrait-drawing.webp` | Hero portrait and illustration gallery |
| `product.webp` | Hero product render and gallery |
| `energy.webp` | Abstract 3D energy render |
| `clock.webp` | Clock render |
| `environment.webp` | Environment scene |
| `chair.webp` | Chair render |
| `cube.webp` | Material/shader experiment |
| `illustration.webp` | Illustration gallery |
| `toon-shader.webp` | Toon shader render, where referenced |
| `neon-shader.webp` | Neon shader render, where referenced |
| `iitaku-avatar.webp` | YouTube channel avatar |

For new artworks, edit `frontend/data/portfolio.ts`: the artwork `id` maps to `art/<id>.webp`. Change the title, caption and alt text to match the real work. Use 1600–2400 px on the long edge and an efficient WebP export. Square images fit most tiles; the hero environment crops to a tall panel. Inspect mobile and desktop after replacement.

The channel counters are dated snapshots. Update the figures in `components/portfolio.tsx` or remove them; this version does not scrape social accounts automatically. PDFs are in `public/resumes/` and their labels are in `data/portfolio.ts`.
