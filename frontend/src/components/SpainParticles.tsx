"use client";

import { useEffect, useState, useRef } from "react";

type Particle = {
  id: number;
  left: string;
  animationDuration: string;
  animationDelay: string;
  size: string;
  type: "ember" | "flare";
};

// --- INDIVIDUAL INTERACTIVE EMBER/FLARE ---
function InteractiveParticle({ particle }: { particle: Particle }) {
  const [wind, setWind] = useState({ x: 0, y: 0, isBlown: false });
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const handleMouseOver = (e: React.MouseEvent) => {
    if (wind.isBlown) return;

    let forceX = e.movementX;
    let forceY = e.movementY;

    // If mouse is moving slowly, add a random scatter gust to simulate wind on the embers
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

  const isFlare = particle.type === "flare";
  
  // Apply our aggressive Spanish Grand Prix shadows
  const glowShadow = isFlare 
    ? "shadow-[0_0_15px_rgba(218,41,28,0.9)]"  // Catalunya Red Flare Glow
    : "shadow-[0_0_15px_rgba(241,191,0,0.9)]"; // Iberian Yellow Ember Glow
  
  const bgColor = isFlare ? "bg-catalunya-red/90" : "bg-iberian-yellow/90";

  return (
    <div
      className="absolute pointer-events-auto"
      style={{
        left: particle.left,
        top: '0%', // The CSS keyframes we added earlier will push this from 110vh (bottom) to -10vh (top)
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
      <div
        className={`${bgColor} rounded-full ${glowShadow} transition-all duration-1000 ease-out`}
        style={{
          width: particle.size,
          height: particle.size,
          // If a flare is a bit larger, maybe blur it slightly to look like smoke/heat
          filter: isFlare ? 'blur(1px)' : 'none',
          transform: wind.isBlown
            ? `translate(${wind.x}px, ${wind.y}px) rotate(${Math.random() * 720}deg) scale(2)` // Embers expand when disturbed!
            : 'translate(0px, 0px) rotate(0deg) scale(1)',
          opacity: wind.isBlown ? 0 : 1,
        }}
      />
    </div>
  );
}

// --- MAIN WEATHER SYSTEM COMPONENT ---
export default function SpainParticles() {
  const [particles, setParticles] = useState<Particle[]>([]);

  useEffect(() => {
    // 40 particles floating up like heat haze and grandstand flares
    const newParticles = Array.from({ length: 40 }).map((_, i) => {
      return {
        id: i,
        left: `${Math.random() * 100}vw`,
        // Slightly slower, lazier float duration for heat/smoke
        animationDuration: `${Math.random() * 8 + 6}s`, 
        animationDelay: `-${Math.random() * 15}s`, 
        // Varying sizes
        size: `${Math.random() * 5 + 3}px`, 
        // Mix of yellow embers and red flares
        type: Math.random() > 0.5 ? "flare" : "ember", 
      } as Particle; 
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