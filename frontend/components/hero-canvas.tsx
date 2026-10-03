"use client";

import { useEffect, useRef, useState } from "react";

// Decorative Canvas 2D animation. No libraries, remote assets, or network calls.
export function HeroCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas?.getContext("2d");
    const host = canvas?.parentElement;
    if (!canvas || !context || !host) return;
    const motion = matchMedia("(prefers-reduced-motion: reduce)");
    let width = 1, height = 1, frame = 0, last = 0, visible = true;
    let particles: { x: number; y: number; vx: number; vy: number; radius: number }[] = [];
    const pointer = { x: -1000, y: -1000 };

    function draw(delta = 0) {
      if (!context) return;
      context.clearRect(0, 0, width, height);
      particles.forEach(p => {
        const dx = p.x - pointer.x, dy = p.y - pointer.y;
        const distance = Math.hypot(dx, dy);
        if (delta && distance > 0 && distance < 110) {
          const force = (1 - distance / 110) * 38 * delta;
          p.x += dx / distance * force; p.y += dy / distance * force;
        }
        p.x = (p.x + p.vx * delta + width) % width;
        p.y = (p.y + p.vy * delta + height) % height;
      });
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        for (let j = i + 1; j < particles.length; j++) {
          const q = particles[j], distance = Math.hypot(p.x - q.x, p.y - q.y);
          if (distance < 125) {
            context.strokeStyle = `rgba(70,180,168,${(1 - distance / 125) * 0.24})`;
            context.lineWidth = 0.7; context.beginPath();
            context.moveTo(p.x, p.y); context.lineTo(q.x, q.y); context.stroke();
          }
        }
        context.fillStyle = i % 3 ? "rgba(69,180,164,0.5)" : "rgba(235,145,79,0.55)";
        context.beginPath(); context.arc(p.x, p.y, p.radius, 0, Math.PI * 2); context.fill();
      }
    }
    function tick(now: number) {
      frame = 0;
      if (!last || now - last >= 1000 / 30) {
        draw(last ? Math.min((now - last) / 1000, 0.05) : 0);
        last = now;
      }
      frame = requestAnimationFrame(tick);
    }
    function sync() {
      cancelAnimationFrame(frame); frame = 0; last = 0;
      draw();
      if (!paused && !motion.matches && visible && !document.hidden) frame = requestAnimationFrame(tick);
    }
    function resize() {
      const bounds = host!.getBoundingClientRect();
      width = Math.max(1, bounds.width); height = Math.max(1, bounds.height);
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      canvas!.width = Math.round(width * ratio); canvas!.height = Math.round(height * ratio);
      context!.setTransform(ratio, 0, 0, ratio, 0, 0);
      const count = width < 640 ? 24 : 54;
      particles = Array.from({ length: count }, () => ({ x: Math.random() * width, y: Math.random() * height,
        vx: (Math.random() - 0.5) * 18, vy: (Math.random() - 0.5) * 18, radius: 1 + Math.random() * 1.4 }));
      sync();
    }
    function move(event: PointerEvent) {
      if (event.pointerType === "touch") return;
      const bounds = host!.getBoundingClientRect();
      pointer.x = event.clientX - bounds.left; pointer.y = event.clientY - bounds.top;
    }
    function leave() { pointer.x = pointer.y = -1000; }
    const resizeObserver = new ResizeObserver(resize);
    const intersectionObserver = new IntersectionObserver(entries => { visible = entries[0].isIntersecting; sync(); });
    resizeObserver.observe(host); intersectionObserver.observe(host);
    host.addEventListener("pointermove", move); host.addEventListener("pointerleave", leave);
    document.addEventListener("visibilitychange", sync); motion.addEventListener("change", sync);
    resize();
    return () => {
      cancelAnimationFrame(frame); resizeObserver.disconnect(); intersectionObserver.disconnect();
      host.removeEventListener("pointermove", move); host.removeEventListener("pointerleave", leave);
      document.removeEventListener("visibilitychange", sync); motion.removeEventListener("change", sync);
    };
  }, [paused]);

  return <><canvas ref={canvasRef} className="hero-canvas" aria-hidden="true" />
    <button className="canvas-toggle" type="button" aria-pressed={paused} onClick={() => setPaused(value => !value)}>
      {paused ? "Play background" : "Pause background"}
    </button></>;
}
