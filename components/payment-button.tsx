'use client'

import { useState } from 'react'

interface PaymentButtonProps {
  productType: 'presale' | 'regular'
  price: number
  className?: string
  children?: React.ReactNode
}

export function PaymentButton({ 
  productType, 
  price, 
  className = '', 
  children 
}: PaymentButtonProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handlePayment = async () => {
    setLoading(true)
    setError('')

    try {
      // Get current URL for success/cancel redirects
      const currentUrl = window.location.origin
      const successUrl = `${currentUrl}/success`
      const cancelUrl = `${currentUrl}/`

      // Call backend to create checkout session
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/payments/create-checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_type: productType,
          success_url: successUrl,
          cancel_url: cancelUrl
        })
      })

      if (!response.ok) {
        throw new Error('Failed to create payment session')
      }

      const data = await response.json()
      
      // Redirect to Stripe checkout
      if (data.checkout_url) {
        window.location.href = data.checkout_url
      } else {
        throw new Error('No checkout URL received')
      }

    } catch (error) {
      console.error('Payment error:', error)
      setError(error instanceof Error ? error.message : 'Payment failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full">
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}
      
      <button
        onClick={handlePayment}
        disabled={loading}
        className={`w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      >
        {loading ? (
          <span className="flex items-center justify-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Processing...
          </span>
        ) : (
          children || `Get Full Access - $${price}`
        )}
      </button>
    </div>
  )
}