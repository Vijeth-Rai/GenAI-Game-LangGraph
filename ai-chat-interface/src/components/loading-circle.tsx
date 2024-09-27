'use client'

import { useEffect, useState } from 'react'

type LoadingCircleProps = {
  state: string
}

export function LoadingCircleComponent({ state }: LoadingCircleProps) {
  const [rotation, setRotation] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setRotation((prevRotation) => (prevRotation + 5) % 360)
    }, 20)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex items-center space-x-2">
      <div className="relative w-5 h-5">
        <div
          className="absolute inset-0 border-2 border-gray-600 rounded-full opacity-25"
          style={{
            transform: `rotate(${rotation}deg)`,
            borderRightColor: 'transparent',
            borderBottomColor: 'transparent',
          }}
        />
        <div
          className="absolute inset-0 border-2 border-gray-400 rounded-full opacity-75"
          style={{
            transform: `rotate(${(rotation + 180) % 360}deg)`,
            borderRightColor: 'transparent',
            borderBottomColor: 'transparent',
          }}
        />
      </div>
      <span className="text-gray-400 text-xs whitespace-nowrap">{state}</span>
    </div>
  )
}