#!/usr/bin/env bash
# TD 1 (EGN-S7, ENSM), manipulations 2 et 3 : lancer CN-AeroModels sur le cas de l'aile du caboteur, sorties dans sorties/.
#
#   cd ~/TD-Propulsion-Velique/TD1_aerodynamique/manip2-et-3_aile-caboteur
#   bash lancer.sh aile-caboteur.yml            # manipulation 2
#   bash lancer.sh aile-caboteur.yml --vtk 1    # manipulation 3 : en plus, les fichiers .vtk pour ParaView
#
# L'outil tourne dans sorties/ (ignoré par Git) : tout ce qu'il affiche défile à l'écran, comme si vous l'aviez lancé
# vous-même, et reste dans sorties/FICHIER_ecran.txt ; ses fichiers gardent leur nom (results.csv,
# aile-caboteur_WPU-1_0000.csv et, avec --vtk 1, les .vtk) et sont écrasés au lancement suivant. La table de profil se
# lit par un chemin relatif au dossier où tourne l'outil (../../../communs/exemples-LHEEA/airfoil_data/). Avec --vtk 1,
# la coque du caboteur (communs/caboteur-serie60.vtk, une donnée, pas une sortie de l'outil) est copiée dans sorties/,
# à côté des .vtk de l'outil, pour l'état vue.pvsm. Le fichier .yml n'est pas modifié.
set -u
ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMUNS="$ICI/../../communs"
OUTIL="$(command -v CN-AeroModels || echo "$HOME/outils/CN-AeroModels/bin/CN-AeroModels")"
[ -x "$OUTIL" ] || { echo "CN-AeroModels introuvable (manipulation 0 : bash scripts/installer_cnaero.sh)"; exit 1; }
[ $# -ge 1 ] || { echo "Usage : bash lancer.sh FICHIER.yml [--vtk 1]   (fichiers de ce dossier : $(cd "$ICI" && ls *.yml | tr '\n' ' '))"; exit 1; }
yml="$(basename "$1")"; nom="${yml%.yml}"; shift
[ -f "$ICI/$yml" ] || { echo "Absent dans ce dossier : $yml"; exit 1; }
if grep -q "file: \.\./exemples/airfoil_data/" "$ICI/$yml"; then
  echo "$yml lit la table de profil à l'ancien chemin (../exemples/airfoil_data/, avant le rangement du 26/11). Corrigez-le, dans ce dossier :"
  echo "   sed -i 's#\.\./exemples/airfoil_data/#../../../communs/exemples-LHEEA/airfoil_data/#' $yml"; exit 1
fi
mkdir -p "$ICI/sorties" || exit 1
cd "$ICI/sorties" || exit 1
rm -f results.csv
"$OUTIL" "../$yml" "$@" 2>&1 | tee "${nom}_ecran.txt"
[ -f results.csv ] || { echo "L'outil n'a pas écrit results.csv : lisez la fin de sorties/${nom}_ecran.txt"; exit 1; }
case " $* " in *" --vtk "*) cp -f "$COMMUNS/caboteur-serie60.vtk" . ;; esac
echo "Sorties dans sorties/ : results.csv, ${nom}_ecran.txt (écran) et les autres fichiers de l'outil (ls sorties)."
