# TD 1 — Aérodynamique avec CN-AeroModels · fiche élève

**EGN-S7 Propulsion assistée par le vent · séance de TD S1 · durée 2 h.** Prérequis : le cours du matin (S7-01,
§ 5.1 à 5.3 : vent apparent, profil 2D, passage à l'aile 3D ; support sur Vega). Cette fiche est aussi dans le
dépôt public du TD, `docs/TD-S1_Aerodynamique.md` : <https://github.com/ChrisVhk/TD-Propulsion-Velique>.

Les exercices sont tirés de la banque d'exercices d'EGN-S7 (A01 à A04). Chaque exercice porte son **niveau** :
**niveau 1**, application directe d'une définition ou d'une formule ; **niveau 2**, enchaînement de plusieurs étapes
ou lecture critique d'une source.

# Objectifs

À la fin de la séance, vous savez :

- calculer un vent apparent (vitesse AWS et angle AWA) à partir du vent vrai et de la vitesse du navire (A01, niveau 1) ;
- lire la convention de direction du vent d'un fichier d'entrée de CN-AeroModels, et ne pas la lire à l'envers (A02,
  niveau 1) ;
- évaluer le nombre de Reynolds d'une voile de cargo et dire ce qu'il implique pour l'usage d'une table de profil (A03,
  niveau 1) ;
- lire une table de profil réelle : maximum de portance, décrochage, finesse, effet du nombre de Reynolds, et la façon
  dont l'outil l'interpole (A04, niveau 2) ;
- installer CN-AeroModels et vérifier votre installation sur deux cas dont le résultat est connu.

# Vos armes : les formules utiles (cours S7-01, § 5)

**Vent apparent** (S7-01 § 5.1). Le vent apparent est le vent vrai moins la vitesse du navire :
V_app = V_vrai − V_navire. Avec TWA compté depuis l'avant du navire (0° : vent debout) et BS la vitesse du navire :

- AWS² = TWS² + BS² + 2 · TWS · BS · cos TWA ;
- tan AWA = TWS · sin TWA / (TWS · cos TWA + BS).

Cas limites : vent debout, AWS = TWS + BS ; vent arrière, AWS = |TWS − BS|.

**Convention de l'outil** (S7-01 § 5.1). Le fichier d'entrée donne la direction **vers laquelle** le vent souffle,
dans le repère NED (nord, est, bas) : β = 180° + TWD, où TWD est la direction **d'où** vient le vent.

**Angle d'attaque** (S7-01 § 5.1 et § 5.4). Pour une unité vélique, l'angle d'attaque AoA est l'angle de vent
apparent corrigé du réglage m de l'aile : AoA = AWA + m, avec les angles signés de l'outil.

**Profil 2D** (S7-01 § 5.2). Pour un profil de corde c dans un écoulement de vitesse V, par unité d'envergure :

- L = ½ ρ C_L(α, Re) c V² et D = ½ ρ C_D(α, Re) c V² ;
- Re = ρ V c / μ = V c / ν ;
- finesse : C_L / C_D.

**Données communes** (fichier `aile_caboteur.yml`) : ρ_air = 1,225 kg/m³ ; ν_air = 1,48 · 10⁻⁵ m²/s.
14 nœuds = 7,2016 m/s ; 20 nœuds = 10,288 m/s.

# Matériel

Tout se fait dans **Ubuntu sous Windows (WSL)**, dans le terminal Ubuntu.

- **Le dépôt du TD**, `TD-Propulsion-Velique` (public, GitHub) : la fiche de chaque séance (`docs/`), les scripts
  d'installation et de tracé (`scripts/`), et les fichiers d'entrée des cas de l'outil (`cas/`).
- **L'outil CN-AeroModels, version v0.5.1, binaire Linux** (LHEEA, Centrale Nantes / CNRS ; licence Eclipse Public
  License 2.0). Le script `scripts/installer_cnaero.sh` le télécharge sur la page *Releases* officielle,
  <https://gitlab.com/lheea/CN-AeroModels/-/releases>, et l'installe ; l'enseignant ne redistribue pas le binaire.
- **Python 3** avec les modules `yaml` et `matplotlib` (installés par le même script), ou à défaut un tableur.
- Une calculatrice.

**Déroulé de la séance.** De 0:00 à 0:40, un membre du binôme installe (manipulations 0 et 1) pendant que l'autre
commence A01 et A02 à la main ; puis, jusqu'à 2:00, A03, A04 et le tracé de la table (manipulations 2 et 3). Si
l'installation coince, continuez les exercices : ils se font tous sans l'outil.

# Manipulations pas à pas

## Manipulation 0 — Installer l'environnement et l'outil

Suivez `docs/00_PRE-VOL_Installation.md` du dépôt du TD. En résumé :

1. **WSL et Ubuntu** : par le script du cours d'informatique appliquée S5 (dépôt public
   `Informatique-Appliquee-S5`, `scripts/installer_poste.ps1`), expliqué dans le pré-vol. Si Ubuntu est déjà installé
   sur votre poste, passez à l'étape 2.
2. **Le dépôt du TD**, dans le terminal Ubuntu :

   ```bash
   cd ~
   git clone https://github.com/ChrisVhk/TD-Propulsion-Velique.git
   cd TD-Propulsion-Velique
   ```

3. **CN-AeroModels et les modules Python** :

   ```bash
   bash scripts/installer_cnaero.sh
   source ~/.bashrc
   ```

**Auto-contrôle** : lancé sans argument, l'outil doit répondre `Please specify an input file` :

```bash
CN-AeroModels
```

## Manipulation 1 — Vérifier l'installation sur l'aile elliptique

Depuis le dossier du dépôt :

```bash
python3 scripts/verifie_mon_install.py
```

Le script lance l'outil sur l'aile elliptique (`cas/exemples/2- nonlinear lifting line/elliptic.yml`) et compare le
résultat à la valeur de référence, C_L = 0,3655 (sortie de l'outil v0.5.1 pour cette aile, accord avec la
théorie de Prandtl).

**Auto-contrôle (valeur de référence)** : la ligne `[ OK ] aile elliptique : C_L = 0.3655` et le message « Tout est prêt
pour le TD ». Sinon, voir `docs/00b_CA_NA_PAS_MARCHE.md`, et renvoyez le bloc encadré à l'enseignant.

## Manipulation 2 — Lancer le cas de l'aile du caboteur (après l'exercice A02)

Faire d'abord l'exercice A02 à la main, puis :

```bash
cd ~/TD-Propulsion-Velique/cas/Cas-ENSM_aile-du-caboteur
CN-AeroModels aile_caboteur.yml
```

Toujours **se placer dans le dossier du cas** : l'outil écrit ses sorties dans le dossier courant, et le cas lit
sa table de profil par un chemin relatif à ce dossier (`../exemples/airfoil_data/NACA0015_v2.yml`). Mettre des guillemets autour des noms qui contiennent des espaces.

**Auto-contrôle (valeur de référence : sortie de l'outil v0.5.1 ; le LHEEA donne le même résultat pour un cas voisin de sa formation, LH p. 25)** : à l'écran, **F_x = 45 015,9 N** et **F_y = 34 203,7 N** ; dans
`results.csv`, **45,0159** et **34,2037 kN** (le fichier donne les efforts en kN, l'écran en N). Comparez ensuite
les colonnes `AWS`, `AWA` et `AoA/SR` de l'écran à vos réponses de l'exercice A02 : les signes suivent les conventions
de l'outil, comparez des valeurs absolues.

## Manipulation 3 — Tracer la table de coefficients du profil (pour A04)

Le fichier `cas/exemples/airfoil_data/NACA0015_v2.yml` est la table de profil que l'outil utilise pour le cas de l'aile du caboteur. Ouvrez-le dans un éditeur de
texte : il commence par le nom du profil (`type: NACA0015`), puis donne, **pour chaque nombre de Reynolds** (`Re`), la
liste des angles d'attaque (`AoA`, en degrés), des coefficients de portance (`lift coefficient`) et de traînée
(`drag coefficient`). Le commentaire en fin de ligne `Re` indique l'origine des valeurs (`xfoil` ou `CFD`).

Depuis le dossier du dépôt :

```bash
cd ~/TD-Propulsion-Velique
python3 scripts/tracer_table.py
```

Le script (à lire : une trentaine de lignes) trace C_L(AoA) et la finesse C_L/C_D, une courbe par nombre de Reynolds.

**Auto-contrôle** : le script affiche `7 tables tracées` (sept nombres de Reynolds, de 5 · 10⁴ à 1,5 · 10⁷, comme
l'annonce l'énoncé d'A04) et écrit `table_NACA0015_v2.png` ; le profil est symétrique, donc chaque courbe de C_L part de
C_L ≈ 0 à AoA = 0°. Sans Python : copiez les listes d'un ou deux nombres de Reynolds dans un tableur et tracez-les.

# Énoncés

## A01 — Vent apparent d'un cargo · niveau 1

**Objectif.** Calculer un vent apparent dans le repère navire (S7-01 § 5.1).

1. Nommer WPS, WPU, TWD, TWS, TWA, AWA, AWS, AoA et SR (LH p. 5-7).
2. Un navire fait route au 000° à 14 nœuds (7,2016 m/s). Le vent vrai **vient du** 045° à 20 nœuds (10,288 m/s).
   Calculer le vent apparent en composantes, puis AWS et AWA.

## A02 — Le vent du cas de l'aile du caboteur : d'où vient-il ? · niveau 1

**Objectif.** Lire la convention NED d'un fichier d'entrée (`aile_caboteur.yml` : `direction: 90`).

Le cas de l'aile du caboteur (`cas/Cas-ENSM_aile-du-caboteur/aile_caboteur.yml`) donne un vent uniforme de 10,288 m/s, de direction 90° (NED), et un navire au cap 000° à
7,2016 m/s ; le réglage de l'aile est de 34,4°.

a) D'où vient le vent ?
b) Calculer TWA, AWS et AWA.
c) Calculer l'angle d'attaque.

Puis faire la manipulation 2 et comparer.

## A03 — Reynolds d'une voile de cargo · niveau 1

Calculer le nombre de Reynolds d'une voile de corde 11 m sous 12 m/s de vent apparent, puis sous l'AWS du cas de l'aile du caboteur.
Que conclure pour l'usage de tables de profils mesurées à Re = 10⁵ à 10⁶ ?

## A04 — Lire une table de profil : décrochage, finesse, effet de Re · niveau 2 (questions 1 et 2)

**Objectif.** Lire C_L(AoA) et C_L/C_D sur une table réelle ; voir l'effet de Re ; voir comment une table se lit et
s'interpole.

La table `NACA0015_v2.yml` du cas de l'aile du caboteur donne C_L et C_D pour sept nombres de Reynolds, de 5 · 10⁴ à 1,5 · 10⁷ (XFOIL
jusqu'à 10⁶, CFD au-delà, d'après les commentaires du fichier). Appuyez-vous sur votre tracé (manipulation 3) et sur
les valeurs du fichier.

1. Pour chaque Re, relever C_L,max et son angle, ainsi que la finesse maximale et son angle.
2. À AoA = 20,61° et Re = 9,33 · 10⁶ (le cas de l'aile du caboteur), interpoler C_L et C_D entre les tables à 3,2 · 10⁶ et 1,5 · 10⁷,
   linéairement en Re puis linéairement en log Re. Laquelle des deux retrouve la sortie de l'outil (C_L = 1,611,
   C_D = 0,0629) ?

   *AoA = 20,61° et Re = 9,33 · 10⁶ sont donnés par l'énoncé : valeurs à comparer à vos réponses d'A02 c) et d'A03.*

# Question d'interprétation physique

Placez sur votre tracé le point de fonctionnement de l'aile du caboteur (AoA = 20,61°, Re = 9,33 · 10⁶, entre les
courbes à 3,2 · 10⁶ et à 1,5 · 10⁷). Ce point est-il avant ou après le maximum de portance de chacune de ces deux
courbes ? Qu'en concluez-vous sur la confiance à accorder à l'effort que l'outil calcule pour cette aile, et sur ce
qu'il faudrait vérifier avant de s'y fier pour une aile réelle ?

# Ce qu'il faut rendre

Un compte rendu (une à deux pages), selon les consignes de dépôt données par l'enseignant, avec :

1. les réponses d'A01, A02, A03 et A04 (questions 1 et 2), **calculs posés** et unités ;
2. le tracé `table_NACA0015_v2.png` (ou celui du tableur) ;
3. une copie d'écran des deux auto-contrôles (manipulations 1 et 2), ou, si l'outil n'a pas pu être installé, la
   panne rencontrée et le message d'erreur ;
4. votre réponse à la question d'interprétation, en cinq lignes au plus.

# Sources

- LHEEA (Centrale Nantes / CNRS), support de formation *CN-AeroModels Training* (LH), p. 5-9, 21-26.
- CN-AeroModels v0.5.1, A. Babarit et M. Charlou, LHEEA, <https://gitlab.com/lheea/CN-AeroModels> (EPL 2.0) ; fichiers
  `1_element.yml` de l'exemple 1 (point de départ du cas de l'aile du caboteur), `airfoil_data/NACA0015_v2.yml`,
  `elliptic.yml` de l'exemple 2.
- Cas de l'aile du caboteur, `cas/Cas-ENSM_aile-du-caboteur/aile_caboteur.yml` (ENSM) ; le LHEEA propose un cas
  voisin dans sa formation.
- Cours EGN-S7, S7-01 « Technologies et systèmes de propulsion vélique », § 5.
- Banque d'exercices EGN-S7, exercices A01 à A04 ; dépôt public du TD, `TD-Propulsion-Velique` (pré-vol, scripts,
  cas).
