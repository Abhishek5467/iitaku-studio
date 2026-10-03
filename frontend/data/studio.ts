export type StudioTab = "upscale" | "flow" | "textures" | "assets" | "blender" | "roadmap";
export const tabs: { id: StudioTab; title: string }[] = [
  { id: "upscale", title: "Upscale" }, { id: "flow", title: "Optical flow" },
  { id: "textures", title: "Textures" }, { id: "assets", title: "3D assets" },
  { id: "blender", title: "Blender bridge" }, { id: "roadmap", title: "What’s next" },
];
export type Plan = { id: string; title: string; price: number; edge: number; factor: number; seconds: number; caption: string; };
export const upscalePlans: Plan[] = [
  { id: "sr_2k", title: "2K", price: 0, edge: 2560, factor: 4, seconds: 0, caption: "One image · up to 2560 px on the long edge" },
  { id: "sr_4k", title: "4K", price: 29, edge: 3840, factor: 4, seconds: 0, caption: "One image · up to 3840 px on the long edge" },
  { id: "sr_8k", title: "8K", price: 99, edge: 7680, factor: 4, seconds: 0, caption: "One image · up to 7680 px on the long edge" },
];
export const flowPlans: Plan[] = [
  { id: "flow_free", title: "Free flow", price: 0, edge: 1280, factor: 2, seconds: 5, caption: "5-second clip · 720p-class · 2× frames" },
  { id: "flow_9", title: "Quick edit", price: 9, edge: 1920, factor: 2, seconds: 10, caption: "10-second clip · 1080p-class · 2× frames" },
  { id: "flow_29", title: "Creator", price: 29, edge: 1920, factor: 4, seconds: 20, caption: "20-second clip · 1080p-class · 4× frames" },
  { id: "flow_99", title: "Studio", price: 99, edge: 3840, factor: 4, seconds: 30, caption: "30-second clip · 4K-class · 4× frames" },
];
export const money = (price: number) => price === 0 ? "Free" : `₹${price}`;
export const products = [
  { id: "toon-palette", name: "Toon essentials", kind: "texture", price: 0, description: "A tileable palette and roughness set for clean stylized surfaces.", preview: "textures/toon-palette/basecolor.png", file: "downloads/toon-palette.zip", specs: "1024 px · PNG · CC0", tags: ["Toon", "Palette", "PBR maps"] },
  { id: "stone", name: "Stylized stone", kind: "texture", price: 0, description: "A procedural stone surface with base color, normal, roughness and height maps.", preview: "textures/stone/basecolor.png", file: "downloads/stone.zip", specs: "1024 px · PNG · CC0", tags: ["Environment", "Tileable", "PBR maps"] },
  { id: "neon-panel", name: "Neon panel kit", kind: "texture", price: 49, description: "Green emissive panel accents for futuristic scenes.", preview: "textures/neon-panel/preview.png", file: "", specs: "2048 px · 5 maps · Starter pack", tags: ["Sci-fi", "Emissive", "Premium"] },
  { id: "fabric", name: "Anime fabric weave", kind: "texture", price: 29, description: "A woven material base for stylized clothing and props.", preview: "textures/fabric/preview.png", file: "", specs: "2048 px · 4 maps · Starter pack", tags: ["Fabric", "Tileable", "Premium"] },
  { id: "crate", name: "Low-poly supply crate", kind: "asset", price: 0, description: "A modular crate with separately coloured trim for small game scenes.", preview: "models/crate-preview.png", model: "models/crate.glb", file: "downloads/crate.zip", specs: "GLB + OBJ · Static prop · CC0", tags: ["Game prop", "Low poly", "Free"] },
  { id: "platform", name: "Arena platform", kind: "asset", price: 0, description: "A compact beveled-looking platform built from modular pieces.", preview: "models/platform-preview.png", model: "models/platform.glb", file: "downloads/platform.zip", specs: "GLB + OBJ · Static prop · CC0", tags: ["Environment", "Modular", "Free"] },
  { id: "portal", name: "Neon gateway", kind: "asset", price: 79, description: "A modular sci-fi frame with bright inserts and a plinth.", preview: "models/portal-preview.png", model: "", file: "", specs: "GLB + OBJ · Static prop · Starter pack", tags: ["Sci-fi", "Environment", "Premium"] },
  { id: "lantern", name: "Stylized lantern", kind: "asset", price: 49, description: "A compact lantern prop with a base, frame and warm-coloured core.", preview: "models/lantern-preview.png", model: "", file: "", specs: "GLB + OBJ · Static prop · Starter pack", tags: ["Stylized", "Lighting", "Premium"] },
];
export const roadmap = [
  { version: "v1.0", title: "Creator toolkit", status: "This release", details: "Local image editing, 2K image export, processing API source, bounded upscale / flow plans, downloadable starter packs and a Blender GLB preview." },
  { version: "v1.1", title: "Anime motion quality", status: "Planned", details: "Benchmark learned frame interpolation against the current optical-flow baseline; add occlusion checks, shot-aware processing and temporal consistency tests." },
  { version: "v1.2", title: "Mesh refinement lab", status: "Research prototype", details: "Train a compact low-poly-to-high-detail geometry model on paired meshes. Compare with subdivision before offering it as a service." },
  { version: "v2.0", title: "Assisted reconstruction", status: "Future", details: "Multi-view / reference-assisted reconstruction, UV-aware texture baking and integration of artist-controlled refinement into Blender." },
];
