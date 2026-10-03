// Professional content from supplied resumes and October 2026 screenshots.
// Social metrics are dated snapshots, not live API counters.
export const profile = {
  name: "Abhishek Singh", alias: "Itsuki", email: "abhishek_2301ec35@iitp.ac.in",
  institution: "Indian Institute of Technology Patna", degree: "B.Tech · Electronics & Communication Engineering",
  education: "2023–2027 · Expected graduation", cpi: "7.00 / 10", snapshot: "October 2026",
  socials: {
    youtube: "https://www.youtube.com/@IITakuEdits",
    instagram: "https://www.instagram.com/abhisheksingh_5701/",
    linkedin: "https://www.linkedin.com/in/abhishek-singh-itsuki/",
    github: "https://github.com/Abhishek5467",
    kaggle: "https://www.kaggle.com/Shivaabhishek108",
    codeforces: "https://codeforces.com/profile/journey_to_grandmaster",
    codechef: "https://www.codechef.com/users/abhishek_5701",
  },
};
export type Category = "All work" | "AI & ML" | "Photonics" | "Creative tech" | "Engineering";
export const categories: Category[] = ["All work", "AI & ML", "Photonics", "Creative tech", "Engineering"];
export type Project = {
  id: string; title: string; category: Exclude<Category, "All work">; eyebrow: string;
  description: string; tags: string[]; visual: string; outcome: string; details: string[];
  links?: { label: string; href: string }[];
};
export const projects: Project[] = [
  { id: "prabha", title: "Prabha / PEMAN", category: "Photonics", eyebrow: "PHOTONIC NEURAL COMPUTING · 2026–PRESENT", visual: "mac", outcome: "1,000 stochastic realizations",
    description: "Modeling the building blocks of photonic–electronic neural computing, one validated component at a time.",
    tags: ["Python", "Numerical modeling", "Photonics"],
    details: ["Research under Prof. Sumanta Gupta at IIT Patna, in the Photonics / Optical Communication Group.", "Built modular continuous-wave laser and signed-weight photonic multiply–accumulate models. Laser effects include relative intensity noise and linewidth-induced phase diffusion.", "Validated power, wavelength, sampling-rate and random-seed behavior. An ensemble of 1,000 realizations recovered a modeled 1 MHz linewidth within approximately 5.1%.", "Verified ideal differential MAC outputs at 0.1, 1 and 10 mW. Ongoing work explores microring weighting and balanced detection toward a PEMAN architecture."],
  },
  { id: "surveillance", title: "Seeing the unexpected", category: "AI & ML", eyebrow: "VIDEO ANOMALY DETECTION · 2026", visual: "auc", outcome: "0.734 ROC-AUC · UCSD Ped2",
    description: "A 3D convolutional autoencoder with Hybrid Patch Feature Scoring for video anomaly detection.",
    tags: ["PyTorch", "Computer vision", "OpenCV"],
    details: ["Video Surveillance Research Internship under Prof. Mahesh Kumar Kolekar at IIT Patna, May–July 2026.", "Built the preprocessing, training, inference and evaluation pipeline for a 3D convolutional autoencoder. Hybrid Patch Feature Scoring combines patch reconstruction and latent-feature errors.", "Achieved ROC-AUC of 0.734 on UCSD Ped2, compared with a baseline of approximately 0.66–0.675. Worked with UCSD Pedestrian, CUHK Avenue and ShanghaiTech datasets.", "Prototyped gradient-based anomaly localization and Llama 3 explanations through the Groq API. Documented evaluation using ROC curves and training-loss plots."],
    links: [{ label: "View project repository", href: "https://github.com/Abhishek5467/ai-surveillance-system" }],
  },
  { id: "rendering", title: "Code meets the third dimension", category: "Creative tech", eyebrow: "CUSTOM 3D RENDERING ENGINE", visual: "art", outcome: "Real-time scenes · Gesture interaction",
    description: "An interactive Three.js / WebGL engine with gesture control, a spline editor and procedural scene generation.",
    tags: ["Three.js", "WebGL", "Blender"],
    details: ["Developed a custom real-time rendering engine with gesture-based interaction using Three.js and WebGL.", "Built a spline editor and procedural scene generation framework. Created and prepared 3D assets in Blender.", "The accompanying creative practice covers modeling, materials, shading, lighting, camera composition and animated renders. The illustration and 3D gallery below contains selections from my supplied Instagram portfolio."],
    links: [{ label: "View project repository", href: "https://github.com/Abhishek5467/Custom-3d-rendering-engine" }, { label: "Explore creative portfolio", href: profile.socials.instagram }],
  },
  { id: "microring", title: "Light, on a smaller scale", category: "Photonics", eyebrow: "SILICON MICRORING RESONATORS · 2026", visual: "ring", outcome: "FDTD · Coupling · Q-factor",
    description: "Studying lateral, vertical and cascaded microring configurations through electromagnetic simulation.",
    tags: ["MEEP", "MPB", "Silicon photonics"],
    details: ["Independent research carried out during May–June 2026 using MEEP FDTD and MPB.", "Simulated lateral, vertical / 3D and parallel-cascaded coupling configurations. Studied coupling-gap dependence, critical coupling, resonance and quality factor.", "Characterized optical modes and effective indices using MPB. Numerical convergence checks helped assess the reliability of simulation results.", "Authored a technical report on silicon photonic microring resonators, coupling optimization, Q-factor analysis and cascaded filter architectures."],
  },
  { id: "stethoscope", title: "Listening through embedded systems", category: "Engineering", eyebrow: "ESP32 SMART STETHOSCOPE · PROTOTYPE", visual: "signal", outcome: "44.1 kHz · Bluetooth streaming",
    description: "An audio acquisition prototype connecting sensor hardware, signal processing and a mobile receiver.",
    tags: ["ESP32", "I2S", "Signal processing"],
    details: ["Built an ESP32-based audio acquisition prototype with a MAX9814 microphone amplifier, ADC1_CH0 input and capacitive coupling in the analog signal path.", "Implemented 44.1 kHz, 16-bit mono acquisition using I2S, with a 20–250 Hz bandpass filter.", "Integrated Bluetooth Serial Port Profile streaming with a Cordova mobile application for reception. This is an engineering prototype, without a clinical-performance claim."],
  },
  { id: "usas", title: "From camera streams to data", category: "AI & ML", eyebrow: "USAS INGESTOR ENGINE · PRIVATE REPOSITORY", visual: "pipeline", outcome: "Multi-camera ingestion pipeline",
    description: "Synchronization, preprocessing and storage for CCTV and DOT camera streams supporting surveillance analytics.",
    tags: ["Python", "Video pipelines", "Data engineering"],
    details: ["Built a multi-camera CCTV and DOT stream ingestion pipeline for surveillance analytics.", "Implemented synchronization, preprocessing and storage modules. The repository is private; a technical discussion is available on request."],
  },
  { id: "cloud", title: "Taking an application live", category: "Engineering", eyebrow: "INDITRONIX WEBSITE DEPLOYMENT · SEPTEMBER 2026", visual: "cloud", outcome: "AWS EC2 · Nginx · Cloudflare",
    description: "Deployment of a React / Vite application with SPA routing, TLS configuration and a rollback-friendly release process.",
    tags: ["AWS EC2", "React", "Linux"],
    details: ["Deployed a React / Vite application on Ubuntu EC2 with Nginx single-page application routing and Cloudflare Full TLS configuration.", "Managed an update using a separate release directory, configuration validation and Nginx reload. Retained the previous application directory for rollback.", "Related experience: Software Head at Inditronix AI Labs, April 2025–May 2026, coordinating a multidisciplinary software team for healthcare AI solutions and developing ESP32-based IoT applications."],
  },
];
export const artworks = [
  { id: "tunnel", title: "Neon environment", type: "3D & shading", caption: "Environment, lighting & materials", alt: "Orange and green neon tunnel rendered in 3D" },
  { id: "portrait-drawing", title: "Character study", type: "Illustration", caption: "Anime-inspired drawing", alt: "Hand-drawn anime character with light hair" },
  { id: "product", title: "Product in the light", type: "3D & shading", caption: "Product visualization", alt: "A dark perfume bottle lit in a studio render" },
  { id: "energy", title: "Electric blue", type: "3D & shading", caption: "Shader & lighting exploration", alt: "Abstract blue glowing shader experiment" },
  { id: "illustration", title: "Lines with a story", type: "Illustration", caption: "Manga-inspired illustration", alt: "Black and white manga-inspired eye drawing" },
  { id: "environment", title: "A quieter place", type: "3D & shading", caption: "Stylized environment", alt: "A stylized 3D house with plants and warm wooden surfaces" },
  { id: "clock", title: "Time, rendered", type: "3D & shading", caption: "Modeling & materials", alt: "A gold and red clock in a rendered scene" },
  { id: "chair", title: "An object study", type: "3D & shading", caption: "Form, texture & composition", alt: "A blue and red stylized chair on a dark background" },
  { id: "cube", title: "Everyday geometry", type: "3D & shading", caption: "Modeling & composition", alt: "A modeled puzzle cube resting on a wooden surface" },
] as const;
export const resumes = [
  { title: "Complete portfolio", subtitle: "Engineering, research & creative work", file: "Abhishek_Singh_Resume__.pdf" },
  { title: "AI & machine learning", subtitle: "Computer vision & ML pipelines", file: "Abhishek_Singh_ML_Resume.pdf" },
  { title: "Software & cloud", subtitle: "IT engineer profile", file: "Abhishek_Singh_IT_Engineer_Resume.pdf" },
  { title: "Analytics", subtitle: "Decision analytics · ZS", file: "Abhishek_Singh_ZS_Resume.pdf" },
  { title: "Electronic hardware", subtitle: "Embedded systems · SEDEMAC", file: "Abhishek_Singh_SEDEMAC_Hardware_Resume.pdf" },
  { title: "Chip design", subtitle: "Photonics & hardware · C-DAC", file: "Abhishek_Singh_Resume_CDAC_ChipDesign.pdf" },
];
export const skillGroups = [
  { title: "Code & systems", skills: ["Python", "C++", "C", "SQL", "React", "Three.js", "WebGL", "Git", "Linux", "AWS EC2", "Nginx", "Cloudflare"] },
  { title: "AI & data", skills: ["PyTorch", "TensorFlow", "NumPy", "Pandas", "OpenCV", "Computer vision", "CNNs & autoencoders", "Hugging Face", "Groq API", "Llama 3", "Model evaluation"] },
  { title: "Devices & simulation", skills: ["MEEP / FDTD", "MPB", "Silicon photonics", "Stochastic modeling", "Signal processing", "ESP32", "I2S", "Bluetooth SPP"] },
  { title: "Creative practice", skills: ["Blender", "3D modeling", "Materials & shaders", "Lighting", "Animation", "Video editing", "Digital illustration"] },
];
export const experience = [
  { date: "May 2026–present", role: "Photonic neural computing research", place: "IIT Patna · Prof. Sumanta Gupta", description: "Optical MAC primitives, microring weighting, balanced detection and modular simulation toward PEMAN." },
  { date: "May–July 2026", role: "Video surveillance research intern", place: "IIT Patna · Prof. Mahesh Kumar Kolekar", description: "3D autoencoders, Hybrid Patch Feature Scoring, benchmark evaluation and explainability prototypes." },
  { date: "May–June 2026", role: "Independent photonics research", place: "Silicon microring resonators", description: "Electromagnetic simulation, coupling optimization, Q-factor analysis and convergence validation." },
  { date: "April 2025–May 2026", role: "Software Head", place: "Inditronix AI Labs", description: "Software architecture, multidisciplinary team coordination, AWS infrastructure and ESP32 IoT development." },
];
