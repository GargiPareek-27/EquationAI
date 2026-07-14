// frontend/app/layout.tsx
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EquationAI",
  description: "Verified step-by-step mathematical reasoning",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="bg-[#0F1B2D] min-h-screen antialiased">{children}</body>
    </html>
  );
}