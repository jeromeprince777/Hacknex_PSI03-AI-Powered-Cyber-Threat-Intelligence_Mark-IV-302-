import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ThreatWeave — Cyber Threat Intelligence & Attack Chain Reconstruction",
  description:
    "Evidence-first attack chain reconstruction, temporal correlation, explainable Risk Index, and verified AI analyst console. HNX26PSI03 Qualifier.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} dark h-full`}>
      <body className="min-h-full flex flex-col bg-[#0b0f14] text-slate-100 selection:bg-cyan-500 selection:text-[#0b0f14]">
        {children}
      </body>
    </html>
  );
}
