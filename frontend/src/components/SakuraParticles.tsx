"use client";

import { useEffect, useState, useRef } from "react";

type Particle = {
  id: number;
  left: string;
  animationDuration: string;
  animationDelay: string;
  size: string;
};

// --- INDIVIDUAL INTERACTIVE LEAF ---
function InteractiveParticle({ particle }: { particle: Particle }) {
  const [wind, setWind] = useState({ x: 0, y: 0, isBlown: false });
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const handleMouseOver = (e: React.MouseEvent) => {
    if (wind.isBlown) return;

    let forceX = e.movementX;
    let forceY = e.movementY;

    // If mouse is moving slowly, add a random scatter gust
    if (Math.abs(forceX) < 2 && Math.abs(forceY) < 2) {
      forceX = (Math.random() - 0.5) * 40;
      forceY = (Math.random() - 0.5) * 40;
    }

    setWind({ 
      x: forceX * 5, 
      y: forceY * 5 - 30, 
      isBlown: true 
    });

    if (timerRef.current) clearTimeout(timerRef.current);

    timerRef.current = setTimeout(() => {
      setWind({ x: 0, y: 0, isBlown: false });
    }, 1500);
  };

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  return (
    <div
      className="absolute pointer-events-auto text-maple-red"
      style={{
        left: particle.left,
        top: '-10%',
        animation: `
          fall ${particle.animationDuration} linear infinite ${particle.animationDelay},
          sway ${particle.animationDuration} ease-in-out infinite alternate ${particle.animationDelay}
        `,
        padding: '2.5rem',
        marginLeft: '-2.5rem',
        marginTop: '-2.5rem',
      }}
      onMouseOver={handleMouseOver}
    >
      {/* Exact Canadian Flag Maple Leaf SVG */}
      <svg
        viewBox="0 0 512 512"
        fill="currentColor"
        className="drop-shadow-[0_0_10px_rgba(229,24,55,0.8)] transition-all duration-1000 ease-out"
        style={{
          width: particle.size,
          height: particle.size,
          transform: wind.isBlown
            ? `translate(${wind.x}px, ${wind.y}px) rotate(${Math.random() * 720}deg) scale(1.5)`
            : 'translate(0px, 0px) rotate(0deg) scale(1)',
          opacity: wind.isBlown ? 0 : 1,
        }}
      >
        <path d="M304 432h-96v-80l-72 40-16-48 48-48-80-16-16-64 80-16-32-64 48-16 64 64 24-80 24 80 64-64 48 16-32 64 80 16-16 64-80 16 48 48-16 48-72-40v80z" />
      </svg>
    </div>
  );
}

// --- MAIN WEATHER SYSTEM COMPONENT ---
export default function MontrealParticles() {
  const [particles, setParticles] = useState<Particle[]>([]);

  useEffect(() => {
    // Reduced from 60 to 24 for a much cleaner, less chaotic look
    const newParticles = Array.from({ length: 24 }).map((_, i) => {
      return {
        id: i,
        left: `${Math.random() * 100}vw`,
        animationDuration: `${Math.random() * 7 + 7}s`,
        animationDelay: `-${Math.random() * 15}s`, 
        // Increased base size so the leaf shape is clearly visible
        size: `${Math.random() * 16 + 14}px`, 
      }; 
    });
    
    setParticles(newParticles);
  }, []);

  if (particles.length === 0) return null;

  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden" aria-hidden="true">
      {particles.map((particle) => (
        <InteractiveParticle key={particle.id} particle={particle} />
      ))}
    </div>
  );
}