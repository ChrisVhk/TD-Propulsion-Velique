# TD 2 — De la théorie des bandes à la ligne portante · fiche élève

**EGN-S7 Propulsion assistée par le vent · séance de TD S2 · durée 2 h.** Prérequis : le cours du 23/11, deck S03 sur Vega
(diapos 17 à 22 : passage à l'aile 3D ; 24 à 26 : modèles aérodynamiques ; 31 : efforts dans le repère navire) ; le
TD 1 (outil installé, vent du cas de l'aile du caboteur).

Les exercices sont tirés de la banque d'exercices d'EGN-S7 (A05 à A08). Chaque exercice porte son **niveau** :
**niveau 1**, application directe d'une définition ou d'une formule ; **niveau 2**, enchaînement de plusieurs étapes
ou lecture critique d'une source.

# Objectifs

À la fin de la séance, vous savez :

- calculer le facteur d'allongement d'une voile et dire ce qu'il fait perdre (A05, niveau 1) ;
- calculer à la main les efforts et la puissance de poussée de l'aile du caboteur (TD 1), et dire pourquoi cette puissance
  n'est pas l'économie au moteur (A06, niveau 2) ;
- dire ce que la théorie des bandes ne corrige pas, et le mesurer en relançant le cas de l'aile du caboteur en ligne portante non
  linéaire (NLL) (A06, niveau 2) ;
- trouver par balayage le réglage qui maximise la poussée, et reconnaître un résultat qui sort du domaine de la table
  de profil (A07, niveau 2) ;
- expliquer pourquoi le nombre d'éléments ne change rien en théorie des bandes et compte en NLL (A08, niveau 1).

# Vos armes : les formules utiles (deck S03, diapos 17 à 31)

**Passage à l'aile 3D** (deck S03, diapos 18 à 20). Pour une aile d'allongement AR = H² / A (hauteur au carré sur surface) :

- C_L ≈ AR / (2 + AR) · C_L,2D ;
- C_D ≈ C_D,2D + C_L² / (e₀ π AR), où le second terme est la traînée induite (e₀ : coefficient d'Oswald).

**Efforts dans le repère navire** (deck S03, diapo 31), avec les valeurs absolues de C_L et d'AWA :

- C_x = |C_L| sin AWA − C_D cos AWA (poussée, vers l'avant) ;
- C_y = |C_L| cos AWA + C_D sin AWA (force latérale) ;
- q = ½ ρ_air AWS², F_x = C_x q A, F_y = C_y q A ;
- puissance de poussée P_x = F_x · u, où u est la vitesse du navire.

**Les modèles** (deck S03, diapos 25 et 26). En théorie des bandes, chaque bande est un profil 2D infini, sans interaction avec les
autres. En ligne portante non linéaire (NLL), les bandes interagissent par les vitesses induites de leurs
tourbillons : l'incidence effective de chaque bande est réduite.

**Données du cas de l'aile du caboteur** (fichier `aile_caboteur.yml`, TD 1) : ρ_air = 1,225 kg/m³ ; aile de 33 m de haut, AR = 3, pied posé sur le pont (z = −2,5 m, sommet à z = −35,5 m) ;
vent vrai 10,288 m/s, navire à 7,2016 m/s ; AWS = 12,558 m/s, AWA = 55,01° ; réglage 34,4°.

# Matériel

- **Ubuntu sous Windows (WSL)** et **CN-AeroModels v0.5.1** (binaire Linux), installés au TD 1 (sinon :
  `docs/00_PRE-VOL_Installation.md` du dépôt du TD, puis `python3 scripts/verifie_mon_install.py`).
- **Le dépôt du TD**, `~/TD-Propulsion-Velique` (à mettre à jour : `git pull`) : dossiers `cas/Cas-ENSM_aile-du-caboteur/` et
  `cas/exemples/1- 2D model/`.
- Un éditeur de texte (pour modifier une copie du fichier `.yml`), un tableur ou Python pour le tracé d'A07, une
  calculatrice.

**Règle pour toutes les manipulations** : ne modifiez jamais le fichier d'origine. Copiez-le d'abord (par exemple
`cp aile_caboteur.yml essai.yml`), modifiez la copie, et lancez l'outil sur la copie, dans
le dossier du cas. Chaque lancement **écrase** `results.csv` : renommez-le avant de relancer s'il faut le garder.

# Manipulations pas à pas

## Manipulation 1 — Relancer le cas de l'aile du caboteur (pour A06)

> **Rappels du TD 1.** Pour ouvrir depuis Windows un fichier du dépôt (éditeur, tableur, ParaView), ne **retapez
> jamais** le chemin : dans le terminal Ubuntu, placez-vous dans le dossier voulu, tapez `wslpath -w .`, puis copiez
> l'adresse affichée (sélection à la souris, **Ctrl+Maj+C**) et collez-la. Un chemin retapé se trompe facilement d'une
> majuscule, et Linux distingue `Cas-ENSM` de `cas-ensm` : le fichier est alors « introuvable ». Dans ParaView, à
> *Load State*, le *Data Directory* est le **dossier du cas** (il se termine par `Cas-ENSM_aile-du-caboteur`).

```bash
cd ~/TD-Propulsion-Velique/cas/Cas-ENSM_aile-du-caboteur
CN-AeroModels aile_caboteur.yml
```

**Auto-contrôle (valeur de référence : sortie de l'outil v0.5.1 ; mêmes forces que le tutoriel 1 de la formation du LHEEA (deck S03, diapos 39 et 40) ; moments différents, l'aile étant posée sur le pont)** : à l'écran, **F_x = 45 015,9 N** et
**F_y = 34 203,7 N**. Comparez ensuite les colonnes `CL`, `CD`, `Cx` et `Cy` à vos calculs d'A06, question 1 (valeurs
absolues).

## Manipulation 2 — Le cas de l'aile du caboteur en ligne portante non linéaire (pour A06, question 3)

Dans `Cas-ENSM_aile-du-caboteur/`, copiez `aile_caboteur.yml` en `nll.yml`, puis, dans `nll.yml` :

1. remplacez la ligne `        model: strip theory` par les trois lignes suivantes (même indentation que la ligne
   remplacée, puis quatre espaces de plus) :

   ```yaml
           model: nonlinear lifting line
           options:
               useAWSsquare: false
               verbose: false
   ```

2. remplacez `number of elements: 3` par `number of elements: 10`.

Lancez :

```bash
CN-AeroModels nll.yml
```

Notez F_x et F_y de la ligne `Total`, C_L et C_D de la ligne de l'aile `WPU-1` (la ligne juste au-dessus de `Total`,
qui les laisse en `N/A`). L'incidence **effective** n'est pas à l'écran (la colonne `AoA/SR` de l'écran garde
l'incidence géométrique, −20,61°) : lisez la moyenne dans `results.csv`, colonne `AoA`, et l'incidence de chaque
élément dans `aile-caboteur_WPU-1_0000.csv`, colonne `AoA(degrees)/SR` (une ligne par élément, du pied au sommet ;
ce fichier est écrasé à chaque lancement, comme `results.csv` : lisez-le avant de relancer).
Recommencez avec `number of elements: 20`.

**Auto-contrôle** : l'outil doit rendre des efforts **non nuls**, et les F_x obtenus avec 10 et 20 éléments doivent
différer de **moins de 1 %** (`docs/00b_CA_NA_PAS_MARCHE.md` du dépôt du TD). Sinon, le calcul n'a pas convergé : revenez à 10 éléments et
vérifiez les deux remplacements.

## Manipulation 3 — Balayer le réglage (pour A07)

Dans `Cas-ENSM_aile-du-caboteur/`, copiez `aile_caboteur.yml` en `balayage.yml`. La ligne `setting`, à la fin du fichier, fixe le réglage :

```yaml
    setting: {unit: deg, values: [34.4, 34.4]}
```

Remplacez **les deux** valeurs 34.4 par le réglage voulu (par exemple `[40, 40]`), lancez
`CN-AeroModels balayage.yml`, notez F_x et F_y de la ligne `Total`, puis passez au réglage suivant. Le groupe se
partage les réglages de 0 à 80°, de 5° en 5°, et met les résultats en commun.

**Auto-contrôle** : avec `[34.4, 34.4]`, `balayage.yml` doit redonner exactement la sortie de la manipulation 1
(F_x = 45 015,9 N).

## Manipulation 4 — L'exemple 1 : une bande ou dix (pour A08)

```bash
cd ~/TD-Propulsion-Velique/cas/exemples/"1- 2D model"
CN-AeroModels 1_element.yml
CN-AeroModels 10_elements.yml
```

**Auto-contrôle (valeurs de l'énoncé d'A08, question 3)** : pour chacun des deux fichiers, à l'écran (ligne de la voile, au-dessus de `Total`),
**C_L = −0,9125**, **C_D = 0,01582**, **C_x = 0,9125**, **C_y = 0,01582**.

# Énoncés

## A05 — Facteur d'allongement · niveau 1

Calculer AR / (AR + 2) pour AR = 3, 4 et 7. Que perd une voile d'allongement 3 ?

## A06 — Efforts de l'aile du caboteur, et ce que la théorie des bandes ne corrige pas · niveau 2

**Objectif.** Refaire à la main le calcul de l'outil en théorie des bandes, et voir ce qu'il ne prend pas en compte.

Cas de l'aile du caboteur : profil NACA0015, hauteur 33 m, AR = 3, trois bandes, vent uniforme ; l'outil donne
C_L = −1,611 et C_D = 0,0629.

1. Calculer la surface, q, C_x, C_y, F_x, F_y et P_x = F_x · u. Puis faire la manipulation 1 et comparer.

2. Que représente ce P_x pour un moteur de 5 000 kW, et pourquoi n'est-ce **pas** l'économie au moteur ?
3. Le C_L de l'outil est celui de la table 2D (A04, TD 1). L'allongement de 3 a-t-il été pris en compte ? Que donnerait le
   facteur d'A05 ? Faire ensuite la manipulation 2 et comparer F_x, F_y et l'incidence des éléments à la théorie des
   bandes.

## A07 — Balayage du réglage · niveau 2

Dans les conditions du cas de l'aile du caboteur, faire varier le réglage μ de 0 à 80° (manipulation 3). Tracer F_x(μ) et F_y(μ).
Pour quel réglage la poussée est-elle maximale ? Est-ce celui de C_L,max ? Que vaut le gain par rapport au réglage de
34,4° du cas ?

Regardez aussi les colonnes `CL` et `CD` pour les petits réglages (μ ≤ 30°) : que remarquez-vous, et d'où cela
vient-il (A04, TD 1) ?

## A08 — Invariance par discrétisation · niveau 1

Exemple 1 du dépôt LHEEA (`exemples/1- 2D model/`, fichiers `1_element.yml` et `10_elements.yml`) : lancer avec 1 puis
10 éléments (manipulation 4).

1. Pourquoi C_L, C_D, C_x et C_y sont-ils identiques ?
2. Quel est l'intérêt d'augmenter le nombre d'éléments en NLL ou en ISILL ?
3. *(sans outil)* L'exemple 1 donne C_L = −0,9125, C_D = 0,01582, C_x = 0,9125, C_y = 0,01582. Quel angle de vent
   apparent ces quatre nombres impliquent-ils ?

# Question d'interprétation physique

En passant de la théorie des bandes à la NLL (manipulation 2), F_x et F_y ne baissent pas dans la même proportion.
Lequel des deux baisse le plus ? En vous aidant de la colonne `AoA/SR` (incidence de chaque élément) et des formules
de C_x et C_y, expliquez pourquoi l'incidence induite par les tourbillons pénalise surtout la poussée. Qu'en
concluez-vous sur l'usage de la théorie des bandes pour estimer le gain de puissance d'un navire ?

# Ce qu'il faut rendre

Un compte rendu (une à deux pages), selon les consignes de dépôt données par l'enseignant, avec :

1. les réponses d'A05, A06, A07 et A08, **calculs posés** et unités ;
2. le tracé F_x(μ) et F_y(μ) d'A07 (tableur ou Python), avec le réglage de poussée maximale ;
3. le tableau des sorties de la manipulation 2 (10 et 20 éléments : F_x, F_y, C_L, C_D) et votre comparaison avec la
   théorie des bandes ; ou, si l'outil n'a pas pu tourner, la panne rencontrée et le message d'erreur ;
4. votre réponse à la question d'interprétation, en cinq lignes au plus.

# Sources

- LHEEA (Centrale Nantes / CNRS), support de formation *CN-AeroModels Training* (LH), p. 21-27.

- CN-AeroModels v0.5.1, A. Babarit et M. Charlou, LHEEA, <https://gitlab.com/lheea/CN-AeroModels> (EPL 2.0) ; fichiers
  `airfoil_data/NACA0015_v2.yml`, exemple 1 (`1_element.yml`, `10_elements.yml`).
- Cas de l'aile du caboteur, `cas/Cas-ENSM_aile-du-caboteur/aile_caboteur.yml` (ENSM, construit sur l'exemple 1) ;
  mêmes forces que le tutoriel 1 de la formation du LHEEA ; moments différents, l'aile étant posée sur le pont.
- Support d'exercices CN-AeroModels de l'ENSM : document interne, non distribué ; les valeurs d'A08, question 3 en
  viennent (ce sont celles de l'exemple 1).

- Cours EGN-S7 du 23/11, deck S03 « Aérodynamique et passage au TD » (Vega), diapos 17 à 31.
- Banque d'exercices EGN-S7, exercices A05 à A08 ; dépôt public du TD, `TD-Propulsion-Velique`.
