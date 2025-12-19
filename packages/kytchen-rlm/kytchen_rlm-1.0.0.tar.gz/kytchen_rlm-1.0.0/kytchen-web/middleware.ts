/**
 * Supabase middleware for Kytchen Cloud.
 *
 * Refreshes Supabase auth session cookies and redirects unauthenticated
 * dashboard requests to /login.
 */

import { updateSession } from "./lib/supabase/middleware"
import type { NextRequest } from "next/server"

export async function middleware(request: NextRequest) {
  return updateSession(request)
}

// Configure which routes use this middleware - only dashboard routes need auth
export const config = {
  matcher: ["/dashboard/:path*"],
}
