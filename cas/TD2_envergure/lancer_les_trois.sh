#!/usr/bin/env bash
# TD 2 (EGN-S7, ENSM), manipulation 2 ter : les trois calculs de l'aile du caboteur, avec les sorties ParaView.
#
#   cd ~/TD-Propulsion-Velique/cas/TD2_envergure
#   bash lancer_les_trois.sh
#
# Les trois calculs écrivent des fichiers de même nom (aile-caboteur_WPU-1_*) : on les lance ici, l'un après
# l'autre, et on renomme les sorties après chacun. Fichiers lus (dossier du cas, non modifiés) :
#   1. aile_caboteur.yml  théorie des bandes (manipulation 1)
#   2. nll.yml            NLL, pied libre, 20 éléments (manipulation 2)
#   3. pont.yml           NLL, pont en miroir, 20 éléments (manipulation 2 bis)
# Fichiers écrits ici : 1_bandes_*, 2_nll-pied-libre_*, 3_nll-pont_* (.vtk pour ParaView, dont l'aile image
# 3_nll-pont_mirror.vtk ; .csv par élément),
# puis envergure.pvsm s'ouvre dans ParaView (File > Load State).
set -u
ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CAS="$ICI/../Cas-ENSM_aile-du-caboteur"
OUTIL="$(command -v CN-AeroModels || echo "$HOME/outils/CN-AeroModels/bin/CN-AeroModels")"
cd "$ICI" || exit 1
[ -x "$OUTIL" ] || { echo "CN-AeroModels introuvable (TD 1 : bash scripts/installer_cnaero.sh)"; exit 1; }
for f in aile_caboteur.yml nll.yml pont.yml; do
  [ -f "$CAS/$f" ] || { echo "Absent : Cas-ENSM_aile-du-caboteur/$f (faites d'abord les manipulations 2 et 2 bis)"; exit 1; }
done
grep -q "number of elements: 20" "$CAS/nll.yml"  || { echo "nll.yml doit être à 20 éléments (fin de la manipulation 2)"; exit 1; }
grep -q "number of elements: 20" "$CAS/pont.yml" || { echo "pont.yml doit être à 20 éléments (manipulation 2 bis)"; exit 1; }
grep -q "plane of symmetry" "$CAS/pont.yml"      || { echo "pont.yml n'a pas de bloc plane of symmetry (manipulation 2 bis)"; exit 1; }
ok=1
for paire in "aile_caboteur.yml:1_bandes" "nll.yml:2_nll-pied-libre" "pont.yml:3_nll-pont"; do
  yml="${paire%%:*}"; nom="${paire##*:}"
  sortie="$("$OUTIL" "../Cas-ENSM_aile-du-caboteur/$yml" --vtk 1 2>&1)"
  if [ ! -f aile-caboteur_WPU-1_force_0000.vtk ]; then
    echo "$yml : l'outil n'a rien écrit. Fin de sa sortie :"; echo "$sortie" | tail -5; exit 1
  fi
  mv -f aile-caboteur_WPU-1_force_0000.vtk "${nom}_force.vtk"
  mv -f aile-caboteur_WPU-1_0000.vtk       "${nom}_aile.vtk"
  for f in aile-caboteur_WPU-1_*_0000.vtk; do   # NLL : horseshoeVortex (tourbillons), mirror (aile image du pont)
    [ -f "$f" ] || continue; x="${f#aile-caboteur_WPU-1_}"; mv -f "$f" "${nom}_${x%_0000.vtk}.vtk"
  done
  mv -f aile-caboteur_WPU-1_0000.csv       "${nom}_elements.csv"
  mv -f results.csv                        "${nom}_results.csv"
  total="$(echo "$sortie" | grep '^ Total' | tail -1)"
  fx="$(echo "$total" | awk -F'|' '{split($4,a,","); gsub(/ /,"",a[1]); print a[1]}')"
  fy="$(echo "$total" | awk -F'|' '{split($4,a,","); gsub(/ /,"",a[2]); print a[2]}')"
  printf "%-18s F_x = %9s N   F_y = %9s N\n" "$nom" "$fx" "$fy"
  [ "$fx" = "0" ] && { echo "   -> efforts nuls : calcul non convergé (voir la manipulation 2 ou 2 bis)"; ok=0; }
done
rm -f FreeSurface_0000.vtk wind_0000.vtk
[ $ok = 1 ] && echo "Les trois calculs sont faits. Dans ParaView : File > Load State > envergure.pvsm (ce dossier)."
