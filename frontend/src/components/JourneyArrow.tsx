import { ArrowRight, MoveRight } from 'lucide-react'

interface JourneyArrowProps {
  variant?: 'horizontal' | 'vertical' | 'icon'
  size?: 'sm' | 'md' | 'lg'
}

export default function JourneyArrow({ variant = 'horizontal', size = 'md' }: JourneyArrowProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6',
  }

  if (variant === 'icon') {
    return <ArrowRight className={`${sizeClasses[size]} text-primary-500`} />
  }

  if (variant === 'vertical') {
    return (
      <div className="flex flex-col items-center py-4">
        <div className="w-0.5 h-8 bg-gradient-to-b from-gray-300 to-primary-400" />
        <div className="w-3 h-3 border-r-2 border-b-2 border-primary-400 transform rotate-45 -mt-1.5" />
      </div>
    )
  }

  // horizontal variant
  return (
    <div className="flex items-center justify-center px-4">
      <div className="flex items-center gap-1">
        <div className="h-0.5 w-8 bg-gradient-to-r from-gray-300 to-primary-400" />
        <MoveRight className={`${sizeClasses[size]} text-primary-500`} />
      </div>
    </div>
  )
}
