# GO-DOJO Design Guidelines

## Design Approach
**Reference-Based + Design System Hybrid**: Drawing from educational platforms like Stepik/Metanit for content structure, combined with Shadcn UI components, all wrapped in a cohesive samurai/Japanese aesthetic. The design balances utility (learning platform) with cultural theming for memorable brand identity.

## Core Design Principles
1. **Samurai Discipline**: Clean, purposeful layouts with breathing room - nothing excessive
2. **Dojo Atmosphere**: Structured learning paths with clear progression
3. **Cultural Authenticity**: Subtle Japanese design elements without stereotypical overuse
4. **Focus & Flow**: Minimize distractions during learning, emphasize content hierarchy

---

## Typography

**Font Families:**
- Primary: Noto Sans JP (for Japanese characters in logo and accents) via Google Fonts
- Body/UI: Inter or system font stack for optimal readability
- Code: JetBrains Mono for code snippets

**Hierarchy:**
- Page Titles: text-4xl to text-5xl, font-bold
- Section Headers: text-2xl to text-3xl, font-semibold  
- Lesson Titles: text-xl, font-medium
- Body Text: text-base, leading-relaxed for comfortable reading
- UI Elements: text-sm to text-base
- Code Snippets: text-sm, monospace

---

## Layout System

**Spacing Units**: Use Tailwind spacing primitives: **2, 4, 6, 8, 12, 16, 20, 24**
- Tight spacing: p-2, gap-4
- Standard spacing: p-6, gap-8, my-12
- Section spacing: py-16, py-20

**Container Structure:**
- Maximum width: max-w-7xl for content areas
- Reading content: max-w-4xl for lesson text
- Sidebar navigation: w-64 to w-80

---

## Component Library

### Header
- Full-width fixed header with backdrop blur
- Left: Logo "GO-DOJO | Go 道場" (Japanese character integrated naturally)
- Right: Theme toggle icon + Language dropdown (RU/EN flags or text)
- Height: h-16
- Border bottom for subtle separation

### Navigation/Sidebar (Lessons)
- Sticky sidebar at w-64 or w-72
- Topic sections as collapsible accordions
- Lesson items as rectangular cards showing:
  - Number + Title (e.g., "2. Мьютексы")
  - Completion indicator (subtle checkmark or progress bar)
  - Active state with accent highlight
- Smooth expand/collapse animations
- Scrollable with fixed header

### Content Area (Lessons)
- Main content with generous padding (px-8 to px-12, py-12)
- Text formatted with rich styles:
  - Headings with clear hierarchy
  - Bold, underline, color highlights
  - Embedded images with captions
  - Hyperlinks with subtle underline
  - Code blocks with syntax highlighting background
- Next/Previous lesson navigation at bottom

### Topic Cards (Main Page)
- Grid layout: grid-cols-1 md:grid-cols-2 lg:grid-cols-3
- Each card shows:
  - Topic icon or Japanese calligraphy accent
  - Topic title (text-xl, font-semibold)
  - Brief description
  - Lesson count
  - Progress indicator if applicable
- Hover state with subtle lift or border glow

### Admin Panel
- Clean dashboard layout
- Left sidebar: Navigation (Topics, Lessons, Create New)
- Main area: 
  - Table view of existing topics/lessons
  - Rich text editor with toolbar for:
    - Text formatting (bold, italic, underline, color picker)
    - Image upload with preview
    - Link insertion
    - Heading levels
  - Save/Cancel actions prominently placed
- Use Tiptap or similar ready-made rich editor library

### Onboarding/Landing Page
**Structure (5-7 sections):**

1. **Hero Section** (h-screen or min-h-[600px]):
   - Large centered headline about go-dojo philosophy
   - Subheadline about unique approach
   - Primary CTA button to start learning
   - Background: Subtle Japanese pattern or abstract geometric design suggesting dojo training

2. **Philosophy Section**:
   - Two-column layout (md:grid-cols-2)
   - Left: Text about approach through experience
   - Right: Supporting visual or icon set

3. **Skills Overview**:
   - Three-column grid (lg:grid-cols-3)
   - Cards highlighting key learning outcomes
   - Icons representing different skills

4. **Unique Approach**:
   - Centered text block with max-w-3xl
   - Emphasis on "кровь и пот" (blood and sweat) methodology
   - Visual testimonial or journey metaphor

5. **Learning Path Preview**:
   - Horizontal timeline or card carousel
   - Shows sample topics (Введение → Типы данных → ООП)
   - Progression arrows or path visualization

6. **CTA Section**:
   - Centered call-to-action
   - "Начать обучение" button
   - Supporting text about free access or community

7. **Footer**:
   - Minimal: Copyright, links to about/contact
   - Social links if applicable

---

## Samurai Theme Elements

**Subtle Integration:**
- Corner accents: Small geometric borders inspired by Japanese architecture
- Dividers: Use thin lines with subtle end caps (like sword edges)
- Icons: Incorporate minimalist Japanese design patterns where appropriate
- Loading states: Simple circular progress inspired by Enso (Zen circle)
- Success states: Subtle reference to achievement/mastery

**Avoid:**
- Excessive katana imagery
- Generic cherry blossoms everywhere
- Stereotypical "Asian font" overuse

---

## Animations

**Minimal & Purposeful:**
- Page transitions: Simple fade (200ms)
- Sidebar expand/collapse: Smooth height animation (300ms)
- Card hover: Subtle scale (1.02) or border glow
- Button interactions: Standard Shadcn hover states
- NO distracting scroll animations or parallax

---

## Accessibility

- Consistent focus states on all interactive elements
- Keyboard navigation for lesson switching (arrow keys)
- ARIA labels for theme/language switchers
- Sufficient contrast ratios in both themes
- Readable font sizes (minimum 16px for body)

---

## Images

**Onboarding Hero**: Use abstract representation of a dojo training space or minimalist Japanese geometric pattern - NOT literal samurai imagery. Should evoke focus, discipline, and learning environment.

**Topic Cards**: Optional small icons or abstract representations for each topic category.

**Lesson Content**: Support for embedded images within rich text editor, user-uploaded.

---

## Responsive Behavior

- Mobile: Stack all columns, collapsible sidebar as drawer
- Tablet: Two-column grids become single column
- Desktop: Full layout with fixed sidebar navigation
- Breakpoints: sm, md, lg, xl following Tailwind standards