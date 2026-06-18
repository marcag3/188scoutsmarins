import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const pages = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/pages' }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    path: z.string().optional(), // URL path e.g. a-propos/inscription (alias: slug in legacy frontmatter)
    navLabel: z.string().optional(),
    navParent: z.string().optional(),
    order: z.number().default(0),
    draft: z.boolean().default(false),
    layout: z.enum(['default', 'contact', 'calendar', 'partners']).default('default'),
  }),
});

export const collections = { pages };
