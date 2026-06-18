// @ts-check
import { defineConfig } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';

import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://188scoutsmarins.ca',

  redirects: {
    '/a-propos/inscription-2': '/a-propos/inscription',
    '/a-propos/inscription-2/': '/a-propos/inscription/',
  },

  vite: {
    plugins: [tailwindcss()]
  },

  integrations: [
    sitemap({
      filter: (page) => !page.includes('/admin') && !page.includes('/styleguide'),
    }),
  ],
});