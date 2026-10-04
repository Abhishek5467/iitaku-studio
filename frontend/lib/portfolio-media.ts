import { useEffect, useState } from "react";
import { artworks } from "@/data/portfolio";
import { assetUrl } from "@/lib/site-assets";

export type MediaItem = {
  id: string; kind: "image" | "video"; title: string; category: string;
  caption: string; alt: string; src: string; thumbnail: string;
};
export type HeroRole = "main" | "portrait" | "product" | "avatar";
export type PortfolioMedia = {
  version: 1; items: MediaItem[];
  hero: Partial<Record<HeroRole, { src: string; alt: string }>>;
};
const fallback: PortfolioMedia = { version: 1, hero: {}, items: artworks.map(a => ({
  id: a.id, kind: "image", title: a.title, category: a.type, caption: a.caption,
  alt: a.alt, src: `art/${a.id}.webp`, thumbnail: `art/${a.id}.webp`,
})) };
function localAsset(value: unknown): value is string {
  return typeof value === "string" && /^(media|art)\/[a-zA-Z0-9_./-]+$/.test(value)
    && !value.split("/").includes("..");
}
export function usePortfolioMedia() {
  const [media, setMedia] = useState<PortfolioMedia>(fallback);
  useEffect(() => {
    const controller = new AbortController();
    fetch(assetUrl("media/portfolio.json"), { signal: controller.signal, cache: "no-store" })
      .then(response => { if (!response.ok) throw new Error("Media manifest unavailable"); return response.json(); })
      .then(data => {
        if (data.version !== 1 || !Array.isArray(data.items)) return;
        const seen = new Set<string>();
        const items: MediaItem[] = data.items.filter((item: MediaItem) => {
          const valid = item && typeof item.id === "string" && !seen.has(item.id)
            && (item.kind === "image" || item.kind === "video")
            && [item.title, item.category, item.caption, item.alt].every(value => typeof value === "string")
            && localAsset(item.src) && localAsset(item.thumbnail);
          if (valid) seen.add(item.id);
          return valid;
        });
        const hero: PortfolioMedia["hero"] = {};
        for (const role of ["main", "portrait", "product", "avatar"] as const) {
          const image = data.hero?.[role];
          if (image && localAsset(image.src) && typeof image.alt === "string") hero[role] = image;
        }
        setMedia({ version: 1, items, hero });
      }).catch(() => { /* Existing artwork remains usable if the manifest is missing. */ });
    return () => controller.abort();
  }, []);
  return media;
}
