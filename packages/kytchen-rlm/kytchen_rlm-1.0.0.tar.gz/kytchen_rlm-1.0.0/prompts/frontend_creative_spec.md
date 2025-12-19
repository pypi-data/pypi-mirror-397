# Kytchen Frontend Creative Spec

**Role**: Lead Frontend Architect (Creative Coding Specialist)
**Context**: Building 'Kytchen' (v1.0) - The Industrial Infrastructure for AI Agents.
**Stack**: Next.js 15 (App Router), Tailwind CSS, Framer Motion, R3F (React Three Fiber).

---

## OBJECTIVE

Make the user experience feel **TACTILE**, **MECHANICAL**, and **HOT**.

We don't want "smooth SaaS." We want **"Industrial Kitchen."**

---

## 1. THE "HEAT" (Visual Effects)

**Goal:** Visualize the "work" being done in the pantry/oven.

### Shader Effect (The Stove)

* Implement a subtle **Heat Haze / Distortion Shader** using `@react-three/fiber` and `@react-three/drei`.
* **Where:** Overlay this on the "Active Run" card when the Agent is "Cooking" (executing tools).
* **Effect:** A slight, waving displacement map that blurs the text behind it, simulating hot air rising off a grill.

```tsx
// components/effects/HeatDistortion.tsx
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'

export function HeatDistortion({ intensity = 0.02 }) {
  const meshRef = useRef()

  useFrame(({ clock }) => {
    // Animate displacement based on time
    meshRef.current.material.uniforms.uTime.value = clock.elapsedTime
  })

  return (
    <mesh ref={meshRef}>
      {/* Custom shader material with heat distortion */}
    </mesh>
  )
}
```

### Steam/Smoke Particles

* Use a lightweight particle system (Canvas API) for the "Footer" or "Loading States."
* **Vibe:** Minimal white steam rising and dissipating against the dark navy background.
* Keep it subtle - 10-20 particles max, slow rise, quick fade.

---

## 2. THE "RECEIPT" (Streaming UI)

**Goal:** Turn standard logs into a physical artifact.

### The Component: `<ThermalReceipt />`

#### CSS Tech

**Jagged Edge:**
```css
.receipt-edge {
  clip-path: polygon(
    0% 0%, 100% 0%,
    100% calc(100% - 8px),
    96% 100%, 92% calc(100% - 8px),
    88% 100%, 84% calc(100% - 8px),
    80% 100%, 76% calc(100% - 8px),
    72% 100%, 68% calc(100% - 8px),
    64% 100%, 60% calc(100% - 8px),
    56% 100%, 52% calc(100% - 8px),
    48% 100%, 44% calc(100% - 8px),
    40% 100%, 36% calc(100% - 8px),
    32% 100%, 28% calc(100% - 8px),
    24% 100%, 20% calc(100% - 8px),
    16% 100%, 12% calc(100% - 8px),
    8% 100%, 4% calc(100% - 8px),
    0% 100%
  );
}
```

**Texture:**
```css
.thermal-paper {
  background-color: #FDFBF7;
  background-image: url('/textures/noise.png');
  background-blend-mode: multiply;
  opacity: 0.95;
}
```

**Typography:**
```css
.receipt-text {
  font-family: 'VT323', 'Share Tech Mono', monospace;
  letter-spacing: -0.5px;
  color: #1a1a1a;
  /* Simulate ink bleed */
  text-shadow: 0 0 0.5px rgba(0,0,0,0.3);
}
```

#### Animation (Framer Motion)

```tsx
// components/ui/ThermalReceipt.tsx
import { motion, AnimatePresence } from 'framer-motion'

export function ThermalReceipt({ logs }) {
  return (
    <motion.div
      className="receipt-container"
      layout
    >
      <AnimatePresence>
        {logs.map((log, i) => (
          <motion.div
            key={log.id}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            transition={{
              type: 'spring',
              stiffness: 500,
              damping: 30
            }}
            className="receipt-line"
          >
            <span className="timestamp">{log.time}</span>
            <span className="content">{log.message}</span>
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Jagged bottom edge */}
      <div className="receipt-edge" />
    </motion.div>
  )
}
```

---

## 3. THE "TICKET RAIL" (Navigation)

**Goal:** Make switching contexts feel like sliding orders.

### View Transitions API

Enable in `next.config.js`:
```js
module.exports = {
  experimental: {
    viewTransitions: true,
  },
}
```

**Action:** When clicking a run in the sidebar, the card should **slide** from the sidebar to the center stage using a shared `view-transition-name`.

```css
/* Sidebar run card */
.run-card-sidebar {
  view-transition-name: run-card;
}

/* Main stage run card */
.run-card-main {
  view-transition-name: run-card;
}
```

### Layout Animations (Blue Tape Tab Indicator)

```tsx
// components/nav/TabNav.tsx
import { motion } from 'framer-motion'

export function TabNav({ tabs, activeTab }) {
  return (
    <nav className="relative flex gap-4">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          className="relative px-4 py-2 z-10"
          onClick={() => setActive(tab.id)}
        >
          {tab.label}

          {activeTab === tab.id && (
            <motion.div
              layoutId="blue-tape"
              className="absolute inset-0 bg-blue-600 -z-10"
              style={{ borderRadius: 4 }}
              transition={{ type: 'spring', stiffness: 500, damping: 30 }}
            />
          )}
        </button>
      ))}
    </nav>
  )
}
```

---

## 4. THE "SOUNDSCAPES" (Audio UI)

**Goal:** Subconscious feedback.

### Library: `use-sound`

```bash
npm install use-sound
```

### Sound Hooks

```tsx
// hooks/useKytchenSounds.ts
import useSound from 'use-sound'

export function useKytchenSounds() {
  const [playClack] = useSound('/sounds/clack.mp3', { volume: 0.3 })
  const [playZip] = useSound('/sounds/print.mp3', { volume: 0.2 })
  const [playDing] = useSound('/sounds/ding.mp3', { volume: 0.2 })

  return {
    // Mechanical keyboard click - primary CTAs
    clack: playClack,

    // Thermal printer - receipt finishes printing
    zip: playZip,

    // Order up bell - job completes
    ding: playDing,
  }
}
```

### Usage

```tsx
function FireButton() {
  const { clack } = useKytchenSounds()

  return (
    <button
      onClick={() => {
        clack()
        fireTicket()
      }}
    >
      FIRE
    </button>
  )
}
```

### Sound Files Needed

| File | Sound | When |
|------|-------|------|
| `clack.mp3` | Mechanical keyboard switch | Primary CTA clicks |
| `print.mp3` | Thermal printer zip | Receipt finishes |
| `ding.mp3` | Order up bell | Job completes |

**Constraint:** Low volume (0.2), optional toggle in settings.

---

## 5. THE "MIS-EN-PLACE" (Drag & Drop)

**Goal:** Make file management feel physical.

### Library: `@dnd-kit`

```bash
npm install @dnd-kit/core @dnd-kit/sortable
```

### The Pantry Grid + Context Bowl

```tsx
// components/pantry/PantryGrid.tsx
import { DndContext, useDraggable, useDroppable } from '@dnd-kit/core'
import { useSpring, animated } from '@react-spring/web'

function ContextBowl({ children, isOver }) {
  const style = useSpring({
    transform: isOver
      ? 'scale(1.05) translateY(4px)'
      : 'scale(1) translateY(0px)',
    config: { tension: 300, friction: 20 }
  })

  return (
    <animated.div
      style={style}
      className="context-bowl border-4 border-dashed border-slate-400 rounded-full p-8"
    >
      {children}
      {isOver && (
        <div className="text-center text-slate-500">
          Drop to add ingredient
        </div>
      )}
    </animated.div>
  )
}

function DatasetCard({ dataset }) {
  const { attributes, listeners, setNodeRef, transform } = useDraggable({
    id: dataset.id,
  })

  return (
    <div
      ref={setNodeRef}
      {...listeners}
      {...attributes}
      className="dataset-card cursor-grab active:cursor-grabbing"
    >
      <span className="font-mono">{dataset.name}</span>
      <span className="text-xs text-slate-500">{dataset.size}</span>
    </div>
  )
}
```

---

## 6. EXECUTION CHECKLIST

### Dependencies to Add

```bash
# 3D / Shaders
npm install @react-three/fiber @react-three/drei three
npm install glsl-random glsl-noise

# Animation
npm install framer-motion @react-spring/web

# Drag & Drop
npm install @dnd-kit/core @dnd-kit/sortable

# Sound
npm install use-sound
```

### Files to Create

```
kytchen-web/
├── public/
│   ├── sounds/
│   │   ├── clack.mp3
│   │   ├── print.mp3
│   │   └── ding.mp3
│   └── textures/
│       └── noise.png
│
├── components/
│   ├── effects/
│   │   ├── HeatDistortion.tsx
│   │   └── SteamParticles.tsx
│   ├── ui/
│   │   └── ThermalReceipt.tsx
│   ├── nav/
│   │   └── TabNav.tsx
│   └── pantry/
│       └── PantryGrid.tsx
│
└── hooks/
    └── useKytchenSounds.ts
```

### Refactoring Tasks

1. [ ] Refactor `RunLogs.tsx` to use `<ThermalReceipt />` style
2. [ ] Add heat distortion overlay to active run cards
3. [ ] Implement blue tape tab indicator
4. [ ] Add sound effects to CTAs
5. [ ] Make pantry grid draggable

---

## 7. VISUAL REFERENCE

### Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| Thermal Paper | `#FDFBF7` | Receipt background |
| Ink Black | `#1a1a1a` | Receipt text |
| Blue Tape | `#2563eb` | Active tab indicator |
| Navy | `#0f172a` | Main background |
| Steam White | `#ffffff` @ 20% | Particle effects |

### Typography

| Context | Font | Weight |
|---------|------|--------|
| Receipt logs | VT323 / Share Tech Mono | 400 |
| Headers | System UI (bold) | 700 |
| Body | System UI | 400 |
| Code | JetBrains Mono | 400 |

---

## 8. PERFORMANCE NOTES

- **Heat shader:** Only render when card is in viewport
- **Particles:** Cap at 20, use object pooling
- **Sounds:** Preload on mount, not on click
- **View Transitions:** Fallback gracefully on unsupported browsers
- **3D elements:** Use `<Suspense>` with loading states

---

*Creative spec for Kytchen v1.0 - Industrial Kitchen UI*
