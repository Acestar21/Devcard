import './globals.css';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'DevCard',
  description: 'The identity layer for developers',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} antialiased`}>
        <div className="freeTierBanner">
          Running on free hosting — occasional slow loads are expected.
        </div>
        {children}
      </body>
    </html>
  );
}
