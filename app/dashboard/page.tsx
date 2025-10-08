'use client'

import { useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import { DashboardHeader } from '@/components/dashboard-header'
import { PromptCategories } from '@/components/prompt-categories'
import { AccountInfo } from '@/components/account-info'

export default function DashboardPage() {
  const { user, loading } = useAuth()

  useEffect(() => {
    if (!loading && !user) {
      window.location.href = '/'
    }
  }, [user, loading])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardHeader user={user} />
      
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user.name}!
          </h1>
          <p className="text-gray-600">
            Access your complete library of AI business prompts
          </p>
        </div>

        <PromptCategories />
        <AccountInfo user={user} />
      </main>
    </div>
  )
}