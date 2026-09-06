import "./globals.css";
import type { Metadata } from "next";
export const metadata: Metadata = {
  title: "AK_predicts — The race. Before the race. | Italian GP 2026",
  description: "A different perspective on Formula 1. Explore AK_predicts race forecasts, podium probabilities, driver comparisons, and what-if simulations. Monza 2026 edition.",
  openGraph: { title: "AK_predicts — The race. Before the race.", description: "Data meets race-day passion. Explore the Monza edition of AK_predicts.", type: "website" },
};
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
