#!/usr/bin/env bash
# TD 3 (EGN-S7, ENSM), partie 2 : les trois ailes de Malmek en NLL et en théorie des bandes, avec les sorties ParaView.
#
#   cd ~/TD-Propulsion-Velique/cas/trois-ailes
#   bash TD3_lancer_les_deux.sh
#
# Les deux calculs écrivent des fichiers de même nom (test 9_sail_*) : on les lance l'un après l'autre dans un
# dossier de calcul temporaire, placé dans cas/ comme le dossier du cas, et on ramène ici les sorties renommées.
# Fichiers lus (dossier du cas, non modifiés) :
#   1. bandes.yml       copie de trois-ailes.yml, modèle « strip theory » (votre copie de la manipulation 5)
#   2. trois-ailes.yml  le fichier de l'exemple 9 du LHEEA, tel que fourni (NLL)
# Fichiers écrits ici : 1_bandes_voile-N_*, 2_nll_voile-N_* (.vtk pour ParaView, dont les tourbillons en fer à
# cheval et l'image sous le plan de symétrie en NLL ; .csv par élément) et 1_bandes_results.csv, 2_nll_results.csv ;
# puis TD3_trois-ailes.pvsm s'ouvre dans ParaView (File > Load State).
set -u
ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTIL="$(command -v CN-AeroModels || echo "$HOME/outils/CN-AeroModels/bin/CN-AeroModels")"
cd "$ICI" || exit 1
TRAV="$(mktemp -d "$ICI/../.calcul_TD3.XXXXXX")" || exit 1
trap 'rm -rf "$TRAV"' EXIT
[ -x "$OUTIL" ] || { echo "CN-AeroModels introuvable (TD 1 : bash scripts/installer_cnaero.sh)"; exit 1; }
for f in trois-ailes.yml bandes.yml; do
  [ -f "$ICI/$f" ] || { echo "Absent : cas/trois-ailes/$f (faites d'abord la manipulation 5)"; exit 1; }
done
grep -q "^      - model: strip theory" "$ICI/bandes.yml" || { echo "bandes.yml doit porter « model: strip theory » (manipulation 5)"; exit 1; }
# (le fichier du LHEEA a des fins de ligne Windows, CRLF : la comparaison les ignore, un éditeur peut les changer)
if ! diff -q --strip-trailing-cr <(sed 's/^      - model: strip theory/      - model: nonlinear lifting line/' "$ICI/bandes.yml") "$ICI/trois-ailes.yml" >/dev/null; then
  echo "bandes.yml ne doit différer de trois-ailes.yml que par la ligne du modèle (manipulation 5) : refaites la copie"; exit 1
fi
ok=1
for paire in "bandes.yml:1_bandes" "trois-ailes.yml:2_nll"; do
  yml="${paire%%:*}"; nom="${paire##*:}"
  rm -f "$TRAV"/*
  sortie="$(cd "$TRAV" && "$OUTIL" "$ICI/$yml" --vtk 1 2>&1)"
  if [ ! -f "$TRAV/test 9_sail_1_force_0000.vtk" ]; then
    echo "$yml : l'outil n'a rien écrit. Fin de sa sortie :"; echo "$sortie" | tail -5; exit 1
  fi
  for n in 1 2 3; do
    mv -f "$TRAV/test 9_sail_${n}_force_0000.vtk" "${nom}_voile-${n}_force.vtk"
    mv -f "$TRAV/test 9_sail_${n}_0000.vtk"       "${nom}_voile-${n}_aile.vtk"
    mv -f "$TRAV/test 9_sail_${n}_0000.csv"       "${nom}_voile-${n}_elements.csv"
    for f in "$TRAV/test 9_sail_${n}_"*_0000.vtk; do   # NLL : horseshoeVortex (tourbillons), mirror (image sous le plan)
      [ -f "$f" ] || continue; x="${f##*/test 9_sail_${n}_}"; mv -f "$f" "${nom}_voile-${n}_${x%_0000.vtk}.vtk"
    done
  done
  mv -f "$TRAV/results.csv" "${nom}_results.csv"
  echo "$nom ($yml) :"
  awk -F';' 'NR > 1 { printf "   voile %d   incidence (AoA) %7.2f deg   C_L %7.4f   C_x %7.4f   C_y %7.4f\n", NR - 1, $5, $8, $10, $11 }' "${nom}_results.csv"
  [ "$(awk -F';' 'NR > 1' "${nom}_results.csv" | wc -l)" = 3 ] || { echo "   -> trois voiles attendues"; ok=0; }
done
[ $ok = 1 ] && echo "Les deux calculs sont faits. Dans ParaView : File > Load State > TD3_trois-ailes.pvsm (ce dossier)."
