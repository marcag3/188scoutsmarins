import partnersSettings from '../content/settings/partners.json';

export type Partner = {
  name: string;
  logo?: string;
  href?: string;
  color?: boolean;
};

export const partners: Partner[] = partnersSettings.partners;
