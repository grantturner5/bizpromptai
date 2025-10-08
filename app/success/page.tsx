'use client'

import { useEffect, useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'

interface PaymentStatus {
  session_id: string
  payment_status: string
  amount?: number
  currency?: string
  product_name?: string
}

function SuccessContent() {
  const searchParams = useSearchParams()
  const sessionId = searchParams.get('session_id')
  const [paymentStatus, setPaymentStatus] = useState<PaymentStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!sessionId) {
      setError('No payment session found')
      setLoading(false)
      return
    }

    checkPaymentStatus()
  }, [sessionId])

  const checkPaymentStatus = async () => {
    if (!sessionId) return

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/payments/status/${sessionId}`
      )

      if (!response.ok) {
        throw new Error('Failed to check payment status')
      }

      const data = await response.json()
      setPaymentStatus(data)

      // If payment is still processing, poll again
      if (data.payment_status === 'pending') {
        setTimeout(checkPaymentStatus, 2000) // Check again in 2 seconds
      } else {
        setLoading(false)
      }

    } catch (error) {
      console.error('Payment status check failed:', error)
      setError('Unable to verify payment status')
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-orange-50 flex items-center justify-center">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full mx-4 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Verifying Your Payment...
          </h2>
          <p className="text-gray-600">
            Please wait while we confirm your purchase
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-orange-50 flex items-center justify-center">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full mx-4 text-center">
          <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Payment Verification Error
          </h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <a 
            href="/"
            className="btn-primary inline-block"
          >
            Return Home
          </a>
        </div>
      </div>
    )
  }

  if (paymentStatus?.payment_status === 'paid') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-orange-50 flex items-center justify-center">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-lg w-full mx-4 text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            🎉 Payment Successful!
          </h1>
          
          <p className="text-gray-600 mb-6 text-lg">
            Thank you for your purchase! You now have lifetime access to all 47 AI business prompts.
          </p>
          
          <div className="bg-primary-50 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-gray-900 mb-2">What happens next?</h3>
            <ul className="text-left space-y-2 text-gray-700">
              <li className="flex items-start">
                <span className="text-primary-600 mr-2">1.</span>
                Check your email for access instructions
              </li>
              <li className="flex items-start">
                <span className="text-primary-600 mr-2">2.</span>
                Create your account to access the prompt library
              </li>
              <li className="flex items-start">
                <span className="text-primary-600 mr-2">3.</span>
                Start saving 12+ hours weekly with AI automation
              </li>
            </ul>
          </div>
          
          <div className="space-y-3">
            <a 
              href="/dashboard"
              className="btn-primary w-full block"
            >
              Access Your Prompts
            </a>
            
            <a 
              href="/"
              className="btn-secondary w-full block"
            >
              Return Home
            </a>
          </div>
          
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h4 className="font-medium text-gray-900 mb-2">Need Help?</h4>
            <p className="text-sm text-gray-600">
              Email us at{' '}
              <a href="mailto:support@bizpromptai.com" className="text-primary-600 hover:text-primary-700">
                support@bizpromptai.com
              </a>{' '}
              for any questions.
            </p>
          </div>
        </div>
      </div>
    )
  }

  // Payment failed or other status
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-orange-50 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full mx-4 text-center">
        <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z"></path>
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Payment Incomplete
        </h2>
        <p className="text-gray-600 mb-4">
          Your payment was not completed. You can try again or contact support if you need assistance.
        </p>
        <div className="space-y-3">
          <a 
            href="/"
            className="btn-primary w-full block"
          >
            Try Again
          </a>
          <a 
            href="mailto:support@bizpromptai.com"
            className="btn-secondary w-full block"
          >
            Contact Support
          </a>
        </div>
      </div>
    </div>
  )
}

export default function SuccessPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-orange-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    }>
      <SuccessContent />
    </Suspense>
  )
}