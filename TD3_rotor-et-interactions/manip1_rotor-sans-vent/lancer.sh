#!/usr/bin/env bash
# TD 3 (EGN-S7, ENSM) : lancer CN-AeroModels sur un fichier de ce dossier, sorties rangées dans sorties/.
#
#   bash lancer.sh FICHIER.yml
#
# L'outil tourne dans sorties/ (ignoré par Git) ; tout ce qu'il affiche défile à l'écran, comme si vous l'aviez lancé
# vous-même, et reste dans sorties/FICHIER_ecran.txt (pour y chercher un message) ; son results.csv devient
# sorties/FICHIER_results.csv. Le fichier .yml n'est pas modifié.
set -u
ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTIL="$(command -v CN-AeroModels || echo "$HOME/outils/CN-AeroModels/bin/CN-AeroModels")"
[ -x "$OUTIL" ] || { echo "CN-AeroModels introuvable (TD 1 : bash scripts/installer_cnaero.sh)"; exit 1; }
[ $# -eq 1 ] || { echo "Usage : bash lancer.sh FICHIER.yml   (fichiers de ce dossier : $(cd "$ICI" && ls *.yml | tr '\n' ' '))"; exit 1; }
yml="$(basename "$1")"; nom="${yml%.yml}"
[ -f "$ICI/$yml" ] || { echo "Absent dans ce dossier : $yml"; exit 1; }
mkdir -p "$ICI/sorties" || exit 1
cd "$ICI/sorties" || exit 1
rm -f results.csv
"$OUTIL" "../$yml" 2>&1 | tee "${nom}_ecran.txt"
if [ -f results.csv ]; then
  mv -f results.csv "${nom}_results.csv"
  echo "Sorties : sorties/${nom}_ecran.txt (écran) et sorties/${nom}_results.csv"
else
  echo "L'outil n'a pas écrit results.csv : lisez la fin de sorties/${nom}_ecran.txt"; exit 1
fi
