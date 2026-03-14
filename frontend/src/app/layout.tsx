import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "F1 Race Predictor | Chinese GP",
  description: "Machine learning race predictions, confidence bands, and telemetry insights for the Shanghai International Circuit",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased selection:bg-shanghai-red selection:text-white">
        {/* Shanghai Red to Imperial Gold Accent Line across the top of the browser */}
        <div className="h-1 w-full bg-gradient-to-r from-shanghai-red via-f1-red to-imperial-gold shadow-[0_0_15px_rgba(238,28,37,0.8)]" />
        
        {/* Main layout wrapper to keep things centered and constrained */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}