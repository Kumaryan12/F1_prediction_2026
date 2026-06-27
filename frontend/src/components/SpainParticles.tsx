"use client";

import { useEffect, useState, useRef } from "react";

type Particle = {
  id: number;
  left: string;
  animationDuration: string;
  animationDelay: string;
  size: string;
  type: "spark" | "drop";
};

// --- INDIVIDUAL INTERACTIVE SPARK/RAINDROP ---
function InteractiveParticle({ particle }: { particle: Particle }) {
  const [wind, setWind] = useState({ x: 0, y: 0, isBlown: false });
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const handleMouseOver = (e: React.MouseEvent) => {
    if (wind.isBlown) return;

    let forceX = e.movementX;
    let forceY = e.movementY;

    // Alpine crosswind simulation when the mouse moves slowly
    if (Math.abs(forceX) < 2 && Math.abs(forceY) < 2) {
      forceX = (Math.random() - 0.5) * 40;
      forceY = (Math.random() - 0.5) * 40;
    }

    setWind({ 
      x: forceX * 5, 
      y: forceY * 5, // Pushed sideways rather than just up
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

  const isSpark = particle.type === "spark";
  
  // Apply our sharp Austrian shadows
  const glowShadow = isSpark 
    ? "shadow-[0_0_15px_rgba(227,34,25,0.9)]"  // Spielberg Red Spark Glow
    : "shadow-[0_0_10px_rgba(0,210,127,0.6)]"; // Styrian Green Rain Glow
  
  const bgColor = isSpark ? "bg-spielberg-red/90" : "bg-styrian-green/70";

  return (
    <div
      className="absolute pointer-events-auto"
      style={{
        left: particle.left,
        top: '-10%', // Starts above the screen, gravity pulls it down via globals.css
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
        className={`${bgColor} ${glowShadow} transition-all duration-1000 ease-out`}
        style={{
          width: particle.size,
          // Drops are elongated to look like falling rain, sparks are perfectly round
          height: isSpark ? particle.size : `${parseFloat(particle.size) * 3}px`,
          borderRadius: isSpark ? '50%' : '999px',
          filter: isSpark ? 'none' : 'blur(1px)',
          transform: wind.isBlown
            ? `translate(${wind.x}px, ${wind.y}px) rotate(${Math.random() * 90}deg) scale(0.5)` // Rain/sparks scatter and shrink
            : 'translate(0px, 0px) rotate(0deg) scale(1)',
          opacity: wind.isBlown ? 0 : 1,
        }}
      />
    </div>
  );
}

// --- MAIN WEATHER SYSTEM COMPONENT ---
// (Kept as SpainParticles as requested, but logic is 100% Austria!)
export default function SpainParticles() {
  const [particles, setParticles] = useState<Particle[]>([]);

  useEffect(() => {
    // 60 particles for heavy alpine weather and track sparks
    const newParticles = Array.from({ length: 60 }).map((_, i) => {
      const isSpark = Math.random() > 0.7;
      
      return {
        id: i,
        left: `${Math.random() * 100}vw`,
        // Rain falls much faster than sparks
        animationDuration: isSpark ? `${Math.random() * 4 + 4}s` : `${Math.random() * 2 + 2}s`, 
        animationDelay: `-${Math.random() * 15}s`, 
        // Sparks are tiny, rain drops vary
        size: isSpark ? `${Math.random() * 3 + 2}px` : `${Math.random() * 2 + 1}px`, 
        type: isSpark ? "spark" : "drop", 
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