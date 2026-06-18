import general from '../content/settings/general.json';

function sentenceCase(text: string): string {
  return text.charAt(0).toLowerCase() + text.slice(1);
}

export const site = {
  name: '188e Montréal-Nord',
  subtext: 'scoutisme marin',
  location: 'Montréal-Nord',
  tagline: general.tagline,
  meetingSchedule: general.meetingSchedule,
  meetingLocation: general.meetingLocation,
  meetingInfo: `Réunions les ${sentenceCase(general.meetingSchedule)} au ${sentenceCase(general.meetingLocation)}`,
  social: general.social,
  affiliation: "Membre de l'association des aventuriers de Baden-Powell",
  affiliationName: "Association des aventuriers de Baden-Powell",
  affiliationUrl: "https://aventuriersdebadenpowell.org/",
  affiliationLogo: "/images/photos/logo-aabp-1024.jpg",
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
      { label: 'Inscription', href: '/a-propos/inscription/' },
      { label: 'Calendrier', href: '/a-propos/calendrier/' },
    ],
  },
  {
    label: 'Contact',
    href: '/contact/',
    children: [{ label: "S'impliquer", href: '/contact/simpliquer/' }],
  },
  {
    label: 'Castors',
    href: '/castor/',
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
    label: 'Clan',
    href: '/clan/',
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
