"use client";

import { useEffect, useState, useRef } from "react";

type Particle = {
  id: number;
  left: string;
  animationDuration: string;
  animationDelay: string;
  size: string;
  colorTheme: "cyan" | "pink";
  styleType: "solid" | "ring" | "square";
};

// --- INDIVIDUAL INTERACTIVE NEON PARTICLE ---
function InteractiveParticle({ particle }: { particle: Particle }) {
  const [wind, setWind] = useState({ x: 0, y: 0, isBlown: false });
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const handleMouseOver = (e: React.MouseEvent) => {
    if (wind.isBlown) return;

    let forceX = e.movementX;
    let forceY = e.movementY;

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

  const isCyan = particle.colorTheme === "cyan";
  const glowShadow = isCyan 
    ? "shadow-[0_0_12px_rgba(13,240,214,0.8)]" 
    : "shadow-[0_0_12px_rgba(255,16,122,0.8)]";
  
  const borderColor = isCyan ? "border-miami-cyan" : "border-vice-pink";
  const bgColor = isCyan ? "bg-miami-cyan/80" : "bg-vice-pink/80";

  let shapeClasses = "";
  if (particle.styleType === "solid") {
    shapeClasses = `${bgColor} rounded-full border-none`;
  } else if (particle.styleType === "ring") {
    shapeClasses = `bg-transparent border-2 ${borderColor} rounded-full`;
  } else if (particle.styleType === "square") {
    shapeClasses = `${bgColor} rounded-sm border-none`;
  }

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
        className={`${shapeClasses} ${glowShadow} transition-all duration-1000 ease-out`}
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
export default function SakuraParticles() {
  const [particles, setParticles] = useState<Particle[]>([]);

  useEffect(() => {
    const newParticles = Array.from({ length: 60 }).map((_, i) => {
      const randStyle = Math.random();
      let styleType: Particle["styleType"] = "solid";
      if (randStyle > 0.66) styleType = "ring";
      else if (randStyle > 0.33) styleType = "square";

      return {
        id: i,
        left: `${Math.random() * 100}vw`,
        animationDuration: `${Math.random() * 7 + 7}s`,
        // FIX 1: Added the negative sign (-) right before the math
        animationDelay: `-${Math.random() * 15}s`, 
        size: `${Math.random() * 8 + 6}px`,
        colorTheme: Math.random() > 0.5 ? "cyan" : "pink",
        styleType: styleType,
      } as Particle; 
    });
    
    setParticles(newParticles);
  }, []);

  if (particles.length === 0) return null;

  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden" aria-hidden="true">
      {/* FIX 2: Removed 'jsx' from the style tag to ensure global injection */}
      <style>{`
        @keyframes fall {
          0% { transform: translateY(-10vh) rotate(0deg); }
          100% { transform: translateY(110vh) rotate(360deg); }
        }
        @keyframes sway {
          0%, 100% { margin-left: -30px; }
          50% { margin-left: 30px; }
        }
      `}</style>

      {particles.map((particle) => (
        <InteractiveParticle key={particle.id} particle={particle} />
      ))}
    </div>
  );
}