import "./globals.css";
import type { Metadata } from "next";
import DutchAtmosphere from "@/components/DutchAtmosphere";

export const metadata: Metadata = {
  title: "Dutch Grand Prix 2026 | F1 Race Intelligence",
  description:
    "Race predictions, podium probabilities and performance insights for the 2026 Dutch Grand Prix at Zandvoort.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="relative min-h-screen antialiased selection:bg-dutch-orange selection:text-black">
        <DutchAtmosphere />
        <main className="relative z-10 mx-auto max-w-[1500px] px-4 py-4 sm:px-6 lg:px-8">
          {children}
        </main>
      </body>
    </html>
  );
}
