export const partners = [
  { name: "Corporation des scouts marins du grand Montréal", logo: "/images/partners/LogoSMGM_2016-228x300.jpg", href: "http://www.scoutsmarins.ca/" },
  { name: "Jeunes marins urbains", logo: "/images/partners/JMU_Logo_RVB_Noir.webp", href: "https://www.jeunesmarinsurbains.org/" },
  { name: "Arrondissement de Montréal-Nord", logo: "/images/partners/mtl-nord.png", href: "https://montreal.ca/montreal-nord" },
  { name: "Église Sainte-Colette", logo: "/images/partners/ste-colette-150x150.jpg", href: "http://www.ste-colette.com/" },
] as const;

export type Partner = (typeof partners)[number];
