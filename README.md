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
│       └── TD2_envergure-paraview.png    figure de la fiche du TD 2
├── scripts/
│   ├── installer_cnaero.sh               installe CN-AeroModels et les modules Python
│   ├── verifie_mon_install.py            vérification à renvoyer (pré-vol, étape ④)
│   ├── test_valeurs_connues.py           C_L de l'aile elliptique, F_x de l'aile du caboteur
│   ├── tracer_table.py                   trace une table de profil
│   ├── TD1_voir_cas.py                   TD 1 : vue ParaView du cas (repli de TD1_vue.pvsm)
│   └── TD2_voir_envergure.py             TD 2 : vue ParaView le long de l'envergure (repli de TD2_envergure.pvsm)
├── TD3_rotor-et-interactions/            TD 3 : un dossier par manipulation ; sorties de calcul dans sorties/ (ignoré)
│   ├── manip1_rotor-sans-vent/           35x5_flettner.yml (= exemple 19), lancer.sh
│   ├── manip2-3_rotor-plaques/           2008_Badalamenti.yml et data.csv (= exemple 7), lancer.sh
│   ├── manip4-6_trois-ailes-15deg/       trois ailes au près : trois-ailes-15deg.yml (exemple 9, réglages du cas à 15°),
│   │                                     voile-N-seule.yml, lancer.sh, vue.pvsm, voir_sans-paraview.py, vue-attendue.png
│   ├── variante_trois-ailes-fichier-LHEEA/  trois-ailes.yml (= exemple 9 tel que fourni), lancer.sh
│   ├── variante_dynarig-reglage-mat-arriere/  V-DynaRig : régler le mât arrière (lancer.sh RÉGLAGE)
│   └── demo_dynarig-greenpeace/          démonstration : deux DynaRigs d'école (polaire d'école, hypothèses), coque
│                                         générique, lancer.sh, vue.pvsm, voir_sans-paraview.py, fardage.py
└── cas/
    ├── LICENSE_CN-AeroModels.txt         EPL 2.0
    ├── aile-caboteur/                    le cas ENSM : aile posée sur le pont du caboteur
    │   ├── aile-caboteur.yml             fichier d'entrée de CN-AeroModels
    │   ├── caboteur-serie60.vtk          coque du navire (Série 60), pour la vue
    │   ├── TD1_vue.pvsm                  TD 1 : état ParaView, à côté des .vtk que l'outil écrit ici
    │   └── TD2_envergure/
    │       ├── lancer_les_trois.sh       TD 2 : les trois calculs (bandes, NLL pied libre, NLL pont)
    │       └── TD2_envergure.pvsm        TD 2 : état ParaView le long de l'envergure
    └── exemples/                         exemples du dépôt de CN-AeroModels (LHEEA), noms d'origine
```

## Rien de sensible

Dépôt **public**. Aucune donnée nominative, aucun corrigé, aucun extrait de support sous droits. Les énoncés qui
s'appuient sur des supports de formation non libres sont distribués sur Vega. Provenance des fichiers :
[`PROVENANCE.md`](PROVENANCE.md). Licences, la règle : fichiers d'entrée de CN-AeroModels issus du LHEEA (et ceux qui en dérivent, dont
`aile-caboteur.yml`) : EPL 2.0 ([`cas/LICENSE_CN-AeroModels.txt`](cas/LICENSE_CN-AeroModels.txt)) ; fichiers faits
à l'ENSM (coque du caboteur, états ParaView, scripts) : Apache 2.0 ([`LICENSE`](LICENSE)) ; textes : CC BY 4.0
([`LICENSE-docs`](LICENSE-docs)). Le détail, fichier par fichier : [`PROVENANCE.md`](PROVENANCE.md).
