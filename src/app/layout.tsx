import type { Metadata } from 'next'
import { Plus_Jakarta_Sans, Space_Grotesk, IBM_Plex_Mono } from 'next/font/google'
import './globals.css'
import '../styles/globals.css'

// Premium font stack inspired by enterprise design systems
const fontSans = Plus_Jakarta_Sans({ subsets: ['latin'], variable: '--font-sans', display: 'swap' })
const fontDisplay = Space_Grotesk({ subsets: ['latin'], variable: '--font-display', weight: ['400','500','600','700'], display: 'swap' })
const fontMono = IBM_Plex_Mono({ subsets: ['latin'], variable: '--font-mono', weight: ['400','500','600'], display: 'swap' })

export const metadata: Metadata = {
  title: 'Iron Cloud - Autonomous Crawler',
  description: 'World-leading autonomous web intelligence platform with military-grade security, AI orchestration, and enterprise solutions.',
  keywords: ['AI', 'autonomous crawler', 'web intelligence', 'data extraction', 'security', 'enterprise'],
  authors: [{ name: 'Iron Cloud Team' }],
  creator: 'Iron Cloud',
  publisher: 'Iron Cloud',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('http://localhost:3000'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: 'Iron Cloud - Autonomous Crawler',
    description: 'World-leading autonomous web intelligence platform with military-grade security, AI orchestration, and enterprise solutions.',
    url: 'http://localhost:3000',
    siteName: 'Iron Cloud',
    images: [
      {
        url: '/images/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Iron Cloud - Autonomous Crawler',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Iron Cloud - Autonomous Crawler',
    description: 'World-leading autonomous web intelligence platform with military-grade security, AI orchestration, and enterprise solutions.',
    images: ['/images/twitter-image.png'],
    creator: '@ironcloud',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-verification-code',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${fontSans.variable} ${fontDisplay.variable} ${fontMono.variable} antialiased bg-[#0b0b0f] text-zinc-100`}
      >
        <div className="relative min-h-screen selection:bg-white/10 selection:text-white">
          {/* Subtle premium canvas gradient */}
          <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 bg-[radial-gradient(1200px_600px_at_50%_-100px,rgba(100,116,139,0.15),transparent_60%)]" />
          {children}
        </div>
      </body>
    </html>
  )
} 