import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Program Matematika Indonesia',
  description: 'Peta belajar matematika terbuka dalam Bahasa Indonesia, dari fondasi hingga kesiapan riset.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="id">
      <body>{children}</body>
    </html>
  );
}
