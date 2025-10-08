'use client'

interface HeaderProps {
  onGetAccess: () => void
}

export function Header({ onGetAccess }: HeaderProps) {
  return (
    <header className="bg-white/80 backdrop-blur-sm border-b border-primary-200 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center max-w-7xl">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">BP</span>
          </div>
          <h1 className="text-2xl font-bold text-primary-600">BizPromptAI</h1>
        </div>
        <button
          onClick={onGetAccess}
          className="btn-primary"
        >
          Get Full Access
        </button>
      </div>
    </header>
  )
}