'use client'

const features = [
  {
    icon: '🎯',
    title: 'Marketing Automation',
    description: 'Email campaigns, social media content, and lead magnets that convert visitors into customers.',
    badge: 'Saves 25+ min per email'
  },
  {
    icon: '📊',
    title: 'Business Operations',
    description: 'SOPs, meeting agendas, project plans, and performance reviews automated.',
    badge: '3x faster planning'
  },
  {
    icon: '💰',
    title: 'Sales & Growth',
    description: 'Proposal templates, pitch decks, and customer onboarding sequences.',
    badge: 'Higher conversion rates'
  }
]

export function FeaturesSection() {
  return (
    <section className="py-20 bg-white/50">
      <div className="container mx-auto px-4 max-w-7xl">
        <h3 className="text-4xl font-bold text-center text-gray-900 mb-4">
          What You Get
        </h3>
        <p className="text-xl text-gray-600 text-center mb-16 max-w-2xl mx-auto">
          Transform your business operations with our comprehensive AI prompt library
        </p>
        
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div 
              key={index} 
              className="card hover:border-primary-200 group transition-all duration-300 hover:shadow-lg"
            >
              <div className="text-4xl mb-4 group-hover:scale-110 transition-transform duration-300">
                {feature.icon}
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-3 group-hover:text-primary-600 transition-colors">
                {feature.title}
              </h4>
              <p className="text-gray-600 mb-4 leading-relaxed">
                {feature.description}
              </p>
              <span className="badge">
                {feature.badge}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}