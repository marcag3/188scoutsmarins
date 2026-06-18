# 188e Montréal-Nord — scoutisme marin

Site web du [188e groupe scout marin de Montréal-Nord](https://188scoutsmarins.ca), construit avec [Astro](https://astro.build), [Tailwind CSS](https://tailwindcss.com) et [Decap CMS](https://decapcms.org). Hébergé sur Cloudflare Pages.

## Structure

```text
public/
  admin/          # Decap CMS (config.yml)
  images/         # photos et logos
src/
  components/     # composants Astro réutilisables
  content/
    pages/        # pages Markdown (routées automatiquement)
    settings/     # paramètres CMS (général, rabaska, partenaires)
  data/           # données dérivées des paramètres
  layouts/        # gabarits de page
  lib/            # utilitaires (navigation, contenu)
  pages/          # routes spéciales (accueil, admin, 404)
docs/
  editing-guide.md  # guide pour les éditeurs
```

## Commandes

| Commande | Action |
|----------|--------|
| `npm install` | Installer les dépendances |
| `npm run dev` | Serveur local sur `localhost:4321` |
| `npm run build` | Build de production dans `dist/` |
| `npm run preview` | Prévisualiser le build |
| `npm run check` | Vérification TypeScript et Astro |

## Édition du contenu

Les responsables du groupe modifient le site via [Decap CMS](https://188scoutsmarins.ca/admin/). Voir [docs/editing-guide.md](docs/editing-guide.md) pour le guide complet.

## Déploiement

Chaque commit sur `main` déclenche un build Cloudflare Pages. Les fonctions OAuth dans `functions/api/` permettent la connexion GitHub pour Decap CMS.

## Prérequis

- Node.js ≥ 24
