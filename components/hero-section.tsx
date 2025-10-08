'use client'

import { useState } from 'react'
import { leadAPI } from '@/lib/api'

interface HeroSectionProps {
  onGetAccess: () => void
}

export function HeroSection({ onGetAccess }: HeroSectionProps) {
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleLeadMagnetSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      await leadAPI.submitLeadMagnet(email, name)
      setSubmitted(true)
      setEmail('')
      setName('')
    } catch (error) {
      console.error('Signup failed:', error)
      alert('Signup failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="py-20 text-center animate-fade-in">
      <div className="container mx-auto px-4 max-w-7xl">
        <h2 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
          Save 12+ Hours Weekly with{' '}
          <span className="text-primary-600 bg-gradient-to-r from-primary-600 to-orange-500 bg-clip-text text-transparent">
            AI Prompts
          </span>
        </h2>
        <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed">
          47 battle-tested ChatGPT prompts that automate your business operations, 
          boost productivity, and scale your success.
        </p>

        {!submitted ? (
          <div className="max-w-md mx-auto card animate-slide-up">
            <h3 className="text-xl font-semibold text-primary-600 mb-2">
              Get 5 FREE AI Prompts
            </h3>
            <p className="text-gray-600 mb-6">
              Start automating your business today
            </p>
            <form onSubmit={handleLeadMagnetSubmit} className="space-y-4">
              <input
                type="email"
                placeholder="Your email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="input-field"
                disabled={loading}
              />
              <input
                type="text"
                placeholder="Your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="input-field"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading}
                className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Getting your prompts...
                  </span>
                ) : (
                  'Get FREE Prompts'
                )}
              </button>
            </form>
          </div>
        ) : (
          <div className="max-w-md mx-auto bg-green-50 border border-green-200 rounded-xl p-6 animate-slide-up">
            <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-full mx-auto mb-4">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
              </svg>
            </div>
            <p className="text-green-800 font-medium">
              Check your email for 5 FREE AI prompts and exclusive bonuses!
            </p>
          </div>
        )}
      </div>
    </section>
  )
}