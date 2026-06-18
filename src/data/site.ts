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

export const ageGroups = [
  { label: 'Castors', ages: '7–9 ans', emoji: '🦫', href: '/castor/' },
  { label: 'Louveteaux', ages: '9–12 ans', emoji: '🐺', href: '/meute/' },
  { label: 'Éclaireurs', ages: '12–17 ans', emoji: '🧭', href: '/troupe/' },
  { label: 'Clan', ages: '17 ans +', emoji: '🔺', href: '/clan/' },
] as const;
