"use client";

import { useEffect, useState, useRef } from "react";

type Petal = {
  id: number;
  left: string;
  animationDuration: string;
  animationDelay: string;
  size: string;
};

// --- INDIVIDUAL INTERACTIVE PETAL COMPONENT ---
function InteractivePetal({ petal }: { petal: Petal }) {
  const [wind, setWind] = useState({ x: 0, y: 0, isBlown: false });
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const handleMouseOver = (e: React.MouseEvent) => {
    if (wind.isBlown) return;

    // Read mouse velocity. If moving slowly, add a random scatter force.
    let forceX = e.movementX;
    let forceY = e.movementY;

    if (Math.abs(forceX) < 2 && Math.abs(forceY) < 2) {
      forceX = (Math.random() - 0.5) * 40;
      forceY = (Math.random() - 0.5) * 40;
    }

    // Amplify the force and push slightly upward to simulate an updraft
    setWind({ 
      x: forceX * 5, 
      y: forceY * 5 - 30, 
      isBlown: true 
    });

    if (timerRef.current) clearTimeout(timerRef.current);

    // Reset the petal back to normal after 1.5 seconds
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
      className="absolute pointer-events-auto"
      style={{
        left: petal.left,
        top: '-10%',
        // The outer div handles the infinite falling and swaying
        animation: `
          fall ${petal.animationDuration} linear infinite ${petal.animationDelay},
          sway ${petal.animationDuration} ease-in-out infinite alternate ${petal.animationDelay}
        `,
        // Massive invisible padding creates the "Wind Hitbox"
        padding: '2.5rem',
        marginLeft: '-2.5rem',
        marginTop: '-2.5rem',
      }}
      onMouseOver={handleMouseOver}
    >
      {/* YOUR EXACT ORIGINAL LEAF DESIGN */}
      <div
        className="bg-sakura-pink/70 shadow-[0_0_10px_rgba(255,20,147,0.8)] transition-all duration-1000 ease-out"
        style={{
          width: petal.size,
          height: petal.size,
          borderRadius: '100% 0 100% 0',
          // Apply the interactive wind physics
          transform: wind.isBlown
            ? `translate(${wind.x}px, ${wind.y}px) rotate(${Math.random() * 720}deg) scale(1.5)`
            : 'translate(0px, 0px) rotate(0deg) scale(1)',
          opacity: wind.isBlown ? 0 : 1, // Fade out while blowing away
        }}
      />
    </div>
  );
}

// --- MAIN WEATHER SYSTEM COMPONENT ---
export default function SakuraParticles() {
  const [petals, setPetals] = useState<Petal[]>([]);

  useEffect(() => {
    // Generate 40 random petals exactly as you set them up
    const newPetals = Array.from({ length: 60 }).map((_, i) => ({
      id: i,
      left: `${Math.random() * 100}vw`,
      animationDuration: `${Math.random() * 7 + 7}s`,
      animationDelay: `${Math.random() * 5}s`,
      size: `${Math.random() * 8 + 6}px`,
    }));
    
    setPetals(newPetals);
  }, []);

  if (petals.length === 0) return null;

  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden" aria-hidden="true">
      {/* Keyframes to ensure the fall/sway animations work */}
      <style jsx>{`
        @keyframes fall {
          0% { transform: translateY(-10vh) rotate(0deg); }
          100% { transform: translateY(110vh) rotate(360deg); }
        }
        @keyframes sway {
          0%, 100% { margin-left: -30px; }
          50% { margin-left: 30px; }
        }
      `}</style>

      {petals.map((petal) => (
        <InteractivePetal key={petal.id} petal={petal} />
      ))}
    </div>
  );
}