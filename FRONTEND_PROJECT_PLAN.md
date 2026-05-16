# 🎨 CAMPUSDEAL FRONTEND - COMPLETE PROJECT PLAN

## 🎯 PROJECT OVERVIEW

**Tech Stack:** Next.js 14 + TypeScript + Tailwind CSS + Shadcn/ui  
**Deployment:** Vercel (recommended) or Netlify  
**API:** https://campusdeal-backend.onrender.com  
**Timeline:** 2-3 hours for MVP, 1 week for full features

---

## 🏗️ ARCHITECTURE DECISION

### Why Next.js 14 (App Router)?
✅ Server-side rendering for SEO  
✅ Built-in API routes  
✅ Image optimization  
✅ Fast refresh  
✅ TypeScript support  
✅ Easy Vercel deployment  

### Why Shadcn/ui?
✅ Beautiful, accessible components  
✅ Customizable with Tailwind  
✅ Copy-paste, not npm install  
✅ Modern, clean design  
✅ Dark mode support  

### Why Tailwind CSS?
✅ Utility-first  
✅ Fast development  
✅ Consistent design  
✅ Small bundle size  
✅ Responsive by default  

---

## 📱 PAGES & FEATURES

### 1. **Authentication Pages**
- `/auth/register` - User registration with phone verification
- `/auth/login` - Login page
- `/auth/verify` - Phone verification
- `/auth/forgot-password` - Password reset

### 2. **Marketplace Pages**
- `/` - Homepage with featured listings
- `/marketplace` - Browse all listings (with filters)
- `/marketplace/[id]` - Single listing detail
- `/marketplace/create` - Create new listing
- `/marketplace/edit/[id]` - Edit listing

### 3. **User Pages**
- `/profile` - Current user profile
- `/profile/edit` - Edit profile
- `/profile/listings` - My listings
- `/profile/orders` - My orders (as buyer)
- `/profile/sales` - My sales (as seller)
- `/user/[id]` - Public user profile

### 4. **Wallet & Payments**
- `/wallet` - Wallet dashboard
- `/wallet/deposit` - Add funds
- `/wallet/withdraw` - Withdraw funds
- `/wallet/transactions` - Transaction history

### 5. **Orders**
- `/orders/[id]` - Order details
- `/checkout/[listingId]` - Checkout page

### 6. **Other**
- `/about` - About page
- `/contact` - Contact page
- `/terms` - Terms of service
- `/privacy` - Privacy policy

---

## 🎨 DESIGN SYSTEM

### Color Palette
```css
Primary: #10B981 (Green - Trust, Money, Growth)
Secondary: #3B82F6 (Blue - Professional)
Accent: #F59E0B (Amber - Attention, CTA)
Success: #10B981
Warning: #F59E0B
Error: #EF4444
Gray: #6B7280
Background: #F9FAFB
Dark: #111827
```

### Typography
- **Headings:** Inter (Bold, 600-800)
- **Body:** Inter (Regular, 400-500)
- **Monospace:** JetBrains Mono (for codes)

### Spacing
- Base: 4px (0.25rem)
- Scale: 4, 8, 12, 16, 24, 32, 48, 64, 96

### Border Radius
- Small: 4px
- Medium: 8px
- Large: 12px
- XL: 16px

---

## 🧩 COMPONENT LIBRARY

### Core Components (Shadcn/ui)
- Button
- Input
- Card
- Dialog (Modal)
- Dropdown Menu
- Form
- Label
- Select
- Textarea
- Toast (Notifications)
- Avatar
- Badge
- Tabs
- Accordion
- Alert
- Skeleton (Loading)

### Custom Components
- **ListingCard** - Display listing preview
- **UserAvatar** - User profile picture
- **PriceTag** - Formatted price display
- **CategoryBadge** - Category indicator
- **SearchBar** - Search with filters
- **Navbar** - Navigation header
- **Footer** - Site footer
- **WalletBalance** - Wallet display
- **OrderStatus** - Order status indicator
- **ImageUpload** - Image upload with preview
- **PhoneInput** - Phone number input with country code
- **VerificationCodeInput** - 6-digit code input

---

## 📂 PROJECT STRUCTURE

```
campusdeal-frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   ├── register/
│   │   ├── verify/
│   │   └── layout.tsx
│   ├── (marketplace)/
│   │   ├── page.tsx (homepage)
│   │   ├── marketplace/
│   │   ├── listing/[id]/
│   │   └── layout.tsx
│   ├── (dashboard)/
│   │   ├── profile/
│   │   ├── wallet/
│   │   ├── orders/
│   │   └── layout.tsx
│   ├── api/ (API routes if needed)
│   ├── layout.tsx (root layout)
│   └── globals.css
├── components/
│   ├── ui/ (shadcn components)
│   ├── layout/
│   │   ├── Navbar.tsx
│   │   ├── Footer.tsx
│   │   └── Sidebar.tsx
│   ├── marketplace/
│   │   ├── ListingCard.tsx
│   │   ├── ListingGrid.tsx
│   │   ├── FilterSidebar.tsx
│   │   └── SearchBar.tsx
│   ├── wallet/
│   │   ├── WalletBalance.tsx
│   │   ├── TransactionList.tsx
│   │   └── WithdrawForm.tsx
│   └── shared/
│       ├── ImageUpload.tsx
│       ├── PhoneInput.tsx
│       └── LoadingSpinner.tsx
├── lib/
│   ├── api.ts (API client)
│   ├── auth.ts (Auth helpers)
│   ├── utils.ts (Utilities)
│   └── constants.ts
├── hooks/
│   ├── useAuth.ts
│   ├── useListings.ts
│   ├── useWallet.ts
│   └── useOrders.ts
├── types/
│   ├── api.ts
│   ├── user.ts
│   ├── listing.ts
│   └── order.ts
├── public/
│   ├── images/
│   └── icons/
├── .env.local
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## 🚀 DEVELOPMENT PHASES

### Phase 1: Setup & Core (Day 1 - 4 hours)
- [x] Initialize Next.js project
- [ ] Install dependencies
- [ ] Setup Tailwind CSS
- [ ] Install Shadcn/ui
- [ ] Create design system
- [ ] Setup API client
- [ ] Create layout components

### Phase 2: Authentication (Day 2 - 4 hours)
- [ ] Login page
- [ ] Register page
- [ ] Phone verification
- [ ] Password reset
- [ ] Auth context/hooks
- [ ] Protected routes

### Phase 3: Marketplace (Day 3-4 - 8 hours)
- [ ] Homepage
- [ ] Listing grid
- [ ] Listing detail
- [ ] Create listing
- [ ] Edit listing
- [ ] Search & filters
- [ ] Categories

### Phase 4: User Dashboard (Day 5 - 4 hours)
- [ ] Profile page
- [ ] Edit profile
- [ ] My listings
- [ ] My orders
- [ ] My sales

### Phase 5: Wallet & Payments (Day 6 - 4 hours)
- [ ] Wallet dashboard
- [ ] Add funds
- [ ] Withdraw funds
- [ ] Transaction history
- [ ] Paystack integration

### Phase 6: Orders & Checkout (Day 7 - 4 hours)
- [ ] Checkout flow
- [ ] Order details
- [ ] Order status updates
- [ ] Reviews

### Phase 7: Polish & Deploy (Day 8 - 4 hours)
- [ ] Responsive design
- [ ] Loading states
- [ ] Error handling
- [ ] SEO optimization
- [ ] Deploy to Vercel

---

## 🎯 MVP FEATURES (Launch in 2-3 hours)

**Essential for testing API:**
1. ✅ Login/Register
2. ✅ Browse listings
3. ✅ View listing details
4. ✅ Create listing
5. ✅ Basic profile

**Can add later:**
- Wallet features
- Orders
- Reviews
- Advanced filters
- Chat

---

## 💻 TECH STACK DETAILS

### Dependencies
```json
{
  "dependencies": {
    "next": "14.2.0",
    "react": "18.3.0",
    "react-dom": "18.3.0",
    "typescript": "5.4.0",
    "tailwindcss": "3.4.0",
    "@radix-ui/react-*": "latest",
    "class-variance-authority": "latest",
    "clsx": "latest",
    "tailwind-merge": "latest",
    "lucide-react": "latest",
    "axios": "latest",
    "react-hook-form": "latest",
    "zod": "latest",
    "zustand": "latest",
    "date-fns": "latest"
  }
}
```

---

## 🎨 UI/UX PRINCIPLES

### 1. **Mobile-First**
- Design for mobile, scale up
- Touch-friendly targets (44px minimum)
- Responsive breakpoints

### 2. **Fast & Responsive**
- Optimistic UI updates
- Skeleton loaders
- Image lazy loading
- Instant feedback

### 3. **Accessible**
- ARIA labels
- Keyboard navigation
- Screen reader support
- Color contrast (WCAG AA)

### 4. **Intuitive**
- Clear CTAs
- Consistent patterns
- Helpful error messages
- Progress indicators

### 5. **Beautiful**
- Clean, modern design
- Smooth animations
- Consistent spacing
- Professional imagery

---

## 🔥 STANDOUT FEATURES

### 1. **Smart Search**
- Real-time search
- Filters (price, category, location)
- Sort options
- Search history

### 2. **Image Optimization**
- Next.js Image component
- Lazy loading
- Blur placeholders
- Multiple sizes

### 3. **Smooth Animations**
- Framer Motion
- Page transitions
- Micro-interactions
- Loading states

### 4. **Real-time Updates**
- Toast notifications
- Optimistic updates
- Auto-refresh

### 5. **Progressive Enhancement**
- Works without JS
- Offline support (future)
- Fast initial load

---

## 📊 PERFORMANCE TARGETS

- **First Contentful Paint:** < 1.5s
- **Time to Interactive:** < 3.5s
- **Lighthouse Score:** > 90
- **Bundle Size:** < 200KB (initial)

---

## 🚀 DEPLOYMENT

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Production
vercel --prod
```

### Environment Variables (Vercel)
```
NEXT_PUBLIC_API_URL=https://campusdeal-backend.onrender.com
NEXT_PUBLIC_PAYSTACK_PUBLIC_KEY=pk_live_xxx
```

---

## 📝 NEXT STEPS

1. **Create project structure**
2. **Setup development environment**
3. **Build MVP (2-3 hours)**
4. **Test with live API**
5. **Deploy to Vercel**
6. **Iterate based on feedback**

---

**Ready to start building?** 

I'll create:
1. Complete Next.js project structure
2. All components with beautiful UI
3. API integration
4. Responsive design
5. Ready to deploy

**Shall I proceed with creating the frontend?** 🚀
