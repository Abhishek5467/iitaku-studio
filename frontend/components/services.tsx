"use client";
import { ImagePlus, Film, Box, Palette, Code2 } from "lucide-react";
import { studioUrl } from "@/lib/site-assets";
export function Services() {
  return <section id="services" className="next-section"><div className="container services-heading"><div><span className="section-number">IITAKU STUDIO / CREATOR SERVICES</span><h2>Your next creation.<br /><em>A little easier.</em></h2><p>Image enhancement, motion tools and reusable materials for creators. Start with the free tools and explore the launch catalogue.</p></div><a className="button primary" href={studioUrl()}>Open the editing studio <ImagePlus size={18} /></a></div><div className="container service-grid">
    <a href={studioUrl("upscale")}><ImagePlus /><h3>Super resolution</h3><p>2K free. 4K at ₹29 and 8K at ₹99 per image.</p><span>Local 2K resize available · AI worker connection required</span></a>
    <a href={studioUrl("flow")}><Film /><h3>Optical-flow retiming</h3><p>Free short-clip tier and ₹9, ₹29, ₹99 exports.</p><span>Slow motion or smoother playback · Bounded clip lengths</span></a>
    <a href={studioUrl("textures")}><Palette /><h3>Textures & materials</h3><p>Free starter maps and premium packs from ₹29.</p><span>Tileable maps · Original procedural starter materials</span></a>
    <a href={studioUrl("assets")}><Box /><h3>Assets for your worlds</h3><p>Free game props and premium assets from ₹49.</p><span>GLB + OBJ · Static props · Clear use terms</span></a>
  </div><div className="container service-footnote"><span>Launch prices · Paid exports and packs are requested manually until checkout is connected.</span><a href={studioUrl("roadmap")}><Code2 size={16} /> Explore the reconstruction roadmap</a></div></section>;
}
