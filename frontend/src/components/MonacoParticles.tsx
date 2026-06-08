"use client";

import { useEffect, useState, useRef } from "react";

type Particle = {
  id: number;
  left: string;
  animationDuration: string;
  animationDelay: string;
  size: string;
  type: "spark" | "confetti";
};

// --- INDIVIDUAL INTERACTIVE CONFETTI/SPARK ---
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

  const isConfetti = particle.type === "confetti";
  
  // Apply our luxurious Monaco shadows
  const glowShadow = isConfetti 
    ? "shadow-[0_0_12px_rgba(212,175,55,0.8)]"  // Casino Gold Glow
    : "shadow-[0_0_12px_rgba(0,163,224,0.8)]"; // Riviera Blue Glow
  
  const bgColor = isConfetti ? "bg-casino-gold/90" : "bg-riviera-blue/90";
  
  // Confetti is square, sparks are perfectly round
  const shape = isConfetti ? "rounded-sm" : "rounded-full";

  return (
    <div
      className="absolute pointer-events-auto"
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
      <div
        className={`${bgColor} ${shape} ${glowShadow} transition-all duration-1000 ease-out`}
        style={{
          width: particle.size,
          height: particle.size,
          transform: wind.isBlown
            ? `translate(${wind.x}px, ${wind.y}px) rotate(${Math.random() * 720}deg) scale(1.5)`
            : 'translate(0px, 0px) rotate(0deg) scale(1)',
          opacity: wind.isBlown ? 0 : 1,
        }}
      />
    </div>
  );
}

// --- MAIN WEATHER SYSTEM COMPONENT ---
export default function MonacoParticles() {
  const [particles, setParticles] = useState<Particle[]>([]);

  useEffect(() => {
    // 50 particles for a luxurious champagne & confetti shower
    const newParticles = Array.from({ length: 50 }).map((_, i) => {
      return {
        id: i,
        left: `${Math.random() * 100}vw`,
        // Slightly faster fall duration to simulate popping champagne
        animationDuration: `${Math.random() * 6 + 4}s`, 
        animationDelay: `-${Math.random() * 15}s`, 
        // Smaller, finer sizes
        size: `${Math.random() * 6 + 4}px`, 
        // Mix of gold squares and blue circles
        type: Math.random() > 0.6 ? "confetti" : "spark", 
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