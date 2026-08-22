import "./globals.css";
import type { Metadata } from "next";
import HungaryAtmosphere from "@/components/HungaryAtmosphere";

export const metadata: Metadata = {
  title: "Hungarian Grand Prix 2026 | F1 Race Intelligence",
  description:
    "Machine-learning race predictions, podium probabilities and performance insights for the 2026 Hungarian Grand Prix at the Hungaroring.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="relative min-h-screen antialiased selection:bg-hungary-red selection:text-white">
        <HungaryAtmosphere />
        <main className="relative z-10 mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
          {children}
        </main>
      </body>
    </html>
  );
}
