# Jamstack Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild https://188scoutsmarins.ca/ as a static Astro site with Decap CMS, hosted on Cloudflare Pages, replacing WordPress.

**Architecture:** Markdown content in GitHub → Astro static build → Cloudflare Pages CDN. Decap CMS provides `/admin` editing for tech-comfortable volunteers via GitHub OAuth. Formspree handles contact.

**Tech Stack:** Astro 5, Tailwind CSS 4, Decap CMS, GitHub, Cloudflare Pages, Formspree, Google Calendar embed

**Spec:** `docs/superpowers/specs/2026-06-14-jamstack-migration-design.md`

---

## File structure (target)

```
188scoutsmarins/
├── public/
│   ├── admin/
│   │   └── config.yml          # Decap CMS config
│   ├── images/                 # logos, album photos
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── Header.astro
│   │   ├── Footer.astro
│   │   ├── Nav.astro
│   │   ├── CalendarEmbed.astro
│   │   ├── ContactForm.astro
│   │   ├── PhotoAlbum.astro
│   │   └── PartnerGrid.astro
│   ├── content/
│   │   ├── config.ts           # Astro content collections schema
│   │   ├── pages/              # *.md — site pages
│   │   ├── albums/             # *.md — photo albums
│   │   └── settings/
│   │       └── general.json    # tagline, social links, meeting info
│   ├── layouts/
│   │   ├── BaseLayout.astro
│   │   └── PageLayout.astro
│   ├── pages/
│   │   ├── index.astro
│   │   ├── [...slug].astro     # catch-all for content pages
│   │   └── admin.astro         # loads Decap CMS
│   └── styles/
│       └── global.css
├── astro.config.mjs
├── package.json
├── tailwind.config.mjs
└── wrangler.toml               # optional Cloudflare Pages config
```

---

## Phase 0 — Discovery and content export

### Task 0.1: WordPress content audit

- [ ] **Step 1:** Log into WordPress admin (`/wp-admin`) and export all content via **Tools → Export → All content** (WXR file).
- [ ] **Step 2:** Download `wp-content/uploads/` from hosting (FTP, cPanel, or host backup).
- [ ] **Step 3:** Create a spreadsheet of all URLs, page titles, and template type:

| URL | Title | Type | Notes |
|-----|-------|------|-------|
| `/` | Accueil | homepage + calendar | |
| `/a-propos/` | À propos | long text | |
| `/a-propos/inscription-2/` | Inscription | text + table + PDF | keep slug as-is |
| `/a-propos/calendrier/` | Calendrier | calendar embed | |
| `/a-propos/photos/` | Photos | gallery | |
| `/contact/` | Contact | form | |
| `/contact/simpliquer/` | S'impliquer | text | |
| `/meute/` | Louveteaux | text | |
| `/troupe/` | Éclaireurs | text | |
| `/partenaires/` | Partenaires | logos | |

**Out of scope:** `/meute/espace-louveteaux/` (password-protected page — not migrated).

- [ ] **Step 4:** Copy Google Calendar embed iframe `src` from current homepage (View Source → search `calendar.google.com`).
- [ ] **Step 5:** Note contact form destination email and any mailing-list signup URL.

---

## Phase 1 — Project scaffold

### Task 1.1: Initialize Astro project

**Files:**
- Create: project root via `npm create astro@latest`

- [ ] **Step 1:** Scaffold the project:

```bash
cd /home/mag/repo/188scoutsmarins
npm create astro@latest . -- --template minimal --install --typescript strict --git false
```

- [ ] **Step 2:** Add Tailwind:

```bash
npx astro add tailwind --yes
```

- [ ] **Step 3:** Verify dev server:

```bash
npm run dev
```

Expected: site at `http://localhost:4321`

- [ ] **Step 4:** Commit scaffold:

```bash
git add -A
git commit -m "chore: scaffold Astro + Tailwind project"
```

### Task 1.2: Configure Cloudflare Pages adapter

**Files:**
- Modify: `astro.config.mjs`

- [ ] **Step 1:** Install adapter:

```bash
npx astro add cloudflare --yes
```

- [ ] **Step 2:** Set `output: 'static'` in `astro.config.mjs`.

- [ ] **Step 3:** Add build script verification:

```bash
npm run build
```

Expected: `dist/` folder created without errors.

---

## Phase 2 — Visual design system (before content migration)

**Spec:** `docs/superpowers/specs/2026-06-14-visual-design-system.md`  
**Primary design reference:** `design/Pub MédiasSociauxBaseNautique2026.pdf`

Design is implemented with placeholder copy. WordPress content is migrated only after design sign-off on `/` and `/styleguide`.

### Task 2.1: Design tokens and global styles

**Files:**
- Create: `src/styles/global.css`
- Reference: `design/logo.jpg`, `design/scoutisme marin(1).png`, `design/font.md`

- [x] Define color tokens (navy, red, sand, grey) in `@theme`
- [x] Load Bebas Neue + Source Sans 3 via Google Fonts; Kristen ITC via `/public/fonts/` when available
- [x] Add `.dot-pattern`, `.display-*`, `.prose-scout` utility classes

### Task 2.2: UI component library

**Files:**
- Create: `src/components/ui/` — Button, Section, Card, CircleImage, AgeGroupBadge
- Create: `src/components/` — Header, Nav, Footer, Hero, CTABanner, ContactForm, PhotoGrid, PartnerGrid, CalendarEmbed
- Create: `src/layouts/BaseLayout.astro`, `src/layouts/PageLayout.astro`
- Create: `src/data/site.ts` — nav structure, site metadata

- [x] All components use design tokens (no one-off colors)
- [x] Nav matches WordPress menu structure (minus espace louveteaux)

### Task 2.3: Design preview pages

**Files:**
- Create: `src/pages/index.astro` — homepage shell with placeholder content
- Create: `src/pages/styleguide.astro` — all component variants

- [x] Homepage demonstrates hero, sections, calendar placeholder, CTA, cards
- [x] Styleguide documents typography, colors, buttons, forms, grids
- [ ] **Review with stakeholders** — adjust colors/spacing before Phase 5 content migration

### Task 2.4: Brand assets

- [x] Copy `design/logo.jpg` → `public/images/logo.jpg`
- [x] Copy sample photos → `public/images/photos/` for design preview
- [ ] Add licensed `kristen-itc.woff2` to `public/fonts/` if exact font is required (optional; Kristi fallback active)

---

## Phase 3 — Content model and page routing

### Task 2.1: Define content collections

**Files:**
- Create: `src/content/config.ts`

- [ ] **Step 1:** Create collection schema:

```typescript
// src/content/config.ts
import { defineCollection, z } from 'astro:content';

const pages = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    navLabel: z.string().optional(),
    navParent: z.string().optional(),
    order: z.number().default(0),
    draft: z.boolean().default(false),
  }),
});

const albums = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    year: z.number(),
    cover: z.string(),
    images: z.array(z.string()),
  }),
});

export const collections = { pages, albums };
```

- [ ] **Step 2:** Create placeholder markdown for each page in `src/content/pages/` with frontmatter matching the URL slug (e.g. `a-propos.md`, `a-propos/inscription.md` using nested paths or flat slugs — pick one convention and stick to it).

---

### Task 2.2: Base layout and navigation

**Files:**
- Create: `src/layouts/BaseLayout.astro`, `src/layouts/PageLayout.astro`
- Create: `src/components/Header.astro`, `src/components/Nav.astro`, `src/components/Footer.astro`
- Create: `src/content/settings/general.json`

- [ ] **Step 1:** Build `BaseLayout.astro` with French `lang="fr"`, meta tags, header, footer slots.
- [ ] **Step 2:** Build `Nav.astro` matching current menu structure:

```
À propos → Inscription, Calendrier, Photos
Contact → S'impliquer
Louveteaux/Louvettes
Éclaireurs / Guides
Partenaires
```

- [ ] **Step 3:** Build `Footer.astro` with AABP membership note, social links (Facebook, Instagram, TikTok, email), from `general.json`.
- [ ] **Step 4:** Copy logo from WordPress uploads to `public/images/logo.jpg`.

---

### Task 2.3: Dynamic page routing

**Files:**
- Create: `src/pages/[...slug].astro`
- Create: `src/pages/index.astro`

- [ ] **Step 1:** `index.astro` — homepage with hero tagline, meeting time/location, `CalendarEmbed` component.
- [ ] **Step 2:** `[...slug].astro` — load page from `src/content/pages/` by slug; 404 if not found.
- [ ] **Step 3:** Verify all migrated slugs render locally.

---

## Phase 4 — Feature components (wire to real content)

### Task 3.1: Google Calendar embed

**Files:**
- Create: `src/components/CalendarEmbed.astro`

- [ ] **Step 1:** Paste iframe embed from WordPress into component (responsive wrapper).
- [ ] **Step 2:** Use on homepage and `a-propos/calendrier` page.

---

### Task 3.2: Contact form (Formspree)

**Files:**
- Create: `src/components/ContactForm.astro`

- [ ] **Step 1:** Create free Formspree form; note form ID.
- [ ] **Step 2:** Build form:

```html
<form action="https://formspree.io/f/XXXXXX" method="POST">
  <label>Nom *<input name="nom" required /></label>
  <label>Courriel *<input type="email" name="email" required /></label>
  <label>Message *<textarea name="message" required></textarea></label>
  <button type="submit">Envoyer</button>
</form>
```

- [ ] **Step 3:** Test submission delivers to group inbox.
- [ ] **Step 4:** Optional: add Cloudflare Turnstile widget for spam.

---

### Task 3.3: Photo albums

**Files:**
- Create: `src/components/PhotoAlbum.astro`
- Create: `src/content/albums/camp-ete-2021.md` (and others)

- [ ] **Step 1:** Migrate images from WordPress uploads into `public/images/albums/camp-ete-2021/`.
- [ ] **Step 2:** Album markdown lists image paths; `PhotoAlbum.astro` renders responsive grid.
- [ ] **Step 3:** `a-propos/photos` page lists all albums with cover thumbnails.

---

### Task 3.4: Partners page

**Files:**
- Create: `src/components/PartnerGrid.astro`

- [ ] **Step 1:** Extract partner names/logos from WordPress `/partenaires/`.
- [ ] **Step 2:** Render logo grid with optional external links.

---

## Phase 5 — Content migration

### Task 4.1: Migrate page copy

- [ ] **Step 1:** For each page in the audit spreadsheet, copy HTML content from WordPress into markdown files (use `wp export` + conversion tool or manual paste).
- [ ] **Step 2:** Convert registration cost table in `a-propos/inscription-2.md` to markdown table.
- [ ] **Step 3:** Download and link registration PDF to `public/documents/inscription.pdf`.
- [ ] **Step 4:** Proofread French content; preserve headings and structure.

**Optional conversion helper:**

```bash
npx wordpress-export-to-markdown --input export.xml --output src/content/pages
```

(Evaluate output quality; manual cleanup will be needed.)

---

### Task 4.2: SEO metadata

- [ ] **Step 1:** Copy `<title>` and meta description from each WordPress page into frontmatter.
- [ ] **Step 2:** Add Open Graph tags in `BaseLayout.astro` (title, description, logo image).
- [ ] **Step 3:** Generate `src/pages/sitemap.xml.ts` or use `@astrojs/sitemap` integration.

---

## Phase 6 — Decap CMS

### Task 5.1: CMS configuration

**Files:**
- Create: `public/admin/config.yml`
- Create: `src/pages/admin.astro`

- [ ] **Step 1:** Create `public/admin/config.yml`:

```yaml
backend:
  name: github
  repo: YOUR_ORG/188scoutsmarins
  branch: main

media_folder: public/images/uploads
public_folder: /images/uploads

locale: fr

collections:
  - name: pages
    label: Pages
    folder: src/content/pages
    create: true
    slug: "{{slug}}"
    fields:
      - { label: Titre, name: title, widget: string }
      - { label: Description, name: description, widget: string, required: false }
      - { label: Contenu, name: body, widget: markdown }
      - { label: Brouillon, name: draft, widget: boolean, default: false }

  - name: albums
    label: Albums photos
    folder: src/content/albums
    create: true
    fields:
      - { label: Titre, name: title, widget: string }
      - { label: Année, name: year, widget: number }
      - { label: Couverture, name: cover, widget: image }
      - { label: Images, name: images, widget: list, field: { label: Image, name: image, widget: image } }

  - name: settings
    label: Paramètres
    files:
      - name: general
        label: Général
        file: src/content/settings/general.json
        fields:
          - { label: Slogan, name: tagline, widget: string }
          - { label: Réunion (texte), name: meetingInfo, widget: string }
          - { label: Facebook, name: facebook, widget: string, required: false }
          - { label: Instagram, name: instagram, widget: string, required: false }
          - { label: TikTok, name: tiktok, widget: string, required: false }
          - { label: Courriel, name: email, widget: string }
```

- [ ] **Step 2:** Create `src/pages/admin.astro` that loads Decap from CDN:

```html
<!DOCTYPE html>
<html lang="fr">
<head><meta charset="utf-8"><title>Admin — 188e scout marin</title></head>
<body>
  <script src="https://unpkg.com/decap-cms@^3.0.0/dist/decap-cms.js"></script>
</body>
</html>
```

- [ ] **Step 3:** Register GitHub OAuth App for Decap (callback URL documented in Decap docs for Cloudflare Pages).

---

## Phase 7 — Hosting and DNS cutover

### Task 6.1: Cloudflare Pages deployment

- [ ] **Step 1:** Push repo to GitHub.
- [ ] **Step 2:** Cloudflare dashboard → Pages → Connect to Git → select repo.
- [ ] **Step 3:** Build settings: command `npm run build`, output `dist`.
- [ ] **Step 4:** Deploy preview URL; verify all pages.
- [ ] **Step 5:** Add custom domain `188scoutsmarins.ca` (and `www` redirect to apex).

### Task 6.2: Cutover checklist

- [ ] **Step 1:** Run old and new sites in parallel for 1–2 weeks (new site on Pages preview URL).
- [ ] **Step 2:** Verify form, calendar, social links, and all page URLs.
- [ ] **Step 3:** Run Lighthouse audit (target ≥ 90 performance).
- [ ] **Step 4:** Submit sitemap to Google Search Console.
- [ ] **Step 5:** Switch DNS to Cloudflare Pages production.
- [ ] **Step 6:** Cancel WordPress hosting after confirming the new site is stable.

---

## Phase 8 — Editor onboarding

### Task 7.1: Volunteer documentation

**Files:**
- Create: `docs/editing-guide.md` (French)

- [ ] **Step 1:** Write guide covering: login to `/admin`, edit a page, upload a photo, publish wait time.
- [ ] **Step 2:** Record 5-minute screen share or screenshots for committee.
- [ ] **Step 3:** Identify 2 volunteer editors; invite to GitHub repo; test one edit end-to-end.

---

## Estimated effort

| Phase | Effort |
|-------|--------|
| 0 — Discovery | 2–4 hours |
| 1 — Scaffold | 1–2 hours |
| 2 — Design system | 4–6 hours |
| 3 — Layouts + routing | 3–4 hours |
| 4 — Feature wiring | 2–3 hours |
| 5 — Content migration | 6–10 hours |
| 6 — Decap CMS | 2–4 hours |
| 7 — Deploy + cutover | 2–4 hours |
| 8 — Onboarding | 1–2 hours |
| **Total** | **~22–35 hours** |

---

## Verification checklist (final)

- [ ] `npm run build` succeeds
- [ ] All public pages render with correct French content
- [ ] Navigation matches WordPress structure (minus espace louveteaux)
- [ ] Contact form sends email
- [ ] Calendar shows current month events
- [ ] Photo albums display images
- [ ] `/admin` CMS saves and triggers rebuild
- [ ] URL paths match current WordPress site
- [ ] No `/wp-*` assets referenced
