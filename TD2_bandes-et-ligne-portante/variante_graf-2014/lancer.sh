#!/usr/bin/env bash
# TD 2 (EGN-S7, ENSM), variante V2 (A09) : votre copie de l'exemple 3 du LHEEA (Graf 2014), sorties dans sorties/.
#
#   cd ~/TD-Propulsion-Velique/TD2_bandes-et-ligne-portante/variante_graf-2014
#   cp "../../communs/exemples-LHEEA/3- 2014 Graf OENG/2014_Graf_OENG.yml" graf.yml
#   bash lancer.sh graf.yml
#
# L'exemple du LHEEA reste intact dans communs/ (ses mesures : data.csv, même dossier). L'outil tourne dans sorties/
# (ignoré par Git) ; tout ce qu'il affiche défile à l'écran et reste dans sorties/FICHIER_ecran.txt ; results.csv garde
# son nom (écrasé au lancement suivant).
set -u
ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTIL="$(command -v CN-AeroModels || echo "$HOME/outils/CN-AeroModels/bin/CN-AeroModels")"
[ -x "$OUTIL" ] || { echo "CN-AeroModels introuvable (TD 1 : bash scripts/installer_cnaero.sh)"; exit 1; }
[ $# -eq 1 ] || { echo "Usage : bash lancer.sh graf.yml   (après la copie : voir l'en-tête de ce script)"; exit 1; }
yml="$(basename "$1")"; nom="${yml%.yml}"
[ -f "$ICI/$yml" ] || { echo "Absent dans ce dossier : $yml (faites d'abord la copie : fiche du TD 2, variante V2)"; exit 1; }
mkdir -p "$ICI/sorties" && cd "$ICI/sorties" || exit 1
rm -f results.csv
"$OUTIL" "../$yml" 2>&1 | tee "${nom}_ecran.txt"
[ -f results.csv ] || { echo "L'outil n'a pas écrit results.csv : lisez la fin de sorties/${nom}_ecran.txt"; exit 1; }
echo "Sorties dans sorties/ : results.csv, ${nom}_ecran.txt (écran)."
