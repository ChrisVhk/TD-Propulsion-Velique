#!/usr/bin/env bash
# TD 3 (EGN-S7, ENSM), démonstration de l'enseignant : deux DynaRigs d'école sur un navire générique aux dimensions
# publiées du navire de Greenpeace, au travers (hypothèses : en tête de fabriquer_cas.py).
#
#   cd ~/TD-Propulsion-Velique/TD3_rotor-et-interactions/demo_dynarig-greenpeace
#   bash lancer.sh
#
# Fichiers lus (ce dossier, non modifiés) : dynarig-deux-mats.yml, dynarig-mat-avant-seul.yml,
# dynarig-mat-arriere-seul.yml (écrits par fabriquer_cas.py) et plaque-cambree.yml (polaire d'école, hypothèse :
# fabriquer_polaire.py). Fichiers écrits dans sorties/ (ignoré par Git) : nll-deux-mats_* (.vtk pour ParaView, .csv
# par élément, results.csv), nll-avant-seul_results.csv, nll-arriere-seul_results.csv ; la coque générique
# (sorties/coque.vtk, sorties/superstructures.vtk) est écrite par fabriquer_coque.py si ce script est présent.
# L'outil lit la polaire par rapport au dossier où il tourne : on la copie dans le dossier de calcul temporaire.
set -u
ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTIL="$(command -v CN-AeroModels || echo "$HOME/outils/CN-AeroModels/bin/CN-AeroModels")"
cd "$ICI" || exit 1
[ -x "$OUTIL" ] || { echo "CN-AeroModels introuvable (TD 1 : bash scripts/installer_cnaero.sh)"; exit 1; }
for f in dynarig-deux-mats.yml dynarig-mat-avant-seul.yml dynarig-mat-arriere-seul.yml plaque-cambree.yml; do
  [ -f "$ICI/$f" ] || { echo "Absent : $f (python3 fabriquer_polaire.py ; python3 fabriquer_cas.py)"; exit 1; }
done
mkdir -p "$ICI/sorties" || exit 1
TRAV="$(mktemp -d "$ICI/sorties/.calcul.XXXXXX")" || exit 1
trap 'rm -rf "$TRAV"' EXIT
S="$ICI/sorties"

calcul() {   # calcul <fichier .yml> <nom> [--vtk 1]
  rm -rf "${TRAV:?}"/*; cp "$ICI/plaque-cambree.yml" "$TRAV/"
  sortie="$(cd "$TRAV" && "$OUTIL" "$ICI/$1" "${@:3}" 2>&1)"
  [ -f "$TRAV/results.csv" ] || { echo "$1 : l'outil n'a rien écrit. Fin de sa sortie :"; echo "$sortie" | tail -5; exit 1; }
  echo "$sortie" | grep -q "Newton method has failed" && echo "   attention : « Newton method has failed » ($1)"
  mv -f "$TRAV/results.csv" "$S/$2_results.csv"
}
fx() {  # fx <results.csv> <rang de la ligne> : F_x en kN
  awk -F';' -v k="$2" 'NR == 1 { for (i = 1; i <= NF; i++) if ($i == "Fx(kN)") c = i } NR == k + 1 { printf "%.1f", $c }' "$1"
}

calcul dynarig-deux-mats.yml nll-deux-mats --vtk 1
for m in avant arriere; do
  for s in "" _force _horseshoeVortex _mirror; do
    mv -f "$TRAV/dynarig_mat_${m}${s}_0000.vtk" "$S/nll-deux-mats_mat-${m}${s:-_voile}.vtk"
  done
  mv -f "$TRAV/dynarig_mat_${m}_0000.csv" "$S/nll-deux-mats_mat-${m}_elements.csv"
done
mv -f "$TRAV/wind_0000.vtk" "$S/nll-deux-mats_vent.vtk"
calcul dynarig-mat-avant-seul.yml nll-avant-seul
calcul dynarig-mat-arriere-seul.yml nll-arriere-seul
[ -f "$ICI/fabriquer_coque.py" ] && python3 "$ICI/fabriquer_coque.py" --sortie "$S" >/dev/null

A2="$(fx "$S/nll-deux-mats_results.csv" 1)"; R2="$(fx "$S/nll-deux-mats_results.csv" 2)"
A1="$(fx "$S/nll-avant-seul_results.csv" 1)"; R1="$(fx "$S/nll-arriere-seul_results.csv" 1)"
echo "Deux DynaRigs d'école, NLL, au travers (vent vrai 12 m/s à 10 m, navire à 10 nœuds), réglages de fabriquer_cas.py :"
echo "   mât avant   : seul $A1 kN ; avec le mât arrière $A2 kN"
echo "   mât arrière : seul $R1 kN ; derrière le mât avant $R2 kN"
awk -v a1="$A1" -v r1="$R1" -v a2="$A2" -v r2="$R2" 'BEGIN {
  printf "   poussée totale (F_x) : %.1f kN, contre %.1f kN pour deux mâts seuls (%+.1f %%) ; mât arrière %+.1f %%\n",
         a2 + r2, a1 + r1, 100 * (a2 + r2 - a1 - r1) / (a1 + r1), 100 * (r2 - r1) / r1 }'
echo "Rappel : polaire d'école (hypothèse), ligne portante non validée pour un DynaRig (allongement 2,6, voile souple,"
echo "mâts et vergues absents). Dans ParaView : File > Load State > vue.pvsm (ce dossier)."
