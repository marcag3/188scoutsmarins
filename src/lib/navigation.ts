import type { CollectionEntry } from 'astro:content';
import type { NavItem } from '../data/site';
import { getPagePath } from './content';

export function buildNavigation(pages: CollectionEntry<'pages'>[]): NavItem[] {
  const published = pages.filter((page) => !page.data.draft);

  const childrenByParent = new Map<string, CollectionEntry<'pages'>[]>();

  for (const page of published) {
    const parent = page.data.navParent;
    if (!parent) continue;

    const siblings = childrenByParent.get(parent) ?? [];
    siblings.push(page);
    childrenByParent.set(parent, siblings);
  }

  const topLevel = published
    .filter((page) => {
      const path = getPagePath(page);
      return !page.data.navParent && !path.includes('/');
    })
    .sort((a, b) => a.data.order - b.data.order);

  return topLevel.map((page) => {
    const path = getPagePath(page);
    const children = (childrenByParent.get(path) ?? [])
      .sort((a, b) => a.data.order - b.data.order)
      .map((child) => ({
        label: child.data.navLabel ?? child.data.title,
        href: `/${getPagePath(child)}/`,
      }));

    const item: NavItem = {
      label: page.data.navLabel ?? page.data.title,
      href: `/${path}/`,
    };

    if (children.length > 0) {
      item.children = children;
    }

    return item;
  });
}
