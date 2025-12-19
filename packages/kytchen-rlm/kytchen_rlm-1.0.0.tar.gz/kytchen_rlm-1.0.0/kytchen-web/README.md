# Kytchen Web

This is the web frontend for Kytchen, built with Next.js. It provides the dashboard, billing, and user management interface.

## Development

First, install dependencies:

```bash
npm install
```

Then, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Environment Variables

Create a `.env.local` file in the `kytchen-web` directory with the following variables:

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# Stripe (for billing)
STRIPE_SECRET_KEY=sk_test_... or sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_CHEF=price_...
STRIPE_PRICE_SOUSCHEF=price_...

# App Configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000
NODE_ENV=development

# Optional: NextAuth (if using)
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key
```

## Building for Production

```bash
npm run build
npm start
```

## Deployment on Vercel

This project is configured to deploy on [Vercel](https://vercel.com).

### Quick Deploy

1. **Create a new project** on Vercel
2. **Connect your GitHub repository**
3. **Configure the project:**
   - **Framework Preset**: Next.js
   - **Root Directory**: `kytchen-web`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`

### Environment Variables

Add these environment variables in the Vercel dashboard (Settings → Environment Variables):

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_CHEF=price_...
STRIPE_PRICE_SOUSCHEF=price_...

# App Configuration
NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
NODE_ENV=production

# Optional: NextAuth
NEXTAUTH_URL=https://your-app.vercel.app
NEXTAUTH_SECRET=your-secret-key
```

### Custom Domain

Since you purchased your domain through Vercel:
1. Go to your project settings
2. Navigate to **Domains**
3. Add your custom domain
4. Follow the DNS configuration steps provided

## Architecture

- **Frontend**: Next.js 16 with TypeScript and Tailwind CSS
- **Authentication**: Supabase Auth
- **Billing**: Stripe integration
- **Styling**: shadcn/ui components

## Project Structure

```
kytchen-web/
├── app/                    # Next.js App Router
│   ├── api/               # API routes (billing, etc.)
│   ├── (auth)/            # Authentication pages
│   ├── (marketing)/       # Marketing pages
│   ├── dashboard/         # Main dashboard
│   └── docs/              # Documentation pages
├── components/            # React components
├── lib/                   # Utilities and configs
│   ├── supabase/         # Supabase client setup
│   ├── auth.ts           # Auth configuration
│   └── api/              # API client
├── public/                # Static assets
└── packages/             # Internal packages
    └── client/           # TypeScript SDK
```

## Related

- [Backend API](../kytchen) - Python backend
- [SDK](../kytchen-sdk) - TypeScript SDK
- [Documentation](https://kytchen.dev/docs)

## License

MIT