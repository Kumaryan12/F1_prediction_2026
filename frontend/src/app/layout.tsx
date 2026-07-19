import "./globals.css";
import type { Metadata } from "next";
import BelgiumWeather from "@/components/BelgiumWeather";

export const metadata: Metadata = {
  title: "Belgian Grand Prix 2026 | F1 Race Intelligence",
  description:
    "Machine-learning race predictions, podium probabilities and telemetry insights for the Belgian Grand Prix at Spa-Francorchamps.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="relative min-h-screen antialiased selection:bg-belgian-yellow selection:text-black">
        <BelgiumWeather />
        <div className="relative z-50 flex h-1 w-full">
          <span className="w-1/3 bg-belgian-black" />
          <span className="w-1/3 bg-belgian-yellow shadow-[0_0_14px_rgba(253,218,36,0.45)]" />
          <span className="w-1/3 bg-belgian-red" />
        </div>
        <main className="relative z-10 mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
          {children}
        </main>
      </body>
    </html>
  );
}
