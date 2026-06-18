import rabaskaSettings from '../content/settings/rabaska.json';

export type RabaskaDateStatus = 'open' | 'cancelled';

export const rabaskaDateStatusLabels: Record<RabaskaDateStatus, string> = {
  open: 'Confirmé',
  cancelled: 'Annulé',
};

export const rabaska = {
  ...rabaskaSettings,
  dates: rabaskaSettings.dates.map((date) => ({
    label: date.label,
    status: date.status as RabaskaDateStatus,
  })),
};
