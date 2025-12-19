"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  life: number
  maxLife: number
  size: number
  opacity: number
}

interface SteamParticlesProps {
  active?: boolean
  maxParticles?: number
  emitRate?: number // particles per second
  className?: string
}

export function SteamParticles({
  active = true,
  maxParticles = 15,
  emitRate = 3,
  className
}: SteamParticlesProps) {
  const canvasRef = React.useRef<HTMLCanvasElement>(null)
  const particlesRef = React.useRef<Particle[]>([])
  const animationRef = React.useRef<number | undefined>(undefined)
  const lastEmitRef = React.useRef(0)
  const lastFrameRef = React.useRef(0)

  React.useEffect(() => {
    if (!active) return

    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Handle resize
    const resize = () => {
      const rect = canvas.getBoundingClientRect()
      const dpr = Math.min(window.devicePixelRatio, 2)
      canvas.width = rect.width * dpr
      canvas.height = rect.height * dpr
      ctx.scale(dpr, dpr)
    }
    resize()
    window.addEventListener("resize", resize)

    // Initialize particle pool
    particlesRef.current = []

    const emitParticle = () => {
      if (particlesRef.current.length >= maxParticles) return

      const rect = canvas.getBoundingClientRect()
      particlesRef.current.push({
        x: rect.width * (0.3 + Math.random() * 0.4), // Emit from middle 40%
        y: rect.height, // Start at bottom
        vx: (Math.random() - 0.5) * 0.3,
        vy: -0.8 - Math.random() * 0.4, // Rise upward
        life: 0,
        maxLife: 2.5 + Math.random() * 1.5, // 2.5-4 seconds
        size: 6 + Math.random() * 10,
        opacity: 0.2 + Math.random() * 0.2
      })
    }

    const animate = (timestamp: number) => {
      const rect = canvas.getBoundingClientRect()
      ctx.clearRect(0, 0, rect.width, rect.height)

      // Calculate delta time
      const dt = lastFrameRef.current ? (timestamp - lastFrameRef.current) / 1000 : 1 / 60
      lastFrameRef.current = timestamp

      // Emit new particles
      const emitInterval = 1000 / emitRate
      if (timestamp - lastEmitRef.current > emitInterval) {
        emitParticle()
        lastEmitRef.current = timestamp
      }

      // Update and draw particles
      particlesRef.current = particlesRef.current.filter(p => {
        p.life += dt
        if (p.life >= p.maxLife) return false

        // Update position
        p.x += p.vx
        p.y += p.vy

        // Add slight wobble
        p.vx += (Math.random() - 0.5) * 0.05

        // Slow down as it rises
        p.vy *= 0.995

        // Calculate opacity based on life (fade in then out)
        const lifeRatio = p.life / p.maxLife
        let alpha = p.opacity
        if (lifeRatio < 0.15) {
          alpha *= lifeRatio / 0.15 // Fade in
        } else if (lifeRatio > 0.6) {
          alpha *= 1 - (lifeRatio - 0.6) / 0.4 // Fade out
        }

        // Calculate size (grow slightly as it rises)
        const currentSize = p.size * (1 + lifeRatio * 0.5)

        // Draw particle (soft circle with gradient)
        const gradient = ctx.createRadialGradient(
          p.x, p.y, 0,
          p.x, p.y, currentSize
        )
        gradient.addColorStop(0, `rgba(255, 255, 255, ${alpha})`)
        gradient.addColorStop(0.4, `rgba(220, 220, 220, ${alpha * 0.6})`)
        gradient.addColorStop(0.7, `rgba(200, 200, 200, ${alpha * 0.3})`)
        gradient.addColorStop(1, "rgba(180, 180, 180, 0)")

        ctx.beginPath()
        ctx.arc(p.x, p.y, currentSize, 0, Math.PI * 2)
        ctx.fillStyle = gradient
        ctx.fill()

        return true
      })

      animationRef.current = requestAnimationFrame(animate)
    }

    animationRef.current = requestAnimationFrame(animate)

    return () => {
      window.removeEventListener("resize", resize)
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [active, maxParticles, emitRate])

  if (!active) return null

  return (
    <canvas
      ref={canvasRef}
      className={cn("absolute inset-0 pointer-events-none", className)}
      style={{ mixBlendMode: "screen" }}
    />
  )
}
