import localFont from "next/font/local";
import "./globals.css";

const outfit = localFont({
  src: "../../public/fonts/Outfit-Variable.ttf",
  variable: "--font-outfit",
  display: "swap",
});

const akira = localFont({
  src: "../../public/fonts/Akira Expanded Demo.otf",
  variable: "--font-akira",
  display: "swap",
});

export const metadata = {
  title: "AEROMINDS",
  description: "Drone 3D Scene Reconstruction",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${outfit.variable} ${akira.variable}`} suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
