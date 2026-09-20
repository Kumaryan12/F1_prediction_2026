import "./globals.css";
import type { Metadata } from "next";
export const metadata: Metadata = {
  title: "AK_predicts — Formula 1 race forecast",
  description: "Explore the predicted Formula 1 classification and the model signals behind it.",
  openGraph: { title: "AK_predicts — Formula 1 race forecast", description: "The predicted classification and every signal behind it.", type: "website" },
};
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
