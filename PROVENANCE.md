# Provenance

## Logiciel appelé (non redistribué)

| Logiciel | Version | Licence | Usage |
|---|---|---|---|
| CN-AeroModels (A. Babarit, M. Charlou, LHEEA, Centrale Nantes / CNRS) | **v0.5.1**, binaire officiel `linux-x64` de la page Releases, <https://gitlab.com/lheea/CN-AeroModels/-/releases> | Eclipse Public License 2.0 | efforts aérodynamiques d'ailes, voiles et rotors ; téléchargé par `scripts/installer_cnaero.sh` depuis la page officielle ; **aucun binaire ni code de l'outil dans ce dépôt** |

## Fichiers d'entrée (`cas/`)

Fichiers d'entrée `.yml` et mesures `data.csv` des exemples du dépôt de CN-AeroModels
(<https://gitlab.com/lheea/CN-AeroModels>, copiés le 04/11/2026 de la branche `master`, f2ec386 = v0.5.1 + 7 commits
de documentation et de correctifs), **sans modification** (sauf `cas/Cas-ENSM_aile-du-caboteur/`, ci-dessous), sous la licence de l'outil, Eclipse Public License 2.0,
reproduite dans `cas/LICENSE_CN-AeroModels.txt`. Les `data.csv` sont les mesures publiées que le dépôt du LHEEA joint
à ses exemples 3, 7, 9 et 15.

| Dossier | Contenu |
|---|---|
| `cas/Cas-ENSM_aile-du-caboteur/` | `aile_caboteur.yml` : cas ENSM, construit sur l'exemple 1 de CN-AeroModels (`exemples/1- 2D model/1_element.yml`, EPL 2.0) : vent de 10,288 m/s (20 nœuds), direction 90°, navire à 7,2016 m/s (14 nœuds, le caboteur d'EGN-S9), aile NACA0015 de 33 m, AR = 3, réglage 34,4° ; table `exemples/airfoil_data/NACA0015_v2.yml`. Œuvre dérivée d'un fichier sous EPL 2.0, distribuée sous la même licence. Le LHEEA propose un cas voisin dans sa formation |
| `cas/exemples/` | exemples 1, 2, 3, 7, 9, 15, 17, 19 et `airfoil_data/` |
| `cas/Cas-ENSM_aile-du-caboteur/aile_caboteur.pvsm` | état ParaView de la vue du cas (aile colorée par C_L, efforts par bande, vent vrai, mer, repère NED), construit de zéro à l'ENSM le 22/11/2026 (pas de reprise de l'état `tutorial-1.pvsm` du LHEEA), avec la même fonction que `scripts/voir_aile_caboteur.py`, et enregistré par l'interface graphique de ParaView 6.1.1 pour Windows ; il ne contient aucune donnée, seulement les noms des quatre fichiers `.vtk` que l'outil écrit avec `--vtk 1` dans le même dossier et celui de la coque `caboteur_serie60.vtk` (session 11 i : le caboteur ajouté à la vue, mer semi-transparente ; état refait et testé dans l'interface de ParaView 6.1.1 et 6.2.1 pour Windows). Apache 2.0 |
| `cas/Cas-ENSM_aile-du-caboteur/caboteur_serie60.vtk` | coque du caboteur pour la vue ParaView (surface fermée, triangles, repère NED : étrave en x = +55 m, flottaison z = 0, pont z = −2,5 m, quille z = +6,5 m). Géométrie : **Série 60, carène mère C_B = 0,65** (modèle 4211W), table 4 des demi-largeurs (*Table of Offsets — Parent Forms — 0.65 Block Coefficient*, page V-8) de F. H. Todd, *Series 60 — Methodical experiments with models of single-screw merchant ships*, David Taylor Model Basin, Report 1712, juillet 1963, **domaine public** (scan Internet Archive `methodicalexperi00todd`, Biodiversity Heritage Library, DOI 10.5962/bhl.title.47452) ; relevée dans la couche texte du scan, deux erreurs d'OCR corrigées sur l'image de la page, contrôlée contre les coefficients publiés (table 2 du rapport) ; mise à l'échelle du caboteur d'EGN-S9 (L 110 m, B 17,5 m, T 6,5 m, D 9,0 m). Sans bulbe, comme la Série 60. Fichier construit à l'ENSM le 22/11/2026, Apache 2.0 ; ce n'est pas une sortie de l'outil (exception nommée dans `.gitignore`) |

## Exercices

Les énoncés des fiches viennent de la banque d'exercices d'EGN-S7 (ENSM, Christophe VANHORICK), construite sur le
support de formation *CN-AeroModels Training* du LHEEA (cité « LH », pages indiquées dans les fiches) et sur le cours
EGN-S7. Les énoncés qui s'appuient sur d'autres supports de formation, non libres, ne sont pas dans ce dépôt : ils
sont distribués sur Vega.

## Scripts

`scripts/voir_aile_caboteur.py` (ENSM) appelle ParaView (Kitware, <https://www.paraview.org>, licence BSD, non
redistribué) par son interpréteur `pvpython`. `scripts/verifie_mon_install.py` reprend la forme du script du même nom du dépôt public
<https://github.com/ChrisVhk/Informatique-Appliquee-S5> (ENSM) ; `scripts/tracer_table.py` lit le format de table de
profil de CN-AeroModels. Code sous Apache 2.0 (`LICENSE`), textes sous CC BY 4.0 (`LICENSE-docs`).
