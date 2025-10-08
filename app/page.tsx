'use client'

import { useState } from 'react'
import { useAuth } from '@/lib/auth-context'
import { AuthModal } from '@/components/auth-modal'
import { Header } from '@/components/header'
import { HeroSection } from '@/components/hero-section'
import { FeaturesSection } from '@/components/features-section'
import { PricingSection } from '@/components/pricing-section'
import { CTASection } from '@/components/cta-section'

export default function HomePage() {
  const [showAuthModal, setShowAuthModal] = useState(false)
  const { user } = useAuth()

  // Redirect authenticated users to dashboard
  if (user) {
    window.location.href = '/dashboard'
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-100">
      <Header onGetAccess={() => setShowAuthModal(true)} />
      <HeroSection onGetAccess={() => setShowAuthModal(true)} />
      <FeaturesSection />
      <CTASection onGetAccess={() => setShowAuthModal(true)} />
      
      {showAuthModal && (
        <AuthModal onClose={() => setShowAuthModal(false)} />
      )}
    </div>
  )
}