import general from '../content/settings/general.json';

export const site = {
  name: '188e groupe de scoutisme marin',
  location: 'Montréal-Nord',
  tagline: general.tagline,
  meetingInfo: general.meetingInfo,
  email: '188scoutmarin@gmail.com',
  social: general.social,
  affiliation: "Membre de l'association des aventuriers de Baden-Powell",
} as const;

export type NavItem = {
  label: string;
  href: string;
  children?: NavItem[];
};

export const navigation: NavItem[] = [
  {
    label: 'À propos',
    href: '/a-propos/',
    children: [
      { label: 'Inscription', href: '/a-propos/inscription-2/' },
      { label: 'Calendrier', href: '/a-propos/calendrier/' },
      { label: 'Photos', href: '/a-propos/photos/' },
    ],
  },
  {
    label: 'Contact',
    href: '/contact/',
    children: [{ label: "S'impliquer", href: '/contact/simpliquer/' }],
  },
  {
    label: 'Louveteaux/Louvettes',
    href: '/meute/',
  },
  {
    label: 'Éclaireurs / Guides',
    href: '/troupe/',
  },
  {
    label: 'Partenaires',
    href: '/partenaires/',
  },
];

export const ageGroups = [
  { label: 'Castors', ages: '7–9 ans', emoji: '🦫' },
  { label: 'Louveteaux', ages: '9–12 ans', emoji: '🐺' },
  { label: 'Éclaireurs', ages: '12–17 ans', emoji: '🧭' },
] as const;
