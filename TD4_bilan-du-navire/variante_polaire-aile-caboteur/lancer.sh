#!/usr/bin/env bash
# TD 4 (EGN-S7, ENSM), variante V-polaire (exercice M07) : polaire de l'aile du caboteur, sorties dans sorties/.
#
#   cd ~/TD-Propulsion-Velique/TD4_bilan-du-navire/variante_polaire-aile-caboteur
#   bash lancer.sh                 # la polaire : vent vrai de 30° à 180° par pas de 10° (16 calculs), puis le tracé
#   bash lancer.sh 90              # un seul angle du vent vrai (ici 90°, le vent de travers du TD 2)
#   bash lancer.sh CONVERGENCE     # vent de travers, réglage fixé à 30,5° : 10, 20, 30 et 40 éléments donnent-ils
#                                  # la même poussée ? (quelques secondes)
#
# Le cas : aile-caboteur-polaire.yml (ce dossier, non modifié), l'aile du caboteur en ligne portante non linéaire,
# pied libre, 20 éléments, réglage cherché par l'outil (maxThrust) ; navire à 14 nœuds, vent vrai de 20 nœuds.
# Pour chaque angle, lancer.sh écrit une copie du fichier où seule la direction du vent change (direction = 180 - TWA,
# convention NED de l'exercice A02 : direction vers laquelle souffle le vent) et lance l'outil dans sorties/TWA_NNN/.
# L'outil cherche le réglage par un algorithme génétique : 2 à 7 minutes par angle ; d'un lancement à l'autre, il
# ne s'arrête pas toujours au même réglage (F_x à quelques % près : relancez un angle pour le voir). Les angles tournent en parallèle,
# autant que de cœurs (JOBS=4 bash lancer.sh pour en prendre moins) ; le tout prend de 5 à 20 minutes selon la machine.
# Sorties : sorties/polaire.csv (TWA, AWA, réglage, F_x, F_y), sorties/polaire.png et .svg (tracé), et pour chaque
# angle sorties/TWA_NNN/ (copie du fichier, results.csv, ecran.txt : tout ce que l'outil a affiché).
set -u
ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTIL="$(command -v CN-AeroModels || echo "$HOME/outils/CN-AeroModels/bin/CN-AeroModels")"
[ -x "$OUTIL" ] || { echo "CN-AeroModels introuvable (TD 1 : bash scripts/installer_cnaero.sh)"; exit 1; }
CAS="$ICI/aile-caboteur-polaire.yml"
[ -f "$CAS" ] || { echo "Absent : aile-caboteur-polaire.yml"; exit 1; }
S="$ICI/sorties"
mkdir -p "$S" || exit 1
JOBS="${JOBS:-$(nproc 2>/dev/null || echo 2)}"

# un calcul : TWA, nombre d'éléments, nom du dossier [, réglage fixé en degrés : sans lui, maxThrust] ; écrit une ligne
# « TWA;n;AWA;réglage;F_x;F_y » (kN), ou « échec », ou « non convergé » (efforts nuls rendus par l'outil)
un_calcul() {
  local twa="$1" n="$2" d="$S/$3" mu="${4:-}"
  mkdir -p "$d" && rm -f "$d"/*
  local dir; dir="$(awk -v t="$twa" 'BEGIN{printf "%g", 180 - t}')"
  sed -e "s#    direction: {unit: deg, value: 90.}#    direction: {unit: deg, value: $dir}#" \
      -e "s#number of elements: 20#number of elements: $n#" "$CAS" > "$d/cas.yml"
  if [ -n "$mu" ]; then
    sed -i -e "s#control: maxThrust#control: commands#" \
           -e "s#setting: {unit: deg, values: \[34.4, 34.4\]}#setting: {unit: deg, values: [$mu, $mu]}#" "$d/cas.yml"
  fi
  (cd "$d" && "$OUTIL" cas.yml > ecran.txt 2>&1)
  local w t; w="$(grep '^ WPU-1 ' "$d/ecran.txt" | tail -1)"; t="$(grep '^ Total ' "$d/ecran.txt" | tail -1)"
  if [ -z "$t" ] || [ ! -f "$d/results.csv" ]; then echo "$twa;$n;échec;;;"; return; fi
  echo "$w|$t" | awk -F'|' -v twa="$twa" -v n="$n" '{
    split($2, a, ","); split($4, f, ",");
    for (i in a) gsub(/ /, "", a[i]); for (i in f) gsub(/ /, "", f[i]);
    awa = a[2] < 0 ? -a[2] : a[2]; fy = f[2] < 0 ? -f[2] : f[2];
    if (f[1] + 0 == 0 && f[2] + 0 == 0) { printf "%s;%s;non convergé;;;\n", twa, n; exit }
    printf "%s;%s;%.2f;%.2f;%.2f;%.2f\n", twa, n, awa, a[3], f[1] / 1000, fy / 1000 }'
}
export -f un_calcul; export S CAS OUTIL

entete="TWA_deg;elements;AWA_deg;reglage_deg;Fx_kN;Fy_kN"
debut=$(date +%s)
case "${1:-POLAIRE}" in
  POLAIRE)
    echo "Polaire : 16 angles, $JOBS en parallèle (2 à 5 min par angle)…"
    { echo "$entete"
      seq 30 10 180 | xargs -P "$JOBS" -I{} bash -c 'un_calcul {} 20 TWA_$(printf %03d {})' | sort -t';' -k1,1n
    } > "$S/polaire.csv" ;;
  CONVERGENCE)
    echo "Convergence au vent de travers (TWA 90°), réglage fixé à 30,5° : 10, 20, 30 et 40 éléments…"
    { echo "$entete"
      printf "10\n20\n30\n40\n" | xargs -P 4 -I{} bash -c 'un_calcul 90 {} convergence_n{} 30.5' | sort -t';' -k2,2n
    } > "$S/convergence.csv"
    column -t -s';' "$S/convergence.csv"; echo "($(( $(date +%s) - debut )) s ; sorties/convergence.csv)"; exit 0 ;;
  *)
    case "$1" in (*[!0-9]*|'') echo "Usage : bash lancer.sh [TWA en degrés | CONVERGENCE]"; exit 1;; esac
    { echo "$entete"; un_calcul "$1" 20 "TWA_$(printf %03d "$1")"; } > "$S/TWA_$(printf %03d "$1").csv"
    column -t -s';' "$S/TWA_$(printf %03d "$1").csv"; echo "($(( $(date +%s) - debut )) s)"; exit 0 ;;
esac
column -t -s';' "$S/polaire.csv"
echo "($(( $(date +%s) - debut )) s ; sorties/polaire.csv)"
grep -q "échec\|non convergé" "$S/polaire.csv" && echo "Des angles n'ont pas abouti : lisez sorties/TWA_NNN/ecran.txt."
python3 "$ICI/tracer_polaire.py" "$S/polaire.csv" && echo "Tracé : sorties/polaire.png (et .svg)."
