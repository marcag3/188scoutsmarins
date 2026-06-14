# Jamstack Migration — 188e Groupe Scout Marin

**Date:** 2026-06-14  
**Site:** https://188scoutsmarins.ca/  
**Status:** Approved (2026-06-14)

---

## Context

The site is a French-language WordPress site for a volunteer-run scout group in Montréal-Nord. It is already proxied through **Cloudflare**. Content is mostly static pages; dynamic features are limited to a contact form, an embedded Google Calendar, and a photo gallery.

### Current site inventory

| URL | Purpose | Migration notes |
|-----|---------|-----------------|
| `/` | Homepage + calendar widget | Rebuild layout; keep Google Calendar embed |
| `/a-propos/` | Long-form about content | Markdown page |
| `/a-propos/inscription-2/` | Registration info, cost table, PDF link | Markdown + assets |
| `/a-propos/calendrier/` | Calendar page | Google Calendar embed |
| `/a-propos/photos/` | Photo albums (e.g. Camp d'été 2021) | Static image galleries or external album embed |
| `/contact/` | Contact form (nom, courriel, message) | Third-party form handler |
| `/contact/simpliquer/` | Fundraising / volunteer info | Markdown page |
| `/meute/` | Louveteaux section (9–11) | Markdown page |
| `/troupe/` | Éclaireurs / Guides (12–17) | Markdown page |
| `/partenaires/` | Partner logos/links | Markdown or structured data |
| `/wp-admin` | WordPress admin | Replaced by `/admin` CMS UI |

### Goals

1. Replace WordPress with a maintainable, low-cost Jamstack site.
2. Let volunteer leaders edit content without touching code for routine updates.
3. Stay on free or near-free hosting tiers.
4. Preserve SEO, existing URL paths, and integrations (Google Calendar, social links).
5. Keep the domain `188scoutsmarins.ca` on Cloudflare.

### Non-goals (v1)

- Rebuilding the calendar in custom code (keep Google Calendar).
- Building a custom membership database.
- Migrating `/meute/espace-louveteaux/` (password-protected page — dropped).
- URL redirects from old WordPress paths (not needed).
- Multilingual support (French only for now).
- Blog/comments (no active blog detected).

### Decisions (confirmed)

- **Editors:** Tech-comfortable volunteers with GitHub accounts → Decap CMS + GitHub OAuth.
- **Protected page:** Not reproduced.
- **Redirects:** None.

---

## Recommended stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Site generator** | [Astro 5](https://astro.build) | Fast static output, markdown content collections, reusable layout components, minimal JavaScript |
| **Styling** | Tailwind CSS 4 | Fast to match existing design; good utility for responsive nav and tables |
| **Content format** | Markdown + YAML frontmatter | Version-controlled, diffable, CMS-friendly |
| **CMS** | [Decap CMS](https://decapcms.org) | Free, Git-based, `/admin` UI familiar to WordPress users, no database |
| **CMS auth** | GitHub OAuth (Decap + Cloudflare Pages) | Free; editors need a GitHub account (one-time onboarding) |
| **Hosting** | Cloudflare Pages | Site already on Cloudflare; free tier, global CDN, custom domain |
| **Source control** | GitHub | Triggers Pages build on push; Decap commits back to repo |
| **Contact form** | [Formspree](https://formspree.io) (free tier) or Cloudflare Worker + Resend | No server to maintain; email notifications to group inbox |
| **Calendar** | Existing Google Calendar embed | No change to editorial workflow |
| **Images** | `public/images/` in repo | Simple; optimize at build with Astro assets. Upgrade to Cloudflare Images later if gallery grows |
| **Analytics** | Cloudflare Web Analytics (free, privacy-friendly) | No cookie banner complexity |

### Why this stack over alternatives

**vs. Google Sheets as CMS**  
Sheets work for tabular data but are poor for long pages, image galleries, and navigation. This site is page-heavy; markdown + Decap is a better fit.

**vs. Netlify + Netlify Identity**  
Smoother non-technical auth, but the domain is already on Cloudflare. Staying on Cloudflare Pages avoids splitting DNS/hosting and keeps one vendor.

**vs. Sanity / Contentful**  
Excellent editor UX, but adds a paid tier risk and another account for volunteers. Overkill for ~10 pages.

**vs. Next.js**  
More complexity and client JS than needed for a brochure-style scout site.

**vs. Hugo / Eleventy**  
Valid choices; Astro wins on component ergonomics for shared nav/footer and future interactive islands if needed.

---

## Architecture

```
Editors ──► Decap CMS (/admin) ──► GitHub repo (markdown)
                                        │
                                        ▼
                              Cloudflare Pages build (Astro)
                                        │
                              ┌─────────┴─────────┐
                              ▼                   ▼
                        Static HTML/CSS    Formspree (forms)
                              │
                              ▼
                      188scoutsmarins.ca
```

### Content model

```
src/content/
  pages/           # one markdown file per page (slug matches URL)
  albums/          # photo albums (title, year, images[])
  partners/        # optional: structured partner entries
  settings/        # site-wide: tagline, meeting time, social links
```

### URL strategy

Keep the same paths as the current WordPress site (e.g. `/a-propos/inscription-2/`). No redirect rules.

---

## Editorial workflow

1. Editor opens `https://188scoutsmarins.ca/admin` (or staging URL during migration).
2. Logs in with GitHub (invited as collaborator on the repo).
3. Edits a page in the Decap UI (WYSIWYG markdown).
4. Clicks **Publish** → Decap commits to `main` → Cloudflare Pages rebuilds (~1–2 min).
5. Changes are live.

For photo albums: editor uploads images through Decap media library (committed to `public/images/albums/`).

---

## Special feature handling

### Contact form

Replace WordPress form with a static HTML form posting to Formspree. Spam protection via Formspree honeypot or Turnstile (Cloudflare, free).

### Mailing list (mentioned on inscription page)

Keep linking to the existing list tool (Google Groups, Mailchimp, etc.). Do not rebuild list management in v1.

---

## Assumptions (confirm before build)

1. **Editors have GitHub accounts** and are comfortable using Decap CMS.
2. **WordPress export is available** (Tools → Export, or hosting backup) for content and `wp-content/uploads`.
3. **Google Calendar embed URL** can be copied from the current site.
4. **Contact form emails** go to the existing group address (`188scoutmarin@m` or similar).
5. **Cloudflare account access** exists for DNS and Pages.

---

## Success criteria

- [ ] All public pages migrated with equivalent content and images
- [ ] Contact form delivers email reliably
- [ ] Google Calendar displays on homepage and/or calendrier page
- [ ] Volunteer can update a page text without developer help
- [ ] Lighthouse performance ≥ 90 on mobile
- [ ] URL paths match the current site (no broken links)
- [ ] WordPress hosting can be cancelled after 2-week parallel run

---

## Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Build fails on bad markdown | PR preview builds; Decap validates required fields |
| SEO drop on cutover | Preserve titles/meta, submit sitemap, keep same URL paths |
| Large photo repo slows builds | Lazy migration: host heavy albums on Google Photos embed initially |
