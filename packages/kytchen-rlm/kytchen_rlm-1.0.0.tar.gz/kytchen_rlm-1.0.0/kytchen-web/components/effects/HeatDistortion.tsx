"use client"

import * as React from "react"
import dynamic from "next/dynamic"
import { cn } from "@/lib/utils"

// Lazy load Three.js to minimize bundle impact
const HeatDistortionCanvas = dynamic(
  () => import("./HeatDistortionCanvas"),
  { ssr: false, loading: () => null }
)

interface HeatDistortionProps {
  active: boolean
  intensity?: number // 0.0 - 1.0
  className?: string
}

export function HeatDistortion({
  active,
  intensity = 0.5,
  className
}: HeatDistortionProps) {
  if (!active) return null

  return (
    <div
      className={cn(
        "absolute inset-0 pointer-events-none z-10 overflow-hidden",
        className
      )}
    >
      <HeatDistortionCanvas intensity={intensity} />
    </div>
  )
}
