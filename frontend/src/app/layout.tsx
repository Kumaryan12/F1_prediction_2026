import "./globals.css";
import type { Metadata } from "next";
import SakuraParticles from "@/components/SakuraParticles";

export const metadata: Metadata = {
  title: "F1 Race Predictor | Miami GP",
  description: "Machine learning race predictions, confidence bands, and telemetry insights for the Miami International Autodrome",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      {/* Selection color updated to the new Hot Magenta / Vice Pink */}
      <body className="min-h-screen antialiased selection:bg-vice-pink selection:text-white relative">
        
        {/* THE NEON STORM IS HERE */}
        <SakuraParticles />
        
        {/* Miami Cyan to Vice Pink Accent Line across the top of the browser */}
        <div className="h-1 w-full bg-gradient-to-r from-miami-cyan via-purple-500 to-vice-pink shadow-[0_0_15px_rgba(13,240,214,0.8)] relative z-50" />
        
        {/* Main layout wrapper to keep things centered and constrained */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
          {children}
        </main>
      </body>
    </html>
  );
}