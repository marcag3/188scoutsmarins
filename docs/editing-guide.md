# Guide d'édition du site — 188e scout marin

Ce site est géré par **Decap CMS** (interface web) et hébergé sur **Cloudflare Pages**. Toute modification publiée sur GitHub déclenche une mise à jour automatique du site (quelques minutes).

## Accéder à l'administration

1. Ouvrez [https://188scoutsmarins.ca/admin/](https://188scoutsmarins.ca/admin/) (ou `/admin` en prévisualisation).
2. Connectez-vous avec votre compte **GitHub** (accès au dépôt `marcag3/188scoutsmarins` requis).
3. La première connexion peut demander d'autoriser l'application OAuth Decap CMS.

## Modifier une page

1. Dans le menu gauche, cliquez sur **Pages**.
2. Choisissez la page (ex. *À propos*, *Inscription*).
3. Modifiez le titre, la description ou le contenu (éditeur Markdown).
4. Cliquez sur **Publier** en haut à droite.
5. Attendez 2 à 5 minutes que Cloudflare reconstruise le site.

### Mise en page spéciale

Certaines pages utilisent un modèle particulier (champ *Mise en page*) :

| Mise en page | Effet |
|--------------|-------|
| `default` | Texte seulement |
| `contact` | Formulaire de contact en bas de page |
| `calendar` | Calendrier Google intégré |
| `partners` | Grille des logos partenaires |

Le champ **Chemin URL** (`path`) doit correspondre à l'adresse du site (ex. `a-propos/inscription`). Ne le changez pas sans raison.

## Paramètres généraux

**Paramètres → Général** permet de modifier :

- Slogan et texte des réunions (accueil, pied de page)
- Liens Facebook, Instagram, TikTok
- URL du calendrier intégré
- Identifiant **Formspree** pour le formulaire de contact

### Formulaire de contact (Formspree)

1. Créez un formulaire gratuit sur [formspree.io](https://formspree.io) avec le courriel `188scoutmarin@gmail.com`.
2. Copiez l'identifiant (partie après `/f/` dans l'URL).
3. Collez-le dans **ID Formspree** dans les paramètres.

## Sorties en rabaska

**Paramètres → Rabaska** permet de gérer la bannière saisonnière sur l'accueil :

- Activer ou désactiver la bannière
- Dates, statut (confirmé / annulé), horaire, lieu
- Lien de réservation et image

## Partenaires

**Paramètres → Partenaires** permet d'ajouter, modifier ou retirer les logos affichés sur la page [Partenaires](/partenaires/).

## Brouillons

Cochez **Brouillon** pour masquer une page du site public sans la supprimer.

## Délai de publication

Après **Publier**, Cloudflare Pages reconstruit le site. Comptez **2 à 5 minutes** avant de voir les changements en ligne. Videz le cache du navigateur si nécessaire.

## Besoin d'aide ?

Contactez la personne responsable du site ou ouvrez une issue sur GitHub.
