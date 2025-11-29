# GO-DOJO | Go 道場

## Overview

GO-DOJO is an educational platform for learning the Go programming language through a structured, practice-oriented approach inspired by Japanese dojo philosophy. The platform features a bilingual interface (Russian/English) with a samurai/Japanese aesthetic theme, providing interactive lessons organized by topics with a rich text editor for content creation and management.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Framework & Build System**
- React 18+ with TypeScript for type-safe component development
- Vite as the build tool and development server with HMR support
- Wouter for lightweight client-side routing
- TanStack Query (React Query) for server state management with infinite stale time and disabled refetching

**UI Component System**
- Shadcn UI components (New York style) with Radix UI primitives for accessible, unstyled components
- Tailwind CSS with custom design tokens aligned with the Japanese/samurai aesthetic
- CSS variables for theming with light/dark mode support
- Custom spacing units (2, 4, 6, 8, 12, 16, 20, 24) for consistent layout
- Google Fonts integration: Inter (UI), Noto Sans JP (Japanese characters), JetBrains Mono (code)

**State Management & Data Flow**
- React Context for theme management (light/dark mode persistence)
- i18next for internationalization with Russian and English translations stored in client-side resources
- Local storage for persisting user preferences (theme, language)
- Session storage for admin authentication state

**Rich Text Editing**
- TipTap editor with StarterKit, allowing headings, bold, italic, underline, links, images, color selection, lists, quotes, and code blocks
- Custom toolbar with popover-based color picker and link/image insertion
- HTML content storage for lesson content in both Russian and English
- Image support with direct URL links (recommended: use direct image URLs like from imgbb or Imgur)

### Backend Architecture

**Server Framework**
- Express.js HTTP server with custom middleware
- HTTP server (not using WebSockets despite ws package being available)
- Custom logging middleware tracking request duration and response details
- JSON body parsing with raw body preservation for potential webhook handling

**API Design Pattern**
- RESTful API endpoints under `/api` prefix
- Resource-based routing: `/api/topics`, `/api/lessons`
- Simple password-based admin authentication (session-stored, no JWT despite package presence)
- CRUD operations for topics and lessons with Zod schema validation

**Data Layer**
- PostgreSQL database via Neon (Replit built-in database)
- Drizzle ORM for type-safe database queries
- DBStorage class implementing IStorage interface
- UUID-based entity identification using crypto.randomUUID()
- Bilingual content storage (Russian/English) for all resources
- All data persists in PostgreSQL - no data loss on app restart

**Build & Deployment**
- Custom build script using esbuild for server bundling
- Selective dependency bundling (allowlist) to reduce cold start times
- Vite for client build with public asset output
- Development mode with Vite middleware integration and HMR
- Production mode serving static files from dist/public

### Data Models

**Topic Schema (PostgreSQL Table: topics)**
- Fields: id (varchar, primary key), titleRu, titleEn, descriptionRu, descriptionEn, order, icon (optional)
- Ordering system for curriculum progression
- Icon mapping for visual representation (book, code, layers, zap, git, database)

**Lesson Schema (PostgreSQL Table: lessons)**
- Fields: id (varchar, primary key), topicId (varchar, foreign key), titleRu, titleEn, contentRu, contentEn, order
- Foreign key relationship to topics via topicId
- Rich HTML content stored for both languages
- Sequential ordering within topics

**Validation**
- Drizzle ORM schemas for database structure
- Zod schemas derived from Drizzle for runtime validation
- Separate insert schemas omitting auto-generated IDs
- Type inference from Zod schemas for TypeScript types

### Routing Strategy

**Client Routes**
- `/` - Topics listing page
- `/onboarding` - Platform introduction and philosophy
- `/topic/:id` - Individual topic with lessons list
- `/lesson/:id` - Lesson detail with navigation
- `/adminpanelka` - Admin panel for content management (password-protected)
- Fallback to 404 page for unmatched routes

**Server Routes**
- `POST /api/admin/login` - Admin authentication
- `GET /api/topics` - List all topics
- `GET /api/topics/:id` - Get single topic
- `GET /api/topics/:id/lessons` - Get lessons for a topic
- `POST /api/topics` - Create new topic
- `GET /api/lessons` - List all lessons
- `GET /api/lessons/:id` - Get single lesson
- `POST /api/lessons` - Create new lesson
- Additional update/delete endpoints for topics and lessons

### Styling & Theming

**Design System**
- Reference-based approach inspired by Stepik/Metanit educational platforms
- Samurai discipline aesthetic with clean layouts and breathing room
- Custom CSS variables for color system with separate light/dark modes
- Hover and active elevation effects using opacity-based shadows
- Custom border radius values (9px, 6px, 3px) for consistent UI elements

**Color Architecture**
- HSL color space with alpha channel support for all theme colors
- Separate color definitions for cards, popovers, sidebars with specific borders
- Chart colors defined for potential data visualization
- Button outline and badge outline using RGBA for subtle borders

## External Dependencies

### Database
- PostgreSQL database via Neon (Replit built-in)
- Drizzle ORM for type-safe database operations
- Schema definition in `shared/schema.ts` using Drizzle tables
- Automatic migrations via `npm run db:push`
- DATABASE_URL environment variable (auto-configured by Replit)

### UI Libraries
- Radix UI primitives (20+ components): accordion, alert-dialog, avatar, checkbox, dialog, dropdown-menu, etc.
- TipTap extensions for rich text editing
- Lucide React for icon system
- class-variance-authority (cva) for variant-based component styling
- Embla Carousel for potential carousel functionality

### Development Tools
- TypeScript with strict mode and ESNext module resolution
- Vite plugins: @replit/vite-plugin-runtime-error-modal, @replit/vite-plugin-cartographer, @replit/vite-plugin-dev-banner (Replit-specific)
- Path aliases: `@/` for client source, `@shared/` for shared code, `@assets/` for attached assets
- PostCSS with Tailwind CSS and Autoprefixer

### Internationalization
- i18next with react-i18next for translation management
- Language detection from localStorage with fallback
- Translation resources embedded in client code (not external files)

### Admin Authentication
- Hardcoded password: "Semen10082008" (stored in server/routes.ts)
- Session-based authentication using sessionStorage on client
- No encryption or JWT despite available packages

## Recent Changes (29 Nov 2025)

- **Migrated to PostgreSQL**: Transitioned from in-memory storage to Neon PostgreSQL database
- **Implemented Drizzle ORM**: Replaced manual MemStorage with database layer using Drizzle
- **Fixed image rendering**: Added proper CSS styling for TipTap Image extension
- **Header improvements**: Centered navigation links, repositioned theme/language toggles
- **Logo update**: Changed to Hiragana "ご" character
- **Footer year**: Updated copyright to 2025
