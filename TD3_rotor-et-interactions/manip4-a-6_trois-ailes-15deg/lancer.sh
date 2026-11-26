#!/usr/bin/env bash
# TD 3 (EGN-S7, ENSM), manipulations 4 à 6 : les trois ailes de Malmek au près (vent apparent à 15° de l'avant),
# en théorie des bandes, en NLL, puis chaque voile seule en NLL ; sorties pour ParaView.
#
#   cd ~/TD-Propulsion-Velique/TD3_rotor-et-interactions/manip4-a-6_trois-ailes-15deg
#   bash lancer.sh
#
# Fichiers lus (ce dossier, non modifiés) :
#   bandes.yml             votre copie de trois-ailes-15deg.yml, modèle « strip theory » (manipulation 5)
#   trois-ailes-15deg.yml  les trois ailes ensemble, NLL (copie de l'exemple 9 du LHEEA, réglages du cas à 15°)
#   voile-1-seule.yml, voile-2-seule.yml, voile-3-seule.yml
#                          la même NLL avec une seule voile, même place et même réglage (pas d'interaction)
# Fichiers écrits dans sorties/ (ignoré par Git) : bandes_voile-N_*, nll_voile-N_* (.vtk pour ParaView, dont les
# tourbillons en fer à cheval et l'image sous le plan de symétrie en NLL ; .csv par élément), bandes_results.csv,
# nll_results.csv, nll-seule_voile-N_results.csv ; puis les données de l'onglet « Interaction » (fabriquer_interaction.py :
# interaction_voile-N.vtk, vent-local_*.vtk, interaction_bilan.csv). Puis vue.pvsm s'ouvre dans ParaView (File > Load State).
# L'outil écrit des fichiers de même nom (test 9_sail_*) à chaque calcul : on les lance l'un après l'autre dans un
# dossier de calcul temporaire et on ramène les sorties renommées.
set -u
ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTIL="$(command -v CN-AeroModels || echo "$HOME/outils/CN-AeroModels/bin/CN-AeroModels")"
cd "$ICI" || exit 1
[ -x "$OUTIL" ] || { echo "CN-AeroModels introuvable (TD 1 : bash scripts/installer_cnaero.sh)"; exit 1; }
for f in trois-ailes-15deg.yml bandes.yml voile-1-seule.yml voile-2-seule.yml voile-3-seule.yml; do
  [ -f "$ICI/$f" ] || { echo "Absent : $f$([ "$f" = bandes.yml ] && echo ' (faites d abord la manipulation 5)')"; exit 1; }
done
grep -q "^      - model: strip theory" "$ICI/bandes.yml" || { echo "bandes.yml doit porter « model: strip theory » (manipulation 5)"; exit 1; }
# (les fichiers du LHEEA ont des fins de ligne Windows, CRLF : la comparaison les ignore, un éditeur peut les changer)
if ! diff -q --strip-trailing-cr <(sed 's/^      - model: strip theory/      - model: nonlinear lifting line/' "$ICI/bandes.yml") "$ICI/trois-ailes-15deg.yml" >/dev/null; then
  echo "bandes.yml ne doit différer de trois-ailes-15deg.yml que par la ligne du modèle (manipulation 5) : refaites la copie"; exit 1
fi
mkdir -p "$ICI/sorties" || exit 1
TRAV="$(mktemp -d "$ICI/sorties/.calcul.XXXXXX")" || exit 1
trap 'rm -rf "$TRAV"' EXIT
S="$ICI/sorties"

calcul() {   # calcul <fichier .yml> : lance l'outil dans $TRAV, vide au préalable
  rm -f "$TRAV"/*
  sortie="$(cd "$TRAV" && "$OUTIL" "$ICI/$1" --vtk 1 2>&1)"
  [ -f "$TRAV/results.csv" ] || { echo "$1 : l'outil n'a rien écrit. Fin de sa sortie :"; echo "$sortie" | tail -5; exit 1; }
}
afficher() {  # afficher <results.csv> <premier numéro de voile>
  awk -F';' -v n0="$2" 'NR > 1 { printf "   voile %d   incidence (AoA) %7.2f deg   C_L %7.4f   C_x %7.4f   C_y %7.4f\n", n0 + NR - 2, $5, $8, $10, $11 }' "$1"
}

ok=1
for paire in "bandes.yml:bandes" "trois-ailes-15deg.yml:nll"; do
  yml="${paire%%:*}"; nom="${paire##*:}"
  calcul "$yml"
  for n in 1 2 3; do
    mv -f "$TRAV/test 9_sail_${n}_force_0000.vtk" "$S/${nom}_voile-${n}_force.vtk"
    mv -f "$TRAV/test 9_sail_${n}_0000.vtk"       "$S/${nom}_voile-${n}_aile.vtk"
    mv -f "$TRAV/test 9_sail_${n}_0000.csv"       "$S/${nom}_voile-${n}_elements.csv"
    for f in "$TRAV/test 9_sail_${n}_"*_0000.vtk; do   # NLL : horseshoeVortex (tourbillons), mirror (image sous le plan)
      [ -f "$f" ] || continue; x="${f##*/test 9_sail_${n}_}"; mv -f "$f" "$S/${nom}_voile-${n}_${x%_0000.vtk}.vtk"
    done
  done
  mv -f "$TRAV/results.csv" "$S/${nom}_results.csv"
  echo "$nom ($yml, les trois voiles ensemble) :"
  afficher "$S/${nom}_results.csv" 1
  [ "$(awk -F';' 'NR > 1' "$S/${nom}_results.csv" | wc -l)" = 3 ] || { echo "   -> trois voiles attendues"; ok=0; }
done
echo "nll, chaque voile seule (voile-N-seule.yml) :"
for n in 1 2 3; do
  calcul "voile-$n-seule.yml"
  mv -f "$TRAV/results.csv" "$S/nll-seule_voile-${n}_results.csv"
  afficher "$S/nll-seule_voile-${n}_results.csv" "$n"
done
somme() { awk -F';' 'FNR > 1 { s += $10 } END { printf "%.4f", s }' "$@"; }
echo "Somme des C_x : nll ensemble $(somme "$S/nll_results.csv") ; nll voiles seules $(somme "$S"/nll-seule_voile-?_results.csv)"
# Données de l'onglet « Interaction » de la vue (session 17) : écart d'incidence NLL − bandes, vent local, bilan
python3 "$ICI/fabriquer_interaction.py" --sortie "$S" || { echo "fabriquer_interaction.py a échoué (l'onglet Interaction sera vide)"; ok=0; }
[ $ok = 1 ] && echo "Les calculs sont faits (sorties/). Dans ParaView : File > Load State > vue.pvsm (ce dossier)."
