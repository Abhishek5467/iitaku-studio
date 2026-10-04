"use client";

import { useState } from "react";
import { Instagram } from "@/components/social-icons";
import { Play, Plus } from "lucide-react";
import { Dialog, DialogContent, DialogDescription, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { assetUrl } from "@/lib/site-assets";
import type { MediaItem } from "@/lib/portfolio-media";

export function PortfolioMediaGallery({ items, instagram }: { items: MediaItem[]; instagram: string }) {
  const [category, setCategory] = useState("All pieces");
  const [visibleCount, setVisibleCount] = useState(12);
  const categories = ["All pieces", ...new Set(items.map(item => item.category))];
  const selected = categories.includes(category) ? category : "All pieces";
  const filtered = items.filter(item => selected === "All pieces" || item.category === selected);
  return <section id="art" className="art-section"><div className="container section">
    <div className="section-heading"><div><span className="section-number">02 / THE OTHER SIDE OF MY BRAIN</span>
      <h2>A little more <em>imagination.</em></h2></div>
      <a className="text-link" href={instagram} target="_blank" rel="noopener noreferrer"><Instagram size={18} /> See my Instagram</a>
    </div>
    <div className="art-intro"><p>Renders, illustrations and moving images. Explore a piece to see it in full.</p>
      <div className="filters" aria-label="Filter artworks">{categories.map(value => <button key={value}
        className={selected === value ? "filter active" : "filter"} aria-pressed={selected === value}
        onClick={() => { setCategory(value); setVisibleCount(12); }}>{value}</button>)}</div>
    </div>
    <p className="media-count" role="status">{filtered.length} {filtered.length === 1 ? "piece" : "pieces"}</p>
    <div className="art-grid managed-art-grid">{filtered.slice(0, visibleCount).map(item => <Dialog key={item.id}>
      <DialogTrigger asChild><button className="art-tile managed-art-tile" aria-label={`Open ${item.title}`}>
        <img src={assetUrl(item.thumbnail)} alt={item.alt} loading="lazy" decoding="async" />
        {item.kind === "video" && <span className="media-video-label"><Play size={15} /> Film</span>}
        <span className="art-tile-caption"><span>{item.title}<small>{item.caption}</small></span>
          {item.kind === "video" ? <Play size={21} /> : <Plus size={21} />}</span>
      </button></DialogTrigger>
      <DialogContent className="art-dialog media-dialog"><DialogTitle>{item.title}</DialogTitle>
        <DialogDescription>{item.caption || item.category}</DialogDescription>
        {item.kind === "video" ? <video className="media-video" controls playsInline preload="none"
          poster={assetUrl(item.thumbnail)} aria-label={item.title}><source src={assetUrl(item.src)} type="video/mp4" />
          Your browser does not support this video. <a href={assetUrl(item.src)}>Open the video</a></video>
          : <img src={assetUrl(item.src)} alt={item.alt} className="lightbox-image" />}
        <a className="text-link" href={instagram} target="_blank" rel="noopener noreferrer"><Instagram size={17} /> More on Instagram</a>
      </DialogContent>
    </Dialog>)}</div>
    {filtered.length > visibleCount && <button className="button secondary media-show-more"
      onClick={() => setVisibleCount(value => value + 12)}>Show more work</button>}
    {!filtered.length && <p>No work in this category yet.</p>}
  </div></section>;
}
