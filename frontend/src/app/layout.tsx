import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "F1 Race Predictor | Australian GP",
  description: "Machine learning race predictions, confidence bands, and telemetry insights",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased selection:bg-f1-red selection:text-white">
        {/* F1 Red Accent Line across the top of the browser */}
        <div className="h-1 w-full bg-f1-red shadow-[0_0_10px_rgba(225,6,0,0.8)]" />
        
        {/* Main layout wrapper to keep things centered and constrained */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}