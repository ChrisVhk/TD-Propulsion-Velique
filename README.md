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
│   ├── TD-S3_Rotor-et-interactions.md    fiche du TD 3
│   └── img/
│       ├── TD1_vue-paraview.png          figure de la fiche du TD 1
│       ├── TD2_envergure-paraview.png    figure de la fiche du TD 2
│       └── TD3_trois-ailes-paraview.png  figure de la fiche du TD 3
├── scripts/
│   ├── installer_cnaero.sh               installe CN-AeroModels et les modules Python
│   ├── verifie_mon_install.py            vérification à renvoyer (pré-vol, étape ④)
│   ├── test_valeurs_connues.py           C_L de l'aile elliptique, F_x de l'aile du caboteur
│   ├── tracer_table.py                   trace une table de profil
│   ├── TD1_voir_cas.py                   TD 1 : vue ParaView du cas (repli de TD1_vue.pvsm)
│   ├── TD2_voir_envergure.py             TD 2 : vue ParaView le long de l'envergure (repli de TD2_envergure.pvsm)
│   └── TD3_voir_trois-ailes.py           TD 3 : vue ParaView des trois ailes (repli de TD3_trois-ailes.pvsm)
└── cas/
    ├── LICENSE_CN-AeroModels.txt         EPL 2.0
    ├── aile-caboteur/                    le cas ENSM : aile posée sur le pont du caboteur
    │   ├── aile-caboteur.yml             fichier d'entrée de CN-AeroModels
    │   ├── caboteur-serie60.vtk          coque du navire (Série 60), pour la vue
    │   ├── TD1_vue.pvsm                  TD 1 : état ParaView, à côté des .vtk que l'outil écrit ici
    │   └── TD2_envergure/
    │       ├── lancer_les_trois.sh       TD 2 : les trois calculs (bandes, NLL pied libre, NLL pont)
    │       └── TD2_envergure.pvsm        TD 2 : état ParaView le long de l'envergure
    ├── trois-ailes/                      TD 3 : les trois ailes de Malmek (exemple 9 du LHEEA, copie à l'identique)
    │   ├── trois-ailes.yml               fichier d'entrée (= exemples/9- 2020 Malmek/2023_Malmek_3sails.yml)
    │   ├── TD3_lancer_les_deux.sh        TD 3 : NLL et théorie des bandes, sorties pour ParaView
    │   └── TD3_trois-ailes.pvsm          TD 3 : état ParaView des trois ailes
    └── exemples/                         exemples du dépôt de CN-AeroModels (LHEEA), noms d'origine
```

## Rien de sensible

Dépôt **public**. Aucune donnée nominative, aucun corrigé, aucun extrait de support sous droits. Les énoncés qui
s'appuient sur des supports de formation non libres sont distribués sur Vega. Provenance des fichiers :
[`PROVENANCE.md`](PROVENANCE.md). Licences, la règle : fichiers d'entrée de CN-AeroModels issus du LHEEA (et ceux qui en dérivent, dont
`aile-caboteur.yml`) : EPL 2.0 ([`cas/LICENSE_CN-AeroModels.txt`](cas/LICENSE_CN-AeroModels.txt)) ; fichiers faits
à l'ENSM (coque du caboteur, états ParaView, scripts) : Apache 2.0 ([`LICENSE`](LICENSE)) ; textes : CC BY 4.0
([`LICENSE-docs`](LICENSE-docs)). Le détail, fichier par fichier : [`PROVENANCE.md`](PROVENANCE.md).
