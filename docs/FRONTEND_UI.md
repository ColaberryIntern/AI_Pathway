# Frontend UI Documentation

**Author:** Karun Swaroop
**Last Updated:** February 2026

## Overview

The AI Pathway frontend is a modern, responsive React application built with TypeScript and Tailwind CSS. It features a clean light theme with smooth animations and an intuitive user experience.

## Design System

### Color Palette

```css
/* Primary Colors */
--color-primary: #6366f1;        /* Indigo-500 - Main actions */
--color-primary-light: #e0e7ff;  /* Indigo-100 - Backgrounds */

/* Background */
--color-bg: #f8fafc;             /* Slate-50 */
--color-surface: #ffffff;         /* White */

/* Text */
--color-text-primary: #0f172a;   /* Slate-900 */
--color-text-secondary: #475569; /* Slate-600 */
--color-text-muted: #94a3b8;     /* Slate-400 */

/* Status Colors */
--color-success: #22c55e;        /* Green-500 */
--color-info: #0ea5e9;           /* Sky-500 */
--color-warning: #f59e0b;        /* Amber-500 */
--color-error: #ef4444;          /* Red-500 */

/* Domain Layer Colors */
--color-foundation: #22c55e;     /* Green */
--color-theory: #6366f1;         /* Indigo */
--color-application: #0ea5e9;    /* Sky */
--color-tools: #10b981;          /* Emerald */
--color-tech-prereq: #f59e0b;    /* Amber */
--color-domain: #ec4899;         /* Pink */
--color-soft: #8b5cf6;           /* Purple */
```

### Typography

- **Font Family:** Inter, system-ui, sans-serif
- **Headings:** font-bold, tracking-tight
- **Body:** font-normal, line-height 1.5

### Spacing Scale

Following Tailwind's default spacing scale (4px base unit):
- `space-1`: 4px
- `space-2`: 8px
- `space-4`: 16px
- `space-6`: 24px
- `space-8`: 32px

## Pages

### 1. HomePage (`/`)

The landing page introduces users to the AI Pathway tool.

**Sections:**
- Hero with gradient background and CTA
- "How It Works" - 4-step process cards
- Features grid
- Final CTA section

**Key Components:**
```tsx
<section className="relative py-20 overflow-hidden">
  <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 via-white to-sky-50" />
  <h1 className="text-5xl font-bold">
    <span className="gradient-text">Your Personalized Path to AI Fluency</span>
  </h1>
</section>
```

### 2. ProfileSelectionPage (`/profiles`)

Single-page layout for profile creation and selection.

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│                 Choose Your Starting Point                   │
│                                                             │
│  [Custom Profile]  [Example Profiles ↓]  ← anchor buttons   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  CUSTOM PROFILE FORM                                │   │
│  │  - Name, Current Role, Target Role                  │   │
│  │  - Industry, Experience, AI Exposure                │   │
│  │  - Learning Intent, Target JD                       │   │
│  │                                                     │   │
│  │  [Continue to Analysis →]                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ─────────────────── OR ───────────────────                 │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  EXAMPLE PROFILES (id="example-profiles")           │   │
│  │                                                     │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │ Profile 1  │  │ Profile 2  │  │ Profile 3  │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘    │   │
│  │       ... 12 profiles in 2-column grid ...          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Smooth scroll navigation between sections
- Form validation with disabled submit until JD provided
- Profile cards with hover effects
- Floating continue button when example profile selected

### 3. AnalysisPage (`/analysis/:profileId`)

Real-time visualization of the AI analysis process.

**States:**

1. **Input State** - Define target (edit JD, review profile)
2. **Analyzing State** - Domain grid with animated cards
3. **Complete State** - Summary with skill gaps
4. **Error State** - Retry option

**Domain Grid Animation:**

```
┌──────────┐ ┌──────────┐ ┌══════════╗ ┌──────────┐
│  dimmed  │ │ complete │ ║  ACTIVE  ║ │  dimmed  │
│  (gray)  │ │ (green)  │ ║ (sky+glow)║ │  (gray)  │
│  40%     │ │ ✓ Done   │ ║ Scanning ║ │  40%     │
└──────────┘ └──────────┘ ╚══════════╝ └──────────┘
```

**Card States:**

| State | Visual Treatment |
|-------|------------------|
| `dimmed` | 40% opacity, gray background, gray border |
| `active` | Sky gradient, glow animation, "Scanning..." badge, scale 1.03x |
| `complete` | Green background, "✓ Analyzed" badge, flash animation |
| `selected` | Indigo gradient, "Chapter X" badge, scale 1.02x |

### 4. LearningPathPage (`/path/:pathId`)

Interactive learning content with expandable chapters.

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Path Title                                      [0%] Done  │
│  Description text...                                        │
│  ▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  Progress Bar        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  ○ Chapter 1 │ Skill Name                         2.5h  ▼  │
├─────────────────────────────────────────────────────────────┤
│  Skill Level: L0 → L1                                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Learning Objectives                                │   │
│  │  ✓ Objective 1                                      │   │
│  │  ✓ Objective 2                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Core Concepts                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Concept Title                                      │   │
│  │  Description...                                     │   │
│  │  Examples: ...                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Exercises                                                  │
│  ┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐   │
│  ╎  hands-on: Exercise Title               ~30 min    ╎   │
│  ╎  1. Step one                                       ╎   │
│  ╎  2. Step two                                       ╎   │
│  └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘   │
│                                                             │
│  Resources                                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  📚 Resource Title                    type • source │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  [Mark as Complete]                                         │
└─────────────────────────────────────────────────────────────┘
```

### 5. DashboardPage (`/dashboard/:pathId`)

Progress tracking and path management.

**Features:**
- Stats cards with colored borders
- Path progress visualization
- Empty state with CTA

## Components

### DomainCard

The core visualization component for the analysis grid.

```tsx
interface DomainCardProps {
  domain: Domain;
  state: 'dimmed' | 'active' | 'complete' | 'selected';
  chapterNum?: number;
}
```

**State Transitions:**

```
dimmed ──▶ active ──▶ complete ──▶ selected
   │                      │
   └──────────────────────┘ (can skip states)
```

**Animations:**

1. **Active State** (`animate-active-glow`)
   ```css
   @keyframes active-glow {
     0%, 100% {
       box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.3),
                   0 0 20px rgba(14, 165, 233, 0.2);
     }
     50% {
       box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.4),
                   0 0 30px rgba(14, 165, 233, 0.4);
     }
   }
   ```

2. **Complete Flash** (`animate-complete-flash`)
   ```css
   @keyframes complete-flash {
     0% { background-color: rgba(34, 197, 94, 0.3); }
     50% { box-shadow: 0 0 20px rgba(34, 197, 94, 0.4); }
     100% { background-color: rgba(240, 253, 244, 1); }
   }
   ```

3. **Checkmark Draw** (`animate-check-draw`)
   ```css
   @keyframes check-draw {
     0% { stroke-dashoffset: 20; }
     100% { stroke-dashoffset: 0; }
   }
   ```

### DomainGrid

Container for the 18 domain cards with legend.

```tsx
interface DomainGridProps {
  highlightedDomains: string[];
  activeDomain: string | null;
  completedDomains: string[];
  selectedDomains?: { domainId: string; chapterNum: number }[];
}
```

**Responsive Grid:**
- Large (lg): 6 columns
- Medium (sm): 3 columns
- Small: 2 columns

### AnalysisProgress

Step indicator for the analysis pipeline.

```tsx
const steps = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'jd', label: 'JD Parse', icon: FileText },
  { id: 'gaps', label: 'Gap Analysis', icon: BarChart3 },
  { id: 'path', label: 'Learning Path', icon: BookOpen },
];
```

## State Management

### React Query Setup

```tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,  // 5 minutes
      retry: 2,
    },
  },
});
```

### Key Queries

| Query Key | Endpoint | Cache Time |
|-----------|----------|------------|
| `['profiles']` | GET /api/profiles | 10 min |
| `['profile', id]` | GET /api/profiles/{id} | 5 min |
| `['path', id]` | GET /api/paths/{id} | 5 min |
| `['progress', id]` | GET /api/progress/{id} | 1 min |

## Styling Guidelines

### Tailwind Classes

**Buttons:**
```tsx
// Primary
className="btn btn-primary"
// → px-4 py-2 rounded-lg bg-primary-600 text-white hover:bg-primary-700

// Secondary
className="btn btn-secondary"
// → px-4 py-2 rounded-lg bg-gray-200 text-gray-800 hover:bg-gray-300
```

**Cards:**
```tsx
className="card"
// → bg-white rounded-xl shadow-sm border border-gray-100 p-6

className="card card-hover"
// → ... + hover:shadow-lg hover:-translate-y-0.5 transition-all
```

**Inputs:**
```tsx
className="input"
// → w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500
```

### Gradient Text

```tsx
className="gradient-text"
// → bg-gradient-to-r from-indigo-600 to-sky-600 bg-clip-text text-transparent
```

## Accessibility

- All interactive elements have focus states
- Color contrast meets WCAG AA standards
- Semantic HTML structure
- ARIA labels on icon-only buttons
- Keyboard navigation support

## Performance

### Optimizations

1. **Code Splitting**
   ```tsx
   const LearningPathPage = lazy(() => import('./pages/LearningPathPage'));
   ```

2. **Image Optimization**
   - SVG icons from Lucide React
   - Lazy loading for off-screen content

3. **CSS**
   - Tailwind purges unused styles
   - CSS animations hardware-accelerated

### Bundle Size

| Chunk | Size (gzip) |
|-------|-------------|
| Main | ~80 KB |
| Vendor (React) | ~45 KB |
| TanStack Query | ~12 KB |

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Future Improvements

1. **Dark Mode** - Theme toggle with system preference detection
2. **Animations** - Framer Motion for page transitions
3. **PWA** - Offline support and installability
4. **i18n** - Multi-language support
