#!/usr/bin/env bash
# TD 2 (EGN-S7, ENSM), manipulations 1 à 5 : le cas de l'aile du caboteur et vos copies, sorties dans sorties/.
#
#   cd ~/TD-Propulsion-Velique/TD2_bandes-et-ligne-portante/manip1-a-5_aile-caboteur
#   bash lancer.sh aile-caboteur.yml     # manipulations 1, 2, 3 et 5 : un calcul (nll.yml, pont.yml, balayage.yml…)
#   bash lancer.sh                       # manipulation 4 : les trois calculs pour ParaView, puis vue.pvsm
#
# Un calcul (avec un fichier) : l'outil tourne dans sorties/ (ignoré par Git) ; tout ce qu'il affiche défile à l'écran
# et reste dans sorties/FICHIER_ecran.txt ; ses fichiers gardent leur nom (results.csv, aile-caboteur_WPU-1_0000.csv)
# et sont écrasés au lancement suivant. La table de profil se lit par un chemin relatif au dossier où tourne l'outil
# (../../../communs/exemples-LHEEA/airfoil_data/).
#
# Les trois calculs (sans argument, manipulation 4) : ils écrivent des fichiers de même nom (aile-caboteur_WPU-1_*) ;
# on les lance l'un après l'autre dans un dossier de calcul temporaire, au niveau de sorties/ (la table de profil se lit
# depuis le dossier courant), et on range dans sorties/ les sorties renommées par modèle. Fichiers lus (ce dossier,
# non modifiés) :
#   aile-caboteur.yml  théorie des bandes (manipulation 1)             -> sorties/bandes_*
#   nll.yml            NLL, pied libre, 20 éléments (manipulation 2)    -> sorties/nll_pied-libre_*
#   pont.yml           NLL, pont en miroir, 20 éléments (manipulation 3) -> sorties/nll_pont_* (aile image : nll_pont_mirror.vtk)
# (.vtk pour ParaView ; _elements.csv par élément ; _results.csv), puis vue.pvsm s'ouvre dans ParaView (File > Load State).
set -u
ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTIL="$(command -v CN-AeroModels || echo "$HOME/outils/CN-AeroModels/bin/CN-AeroModels")"
[ -x "$OUTIL" ] || { echo "CN-AeroModels introuvable (TD 1 : bash scripts/installer_cnaero.sh)"; exit 1; }
mkdir -p "$ICI/sorties" || exit 1
S="$ICI/sorties"

if [ $# -ge 1 ]; then   # ---- un calcul ----
  yml="$(basename "$1")"; nom="${yml%.yml}"; shift
  [ -f "$ICI/$yml" ] || { echo "Absent dans ce dossier : $yml (fichiers : $(cd "$ICI" && ls *.yml | tr '\n' ' '))"; exit 1; }
  if grep -q "file: \.\./exemples/airfoil_data/" "$ICI/$yml"; then
    echo "$yml lit la table de profil à l'ancien chemin (../exemples/airfoil_data/, avant le rangement du 26/11). Corrigez-le, dans ce dossier :"
    echo "   sed -i 's#\.\./exemples/airfoil_data/#../../../communs/exemples-LHEEA/airfoil_data/#' $yml"; exit 1
  fi
  cd "$S" || exit 1
  rm -f results.csv
  "$OUTIL" "../$yml" "$@" 2>&1 | tee "${nom}_ecran.txt"
  [ -f results.csv ] || { echo "L'outil n'a pas écrit results.csv : lisez la fin de sorties/${nom}_ecran.txt"; exit 1; }
  echo "Sorties dans sorties/ : results.csv, aile-caboteur_WPU-1_0000.csv, ${nom}_ecran.txt (écran)."
  exit 0
fi

# ---- les trois calculs (manipulation 4) ----
cd "$ICI" || exit 1
for f in aile-caboteur.yml nll.yml pont.yml; do
  [ -f "$ICI/$f" ] || { echo "Absent : $f (faites d'abord les manipulations 2 et 3)"; exit 1; }
done
grep -q "number of elements: 20" "$ICI/nll.yml"  || { echo "nll.yml doit être à 20 éléments (fin de la manipulation 2)"; exit 1; }
grep -q "number of elements: 20" "$ICI/pont.yml" || { echo "pont.yml doit être à 20 éléments (manipulation 3)"; exit 1; }
grep -q "plane of symmetry" "$ICI/pont.yml"      || { echo "pont.yml n'a pas de bloc plane of symmetry (manipulation 3)"; exit 1; }
for yml in nll.yml pont.yml; do
  if grep -q "file: \.\./exemples/airfoil_data/" "$ICI/$yml"; then
    echo "$yml lit la table de profil à l'ancien chemin (../exemples/airfoil_data/, avant le rangement du 26/11). Corrigez-le, dans ce dossier :"
    echo "   sed -i 's#\.\./exemples/airfoil_data/#../../../communs/exemples-LHEEA/airfoil_data/#' $yml"; exit 1
  fi
done
TRAV="$(mktemp -d "$ICI/.calcul.XXXXXX")" || exit 1
trap 'rm -rf "${TRAV:?}"' EXIT
ok=1
for paire in "aile-caboteur.yml:bandes" "nll.yml:nll_pied-libre" "pont.yml:nll_pont"; do
  yml="${paire%%:*}"; nom="${paire##*:}"
  rm -f "${TRAV:?}"/*
  sortie="$(cd "$TRAV" && "$OUTIL" "$ICI/$yml" --vtk 1 2>&1)"
  if [ ! -f "$TRAV/aile-caboteur_WPU-1_force_0000.vtk" ]; then
    echo "$yml : l'outil n'a rien écrit. Fin de sa sortie :"; echo "$sortie" | tail -5; exit 1
  fi
  mv -f "$TRAV/aile-caboteur_WPU-1_force_0000.vtk" "$S/${nom}_force.vtk"
  mv -f "$TRAV/aile-caboteur_WPU-1_0000.vtk"       "$S/${nom}_aile.vtk"
  for f in "$TRAV"/aile-caboteur_WPU-1_*_0000.vtk; do   # NLL : horseshoeVortex (tourbillons), mirror (aile image du pont)
    [ -f "$f" ] || continue; x="${f##*/aile-caboteur_WPU-1_}"; mv -f "$f" "$S/${nom}_${x%_0000.vtk}.vtk"
  done
  mv -f "$TRAV/aile-caboteur_WPU-1_0000.csv"       "$S/${nom}_elements.csv"
  mv -f "$TRAV/results.csv"                        "$S/${nom}_results.csv"
  total="$(echo "$sortie" | grep '^ Total' | tail -1)"
  fx="$(echo "$total" | awk -F'|' '{split($4,a,","); gsub(/ /,"",a[1]); print a[1]}')"
  fy="$(echo "$total" | awk -F'|' '{split($4,a,","); gsub(/ /,"",a[2]); print a[2]}')"
  printf "%-18s F_x = %9s N   F_y = %9s N\n" "$nom" "$fx" "$fy"
  [ "$fx" = "0" ] && { echo "   -> efforts nuls : calcul non convergé (voir la manipulation 2 ou 3)"; ok=0; }
done
[ $ok = 1 ] && echo "Les trois calculs sont faits (sorties/). Dans ParaView : File > Load State > vue.pvsm (ce dossier)."
