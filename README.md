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
| élève, en séance | la fiche de la séance dans `docs/` (TD 1 : [`docs/TD-S1_Aerodynamique.md`](docs/TD-S1_Aerodynamique.md) ; les suivantes sont publiées au fil des séances) |
| enseignant / curieux | [`docs/01_PROGRAMME.md`](docs/01_PROGRAMME.md) |

## Structure

```
TD-Propulsion-Velique/
├── docs/     — 00 pré-vol · 00b dépannage · 01 programme · une fiche par séance (TD-S1, puis les suivantes)
├── scripts/  — installer_cnaero.sh (outil + Python) · verifie_mon_install.py (vérification) · test_valeurs_connues.py (C_L elliptique, F_x cas ENSM) · tracer_table.py
└── cas/      — fichiers d'entrée de CN-AeroModels : Cas-ENSM_aile-du-caboteur/ (cas ENSM), exemples/ (dépôt LHEEA) ; EPL 2.0
```

## Rien de sensible

Dépôt **public**. Aucune donnée nominative, aucun corrigé, aucun extrait de support sous droits. Les énoncés qui
s'appuient sur des supports de formation non libres sont distribués sur Vega. Provenance des fichiers :
[`PROVENANCE.md`](PROVENANCE.md). Licences : code sous Apache 2.0 ([`LICENSE`](LICENSE)), textes sous CC BY 4.0
([`LICENSE-docs`](LICENSE-docs)), fichiers de `cas/` sous EPL 2.0 ([`cas/LICENSE_CN-AeroModels.txt`](cas/LICENSE_CN-AeroModels.txt)).
