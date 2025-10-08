'use client'

const categories = [
  {
    title: 'Marketing Prompts',
    description: 'Access your marketing automation prompts for emails, social media, and campaigns',
    count: '15 prompts',
    color: 'bg-blue-500',
    icon: '📧'
  },
  {
    title: 'Operations',
    description: 'Streamline your business operations with SOPs and process automation',
    count: '16 prompts', 
    color: 'bg-green-500',
    icon: '⚙️'
  },
  {
    title: 'Sales & Growth',
    description: 'Accelerate your sales process with proposals and pitch templates',
    count: '16 prompts',
    color: 'bg-purple-500',
    icon: '📈'
  }
]

export function PromptCategories() {
  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
      {categories.map((category, index) => (
        <div key={index} className="card group hover:border-primary-200 cursor-pointer">
          <div className="flex items-start justify-between mb-4">
            <div className={`w-12 h-12 ${category.color} rounded-xl flex items-center justify-center text-white text-xl group-hover:scale-110 transition-transform duration-200`}>
              {category.icon}
            </div>
            <span className="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
              {category.count}
            </span>
          </div>
          
          <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
            {category.title}
          </h3>
          <p className="text-gray-600 text-sm mb-4 leading-relaxed">
            {category.description}
          </p>
          
          <button className="btn-secondary w-full text-sm group-hover:bg-primary-50 group-hover:border-primary-300 transition-colors">
            View Prompts
          </button>
        </div>
      ))}
    </div>
  )
}