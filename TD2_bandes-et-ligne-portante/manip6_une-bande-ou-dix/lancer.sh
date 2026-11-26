#!/usr/bin/env bash
# TD 2 (EGN-S7, ENSM), manipulation 6 : l'exemple 1 du LHEEA, une bande ou dix (pour A08), sorties dans sorties/.
#
#   cd ~/TD-Propulsion-Velique/TD2_bandes-et-ligne-portante/manip6_une-bande-ou-dix
#   bash lancer.sh 1_element.yml
#   bash lancer.sh 10_elements.yml
#
# Les deux fichiers sont ceux de l'exemple 1 du LHEEA, lus là où ils sont, sans copie ni modification :
# communs/exemples-LHEEA/1- 2D model/. L'outil tourne dans sorties/ (ignoré par Git) ; tout ce qu'il affiche défile
# à l'écran et reste dans sorties/FICHIER_ecran.txt ; results.csv garde son nom (écrasé au lancement suivant).
set -u
ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EX="$ICI/../../communs/exemples-LHEEA/1- 2D model"
OUTIL="$(command -v CN-AeroModels || echo "$HOME/outils/CN-AeroModels/bin/CN-AeroModels")"
[ -x "$OUTIL" ] || { echo "CN-AeroModels introuvable (TD 1 : bash scripts/installer_cnaero.sh)"; exit 1; }
[ $# -eq 1 ] || { echo "Usage : bash lancer.sh 1_element.yml   ou   bash lancer.sh 10_elements.yml"; exit 1; }
yml="$(basename "$1")"; nom="${yml%.yml}"
[ -f "$EX/$yml" ] || { echo "Absent de l'exemple 1 : $yml (fichiers : $(cd "$EX" && ls *.yml | tr '\n' ' '))"; exit 1; }
mkdir -p "$ICI/sorties" && cd "$ICI/sorties" || exit 1
rm -f results.csv
"$OUTIL" "$EX/$yml" 2>&1 | tee "${nom}_ecran.txt"
[ -f results.csv ] || { echo "L'outil n'a pas écrit results.csv : lisez la fin de sorties/${nom}_ecran.txt"; exit 1; }
echo "Sorties dans sorties/ : results.csv, ${nom}_ecran.txt (écran)."
