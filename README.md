# TD Propulsion vélique — EGN-S7 (ENSM Génie Maritime)

Travaux dirigés de l'unité **EGN-S7 « Propulsion assistée par le vent »** : 12 h en sept séances, en **binômes**.
On calcule les efforts d'une aile ou d'un rotor dans le vent apparent d'un navire, à la main puis avec l'outil libre
**CN-AeroModels** (LHEEA, Centrale Nantes / CNRS), dans **Ubuntu sous Windows (WSL)**.

La théorie est dans le **cours**, sur Vega. Ce dépôt contient le TD seulement : fiches, scripts, fichiers d'entrée.

## Par où commencer

| Vous êtes… | Lisez |
|---|---|
| élève, avant le TD 1 | [`docs/00_PRE-VOL_Installation.md`](docs/00_PRE-VOL_Installation.md), puis lancez `python3 scripts/verifie_mon_install.py` |
| élève, ça bloque | [`docs/00b_CA_NA_PAS_MARCHE.md`](docs/00b_CA_NA_PAS_MARCHE.md), et lancez `python3 scripts/test_valeurs_connues.py` : collez sa sortie dans votre message à l'enseignant |
| élève, en séance | la fiche de la séance dans `docs/` (TD 1 : [`docs/TD-S1_Aerodynamique.md`](docs/TD-S1_Aerodynamique.md) ; TD 2 : [`docs/TD-S2_Bandes-et-ligne-portante.md`](docs/TD-S2_Bandes-et-ligne-portante.md) ; TD 3 : [`docs/TD-S3_Rotor-et-interactions.md`](docs/TD-S3_Rotor-et-interactions.md) ; les suivantes sont publiées au fil des séances) |
| enseignant / curieux | [`docs/01_PROGRAMME.md`](docs/01_PROGRAMME.md) |

## Structure

Un dossier par TD, un sous-dossier par manipulation (numéros de la fiche) ; dans chacun, `lancer.sh` lance l'outil et
range ses sorties dans `sorties/` (ignoré par Git). Ce qui sert à plusieurs TD est dans `communs/`.

```
TD-Propulsion-Velique/
├── README.md
├── PROVENANCE.md                         origine et licence de chaque fichier
├── LICENSE                               Apache 2.0 (code et fichiers faits à l'ENSM)
├── LICENSE-docs                          CC BY 4.0 (textes)
├── docs/
│   ├── 00_PRE-VOL_Installation.md        à faire avant le TD 1
│   ├── 00b_CA_NA_PAS_MARCHE.md           dépannage
│   ├── 01_PROGRAMME.md                   les sept séances
│   ├── TD-S1_Aerodynamique.md            fiche du TD 1
│   ├── TD-S2_Bandes-et-ligne-portante.md fiche du TD 2
│   └── TD-S3_Rotor-et-interactions.md    fiche du TD 3
├── scripts/                              installation et vérifications (TD 1, manipulations 0 et 1)
│   ├── installer_cnaero.sh               installe CN-AeroModels et les modules Python
│   ├── verifie_mon_install.py            vérification à renvoyer (pré-vol, étape ④)
│   └── test_valeurs_connues.py           C_L de l'aile elliptique, F_x de l'aile du caboteur
├── communs/                              ce qui sert à plusieurs TD
│   ├── caboteur-serie60.vtk              coque du caboteur (Série 60), pour les vues ParaView ; construite par
│   │                                     construire_coque_serie60.py (table : serie60_cb065_table4.csv)
│   └── exemples-LHEEA/                   exemples du dépôt de CN-AeroModels (LHEEA), intacts, noms d'origine ;
│                                         LICENSE_CN-AeroModels.txt (EPL 2.0)
├── TD1_aerodynamique/
│   ├── manip2-et-3_aile-caboteur/        aile-caboteur.yml (le cas ENSM : aile posée sur le pont du caboteur),
│   │                                     lancer.sh, vue.pvsm, voir_sans-paraview.py, vue-attendue.png
│   └── manip4_table-de-profil/           tracer_table.py
├── TD2_bandes-et-ligne-portante/
│   ├── manip1-a-5_aile-caboteur/         aile-caboteur.yml (copie de celui du TD 1), lancer.sh (un calcul ; sans
│   │                                     fichier : les trois calculs de la manipulation 4), vue.pvsm,
│   │                                     voir_sans-paraview.py, vue-attendue.png
│   ├── manip6_une-bande-ou-dix/          lancer.sh (exemple 1 du LHEEA, lu dans communs/)
│   └── variante_graf-2014/               lancer.sh (V2 : votre copie de l'exemple 3)
└── TD3_rotor-et-interactions/
    ├── manip1_rotor-sans-vent/           35x5_flettner.yml (= exemple 19), lancer.sh
    ├── manip2-et-3_rotor-plaques/        2008_Badalamenti.yml et data.csv (= exemple 7), lancer.sh
    ├── manip4-a-6_trois-ailes-15deg/     trois ailes au près : trois-ailes-15deg.yml (exemple 9, réglages du cas à 15°),
    │                                     voile-N-seule.yml, lancer.sh, vue.pvsm, voir_sans-paraview.py, vue-attendue.png
    ├── variante_trois-ailes-fichier-LHEEA/  trois-ailes.yml (= exemple 9 tel que fourni), lancer.sh
    ├── variante_dynarig-reglage-mat-arriere/  V-DynaRig : régler le mât arrière (lancer.sh RÉGLAGE)
    └── demo_dynarig-greenpeace/          démonstration : deux DynaRigs d'école (polaire d'école, hypothèses) ; habillage
                                          (coque Série 60 à l'échelle, gréement) ; lancer.sh, vue.pvsm,
                                          voir_sans-paraview.py, fardage.py, README.md
```

## Rien de sensible

Dépôt **public**. Aucune donnée nominative, aucun corrigé, aucun extrait de support sous droits. Les énoncés qui
s'appuient sur des supports de formation non libres sont distribués sur Vega. Provenance des fichiers :
[`PROVENANCE.md`](PROVENANCE.md). Licences, la règle : fichiers d'entrée de CN-AeroModels issus du LHEEA (et ceux qui en dérivent, dont
`aile-caboteur.yml`) : EPL 2.0 ([`communs/exemples-LHEEA/LICENSE_CN-AeroModels.txt`](communs/exemples-LHEEA/LICENSE_CN-AeroModels.txt)) ; fichiers faits
à l'ENSM (coque du caboteur, états ParaView, scripts) : Apache 2.0 ([`LICENSE`](LICENSE)) ; textes : CC BY 4.0
([`LICENSE-docs`](LICENSE-docs)). Le détail, fichier par fichier : [`PROVENANCE.md`](PROVENANCE.md).
