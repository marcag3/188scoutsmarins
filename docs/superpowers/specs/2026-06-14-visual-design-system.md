# Visual Design System — 188e Groupe Scout Marin

**Date:** 2026-06-14  
**Status:** Approved  
**Primary inspiration:** `design/Pub MédiasSociauxBaseNautique2026.pdf`  
**Reference render:** `design/base-nautique-pub-reference.png`  
**Secondary sources:** `design/logo.jpg`, `design/scoutisme marin(1).png`, `design/font.md`

---

## Design direction

The site follows the **Base Nautique promotional poster** (Microsoft Publisher, Arrondissement MTL-NORD). That document defines the principal visual language:

| Pub element | Web implementation |
|-------------|-------------------|
| Navy header band + marker headline | `Hero` top bar — "Viens … avec NOUS!" |
| Full-bleed outdoor photo | Hero background image |
| Inset photo with **red border** | `InsetPhoto` component |
| **Starburst** badges ("Gratuit", "2e Édition") | `StarburstBadge` component |
| Stacked **white info boxes** with thick navy border | `InfoBox` component |
| **Red horizontal rules** between sections | `RedRule` component |
| "Inscris-toi ici" CTA box | `InfoBox` as link / button |
| "Et puis.. **Embarques-tu?**" serif italic | `.tagline-serif` (Lora) |
| Navy footer + **black fine-print bar** | `Footer` |
| Logo anchor + fleur-de-lis | `design/logo.jpg` |

The older circular-frame style from `scoutisme marin(1).png` is **secondary** — used sparingly if at all.

---

## Color tokens

From the Base Nautique pub and logo:

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-navy` | `#0a1a3a` | Header bands, borders, footer |
| `--color-red` | `#d71920` | Rules, inset borders, accents |
| `--color-white` | `#ffffff` | Info boxes, starbursts, text on navy |
| `--color-sand` | `#f5f2ec` | Alternate section background |
| `--color-black` | `#000000` | Fine-print footer strip |

---

## Typography

| Role | Font | Matches pub |
|------|------|-------------|
| **Marker headlines** | [Permanent Marker](https://fonts.google.com/specimen/Permanent+Marker) | "Viens RAMER avec NOUS!" |
| **Info box labels** | Source Sans 3 bold caps | "Dates", "Heures", "Lieu" |
| **Tagline** | [Lora](https://fonts.google.com/specimen/Lora) italic | "Embarques-tu?" |
| **Body** | Source Sans 3 | Paragraphs, forms, nav |
| **Accent script** | Kristen ITC / Kristi | Optional accents per `font.md` |

---

## Component inventory

| Component | Pub source |
|-----------|------------|
| `Hero` | Full poster layout |
| `InfoBox` | Date/time/location/CTA boxes |
| `StarburstBadge` | "Gratuit", "2e Édition" |
| `InsetPhoto` | Top-left framed inset |
| `RedRule` | Red section dividers |
| `Header` / `Nav` | Navy top bar |
| `Footer` | Navy + black fine print |
| `PhotoGrid` | Photo sections (bordered cards) |
| `CalendarEmbed` | Activity schedule |
| `ContactForm` | Styled with info-box inputs |
| `PageLayout` | Inner pages with marker title + red rule |

---

## Pages for design validation

| Route | Purpose |
|-------|---------|
| `/` | Homepage — poster-style hero + info boxes |
| `/styleguide` | All pub-derived components |

Content migration happens **after** design sign-off.
