import "./globals.css";
import type { Metadata } from "next";
import SakuraParticles from "@/components/SakuraParticles";

export const metadata: Metadata = {
  title: "F1 Race Predictor | Japanese GP",
  description: "Machine learning race predictions, confidence bands, and telemetry insights for the Suzuka International Racing Course",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      {/* Updated selection color to the new neon pink and added relative positioning */}
      <body className="min-h-screen antialiased selection:bg-sakura-pink selection:text-white relative">
        
        {/* The Neon Blossom Weather System */}
        <SakuraParticles />

        {/* Suzuka Red to Sakura Pink Accent Line across the top of the browser */}
        <div className="h-1 w-full bg-gradient-to-r from-suzuka-red via-[#ff4d4d] to-sakura-pink shadow-[0_0_15px_rgba(255,20,147,0.8)] relative z-50" />
        
        {/* Main layout wrapper to keep things centered and constrained */}
        {/* Added relative z-10 so your glassmorphism cards sit ABOVE the falling petals */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
          {children}
        </main>
      </body>
    </html>
  );
}