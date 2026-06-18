import type { CollectionEntry } from 'astro:content';

/** URL path for a page entry (no leading/trailing slashes). */
export function getPagePath(page: CollectionEntry<'pages'>): string {
  return page.data.path ?? page.id;
}

/** Path string for Astro catch-all `params.slug`. */
export function getPageSlugParam(page: CollectionEntry<'pages'>): string {
  return getPagePath(page);
}
