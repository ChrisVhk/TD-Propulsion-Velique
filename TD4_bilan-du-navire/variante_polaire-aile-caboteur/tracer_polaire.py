#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trace la polaire de l'aile du caboteur : F_x et F_y selon l'angle du vent vrai, et le point du TD 2 (exercice A06).
TD Propulsion vélique (EGN-S7, ENSM), TD 4, variante V-polaire (exercice M07).

Usage, depuis ce dossier (lancer.sh l'appelle à la fin de la polaire) :
    python3 tracer_polaire.py                      # lit sorties/polaire.csv
    python3 tracer_polaire.py sorties/polaire.csv
Écrit sorties/polaire.png et sorties/polaire.svg.
Modules : matplotlib (installé par scripts/installer_cnaero.sh).
"""
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")                      # pas de fenêtre : on écrit un fichier image
import matplotlib.pyplot as plt

ICI = os.path.dirname(os.path.abspath(__file__))
chemin = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ICI, "sorties", "polaire.csv")
sortie = os.path.join(os.path.dirname(os.path.abspath(chemin)), "polaire")

# Point du TD 2 (exercice A06) : vent de travers (TWA 90°), réglage fixé à 34,4° (pas maxThrust), NLL pied libre
A06 = dict(twa=90.0, fx=32.1, fy=30.4)
LIMITE_TABLE = 135.0   # au-delà, l'optimum demande des incidences où la table de profil n'a pas de points (M07, q. 3)


def fr(x, n=1):
    return f"{x:.{n}f}".replace(".", ",")


twa, fx, fy, regl, rates = [], [], [], [], []
with open(chemin, encoding="utf-8") as f:
    for l in csv.DictReader(f, delimiter=";"):
        try:
            twa.append(float(l["TWA_deg"])); fx.append(float(l["Fx_kN"])); fy.append(float(l["Fy_kN"]))
            regl.append(float(l["reglage_deg"]))
        except ValueError:                 # « échec » ou « non convergé » : l'angle n'est pas tracé, il est compté
            rates.append(l["TWA_deg"])
if not twa:
    sys.exit("Aucun angle n'a abouti : lisez sorties/TWA_NNN/ecran.txt")

fig, ax = plt.subplots(figsize=(8, 5.6))
ax.axvspan(LIMITE_TABLE, 185, color="0.92", zorder=0)
ax.text(LIMITE_TABLE + 2, 0.97, "au-delà de 135° :\nhors du domaine\nde la table de profil", transform=ax.get_xaxis_transform(),
        va="top", fontsize=8, color="0.35", zorder=1)
ax.plot(twa, fx, "o-", color="#1f5fa8", ms=4, label="$F_x$, poussée (réglage de poussée maximale)")
ax.plot(twa, fy, "s--", color="#c0504d", ms=4, label="$F_y$, force latérale (au même réglage)")
i = max(range(len(fx)), key=lambda k: fx[k])
ax.annotate(f"poussée maximale\n{fr(fx[i])} kN à {twa[i]:.0f}°", (twa[i], fx[i]), xytext=(twa[i] + 12, fx[i] + 14),
            fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.8))
ax.plot([A06["twa"]], [A06["fx"]], marker="*", ms=14, color="#1f5fa8", mec="k", ls="none", zorder=5,
        label="TD 2, exercice A06 : même vent, réglage fixé à 34,4° (pas maxThrust)")
ax.plot([A06["twa"]], [A06["fy"]], marker="*", ms=14, color="#c0504d", mec="k", ls="none", zorder=5)
ax.annotate(f"A06 : $F_x$ = {fr(A06['fx'])} kN\n$F_y$ = {fr(A06['fy'])} kN", (A06["twa"], A06["fy"]),
            xytext=(A06["twa"] - 32, 6), fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.8))
ax.set_xlim(25, 185); ax.set_ylim(bottom=0)
ax.set_xticks(range(30, 181, 15))
ax.set_xlabel("angle du vent vrai, compté depuis l'avant (°)")
ax.set_ylabel("effort de l'aile (kN)")
ax.grid(alpha=0.3); ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=1, frameon=False)
titre = ("Polaire de l'aile du caboteur : navire à 14 nœuds, vent vrai de 20 nœuds\n"
         "ligne portante non linéaire, pied libre, 20 éléments, réglage cherché par l'outil (maxThrust)")
if rates:
    titre += f"\nangles sans résultat : {', '.join(rates)}°"
ax.set_title(titre, fontsize=9)
fig.tight_layout()
fig.savefig(sortie + ".png", dpi=150)
fig.savefig(sortie + ".svg")
print(f"{len(twa)} angles tracés, {len(rates)} sans résultat ; poussée maximale {fr(fx[i])} kN à TWA {twa[i]:.0f}° "
      f"(réglage {fr(regl[i])}°) -> {os.path.relpath(sortie)}.png, .svg")
