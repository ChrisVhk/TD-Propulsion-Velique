#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trace une table de profil de CN-AeroModels : C_L(AoA) et finesse C_L/C_D, une courbe par nombre de Reynolds.
TD Propulsion vélique (EGN-S7, ENSM), TD 1, manipulation 3 (pour A04).

Usage, depuis le dossier du dépôt :
    python3 scripts/tracer_table.py                    # table du cas de l'aile du caboteur (NACA0015_v2.yml)
    python3 scripts/tracer_table.py cas/exemples/airfoil_data/NACA0015_v1.yml
Écrit table_NACA0015_v2.png (ou table_<nom>.png) dans le dossier courant et affiche le nombre de tables tracées.
Modules : pyyaml, matplotlib (installés par scripts/installer_cnaero.sh).
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")                      # pas de fenêtre : on écrit un fichier image
import matplotlib.pyplot as plt
import yaml

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
chemin = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RACINE, "cas", "exemples", "airfoil_data", "NACA0015_v2.yml")
nom = os.path.splitext(os.path.basename(chemin))[0]

# 1er élément du fichier : le nom du profil ; ensuite, une table par Re
tables = yaml.safe_load(open(chemin, encoding="utf-8"))[1:]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
for t in tables:
    aoa = t["AoA"]["values"]
    cl = t["lift coefficient"]
    cd = t["drag coefficient"]
    pts = [(a, l, d) for a, l, d in zip(aoa, cl, cd) if 0 <= a < 90]
    ax1.plot([p[0] for p in pts], [p[1] for p in pts], label="Re = %.1e" % float(t["Re"]))
    pos = [p for p in pts if p[0] > 0]
    ax2.plot([p[0] for p in pos], [p[1] / p[2] for p in pos])
ax1.set_xlabel("AoA (deg)")
ax1.set_ylabel("C_L")
ax1.legend(fontsize=7)
ax1.grid()
ax2.set_xlabel("AoA (deg)")
ax2.set_ylabel("C_L / C_D")
ax2.grid()
sortie = "table_%s.png" % nom
fig.savefig(sortie, dpi=120)
print(len(tables), "tables tracées ->", sortie)
