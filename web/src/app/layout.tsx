import type { Metadata } from "next";
import { DM_Sans, Caveat } from "next/font/google";
import "@/app/globals.css";

const bodyFont = DM_Sans({ subsets: ["latin"], weight: ["400", "500", "700"], variable: "--font-body" });
const displayFont = Caveat({ subsets: ["latin"], weight: ["600", "700"], variable: "--font-display" });

export const metadata: Metadata = {
  title: "Prep Bench Studio",
  description: "Turn rough meal-prep notes into a practical weekly plan with groceries and prep artifacts."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${bodyFont.variable} ${displayFont.variable} bg-background text-foreground`}>{children}</body>
    </html>
  );
}
