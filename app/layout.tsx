import type { Metadata, Viewport } from 'next'
import './globals.css'
import { AuthProvider } from '@/lib/auth-context'

export const metadata: Metadata = {
  title: 'BizPromptAI - Save 12+ Hours Weekly with AI Prompts',
  description: '47 battle-tested ChatGPT prompts that automate your business operations, boost productivity, and scale your success.',
  keywords: ['AI prompts', 'ChatGPT', 'business automation', 'productivity', 'marketing'],
  authors: [{ name: 'BizPromptAI' }],
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className="antialiased">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}