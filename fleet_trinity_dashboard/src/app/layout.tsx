import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FLEET-Safe Trinity Command",
  description: "SOTA Mission Control for OpenVLA Hospital Fleets (Isaac Sim, MuJoCo, RViz2)",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-[#0a0a0f] text-white">
        {children}
      </body>
    </html>
  );
}
