// @ts-check
import { defineConfig } from 'astro/config';
import { visit } from 'unist-util-visit';

import tailwindcss from '@tailwindcss/vite';

import sitemap from '@astrojs/sitemap';

/** Add lazy loading and async decoding to markdown images. */
function rehypeLazyImages() {
  /** @param {import('hast').Root} tree */
  return (tree) => {
    visit(tree, 'element', (node) => {
      if (node.tagName !== 'img') return;

      const props = node.properties ?? {};
      if (!props.loading) props.loading = 'lazy';
      if (!props.decoding) props.decoding = 'async';
      node.properties = props;
    });
  };
}

// https://astro.build/config
export default defineConfig({
  site: 'https://188scoutsmarins.ca',

  vite: {
    plugins: [tailwindcss()],
  },

  markdown: {
    rehypePlugins: [rehypeLazyImages],
  },

  integrations: [
    sitemap({
      filter: (page) => !page.includes('/admin') && !page.includes('/styleguide'),
    }),
  ],
});
