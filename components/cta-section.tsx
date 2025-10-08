'use client'

interface CTASectionProps {
  onGetAccess: () => void
}

export function CTASection({ onGetAccess }: CTASectionProps) {
  return (
    <section className="py-20 bg-gradient-to-r from-primary-600 to-orange-500 text-white relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-black/10"></div>
      <div className="absolute top-0 left-0 w-full h-full">
        <div className="absolute top-10 left-10 w-20 h-20 bg-white/10 rounded-full"></div>
        <div className="absolute bottom-10 right-10 w-32 h-32 bg-white/5 rounded-full"></div>
        <div className="absolute top-1/2 left-1/4 w-16 h-16 bg-white/10 rounded-full"></div>
      </div>
      
      <div className="container mx-auto px-4 text-center relative z-10 max-w-4xl">
        <h3 className="text-4xl md:text-5xl font-bold mb-6 leading-tight">
          Ready to 10x Your Productivity?
        </h3>
        <p className="text-xl mb-8 opacity-90 leading-relaxed">
          Join 1,000+ entrepreneurs already automating their success with our AI prompts
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
          <button
            onClick={onGetAccess}
            className="bg-white text-primary-600 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            Get Full Access Now - $37
          </button>
          <span className="text-sm opacity-75 font-medium">
            Limited Time Offer
          </span>
        </div>
        
        <div className="flex justify-center items-center space-x-8 text-sm opacity-75">
          <div className="flex items-center">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
            </svg>
            Instant Access
          </div>
          <div className="flex items-center">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
            </svg>
            47 Premium Prompts
          </div>
          <div className="flex items-center">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
            </svg>
            Lifetime Updates
          </div>
        </div>
      </div>
    </section>
  )
}