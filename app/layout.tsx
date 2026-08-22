import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  metadataBase: new URL('https://kokunoyumeto.github.io/program-matematika-indonesia/'),
  title: 'Program Matematika Indonesia',
  description: 'Peta belajar matematika terbuka dalam Bahasa Indonesia, dari fondasi hingga kesiapan riset.',
  openGraph: {
    title: 'Program Matematika Indonesia',
    description: 'Peta belajar matematika terbuka dalam Bahasa Indonesia, dari fondasi hingga kesiapan riset.',
    type: 'website',
    locale: 'id_ID',
    images: [{ url: 'https://kokunoyumeto.github.io/program-matematika-indonesia/og.png', width: 1200, height: 630, alt: 'Program Matematika Indonesia' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Program Matematika Indonesia',
    description: 'Peta belajar matematika terbuka dalam Bahasa Indonesia, dari fondasi hingga kesiapan riset.',
    images: ['https://kokunoyumeto.github.io/program-matematika-indonesia/og.png'],
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="id">
      <body>{children}</body>
    </html>
  );
}
