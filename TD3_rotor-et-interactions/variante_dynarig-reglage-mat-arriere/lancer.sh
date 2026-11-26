#!/usr/bin/env bash
# TD 3 (EGN-S7, ENSM), variante V-DynaRig : les deux DynaRigs d'école de la démonstration, mât avant fixe à −70°,
# réglage du mât arrière au choix ; une ligne par calcul dans sorties/balayage.csv (ignoré par Git).
#
#   cd ~/TD-Propulsion-Velique/TD3_rotor-et-interactions/variante_dynarig-reglage-mat-arriere
#   bash lancer.sh -75          # mât arrière à −75°, 40 éléments par mât
#   bash lancer.sh -55 80       # même chose avec 80 éléments par mât (contrôle de convergence, ~10 s)
#
# Fichiers lus (ce dossier, non modifiés) : fabriquer_cas.py et plaque-cambree.yml, copies à l'identique de ceux de
# demo_dynarig-greenpeace/ (hypothèses d'école et polaire d'école : en tête de fabriquer_cas.py). Le fichier d'entrée
# de chaque calcul est écrit dans sorties/ (arriere_<réglage>_n<éléments>.yml) : vous pouvez l'ouvrir.
set -u
ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTIL="$(command -v CN-AeroModels || echo "$HOME/outils/CN-AeroModels/bin/CN-AeroModels")"
[ -x "$OUTIL" ] || { echo "CN-AeroModels introuvable (TD 1 : bash scripts/installer_cnaero.sh)"; exit 1; }
[ $# -ge 1 ] && [ $# -le 2 ] || { echo "Usage : bash lancer.sh RÉGLAGE_DU_MÂT_ARRIÈRE [ÉLÉMENTS_PAR_MÂT]   (ex. : bash lancer.sh -75)"; exit 1; }
R="$1"; N="${2:-40}"
[[ "$R" =~ ^-?[0-9]+([.][0-9]+)?$ ]] || { echo "Réglage attendu en degrés, par exemple -75"; exit 1; }
[[ "$N" =~ ^[0-9]+$ ]] && [ $((N % 5)) -eq 0 ] || { echo "Éléments par mât : un multiple de 5 (40 ou 80)"; exit 1; }
mkdir -p "$ICI/sorties" || exit 1
TRAV="$(mktemp -d "$ICI/sorties/.calcul.XXXXXX")" || exit 1
trap 'rm -rf "$TRAV"' EXIT
Y="$ICI/sorties/arriere_${R}_n${N}.yml"
python3 "$ICI/fabriquer_cas.py" --elements "$N" --avant -70 --arriere "$R" --sortie "$Y" >/dev/null || exit 1
cp "$ICI/plaque-cambree.yml" "$TRAV/"
sortie="$(cd "$TRAV" && "$OUTIL" "$Y" 2>&1)"
[ -f "$TRAV/results.csv" ] || { echo "L'outil n'a rien écrit. Fin de sa sortie :"; echo "$sortie" | tail -5; exit 1; }
echo "$sortie" | grep -q "Newton method has failed" && echo "attention : « Newton method has failed »"
ligne="$(awk -F';' -v r="$R" -v n="$N" 'NR == 1 { for (i = 1; i <= NF; i++) { if ($i == "Fx(kN)") c = i; if ($i == "AoA") a = i } }
  NR == 2 { fa = $c; aa = $a } NR == 3 { printf "%s;%s;%.2f;%.2f;%.2f;%.2f;%.2f", r, n, aa, $a, fa, $c, fa + $c }' "$TRAV/results.csv")"
B="$ICI/sorties/balayage.csv"
[ -f "$B" ] || echo "reglage_arriere(deg);elements_par_mat;incidence_avant(deg);incidence_arriere(deg);Fx_avant(kN);Fx_arriere(kN);Fx_total(kN)" > "$B"
echo "$ligne" >> "$B"
echo "$ligne" | awk -F';' '{ printf "mât arrière %s° (%s éléments par mât) : incidences %s° / %s° ; F_x avant %s kN, arrière %s kN, total %s kN\n", $1, $2, $3, $4, $5, $6, $7 }'
echo "(ligne ajoutée à sorties/balayage.csv)"
