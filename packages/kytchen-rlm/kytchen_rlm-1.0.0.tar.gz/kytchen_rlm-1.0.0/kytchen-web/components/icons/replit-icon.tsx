/**
 * Replit brand icon component.
 */

import { SVGProps } from "react"

export function ReplitIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="currentColor"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16z" />
      <path d="M12 6a6 6 0 0 0-6 6h2a4 4 0 0 1 4-4V6z" />
      <path d="M12 18a6 6 0 0 0 6-6h-2a4 4 0 0 1-4 4v2z" />
    </svg>
  )
}
