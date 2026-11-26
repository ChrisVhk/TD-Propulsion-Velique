#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Données de la vue « Interaction » des trois ailes (TD 3, manipulation 6 ; EGN-S7, ENSM ; session 17, ARB-EGN-S7-074).
Lit les sorties de lancer.sh (sorties/), n'en change aucune, et écrit dans sorties/ :

  interaction_voile-N.vtk   un point par élément (centre, celui de l'outil) et l'écart d'incidence NLL − bandes, en
                            degrés (« ecart_incidence ») : ce que l'interaction (et l'effet 3D) retire à chaque élément,
                            sans l'effet des réglages, qui diffèrent d'une voile à l'autre ;
  vent-local_bandes.vtk,    un point par voile, au quart de corde (centre de l'élément de mi-hauteur), et le vent
  vent-local_nll.vtk        apparent local de l'outil à cet élément (« vent_local », m/s : colonnes ApparentVelocity_x,
                            _y, _z du fichier par élément, vitesses induites comprises) ;
  interaction_bilan.csv     par voile : C_x seule (NLL, voile-N-seule.yml), C_x ensemble (NLL), perte en %, direction
                            du vent local en bandes et en NLL, et leur écart (deg) ; ligne « somme ».

    python3 fabriquer_interaction.py [--sortie DOSSIER]   # défaut : sorties/ de ce dossier ; lancé par lancer.sh

La vue est construite par voir_sans-paraview.py (et l'état vue.pvsm). ENSM (Christophe VANHORICK), 26/11/2026,
Apache 2.0.
"""
import argparse
import csv
import math
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
VOILES = (1, 2, 3)


def elements(dossier, modele, n):
    with open(os.path.join(dossier, "%s_voile-%d_elements.csv" % (modele, n)), newline="") as f:
        return [{k: float(v) for k, v in r.items() if k and v not in (None, "")}
                for r in csv.DictReader(f, delimiter=";")]


def cx(chemin):
    with open(chemin, newline="") as f:
        return [float(r["Cx"]) for r in csv.DictReader(f, delimiter=";")]


def ecrire_points(chemin, titre, pts, scalaires=(), vecteurs=()):
    with open(chemin, "w", newline="\n") as fh:
        fh.write("# vtk DataFile Version 3.0\n%s\nASCII\nDATASET POLYDATA\n" % titre)
        fh.write("POINTS %d float\n" % len(pts))
        fh.writelines("%.6f %.6f %.6f\n" % p for p in pts)
        fh.write("VERTICES %d %d\n" % (len(pts), 2 * len(pts)))
        fh.writelines("1 %d\n" % k for k in range(len(pts)))
        fh.write("POINT_DATA %d\n" % len(pts))
        for nom, val in scalaires:
            fh.write("SCALARS %s float 1\nLOOKUP_TABLE default\n" % nom)
            fh.writelines("%.6f\n" % v for v in val)
        for nom, val in vecteurs:
            fh.write("VECTORS %s float\n" % nom)
            fh.writelines("%.6f %.6f %.6f\n" % v for v in val)


def preparer(dossier):
    cle_aoa = "AoA(degrees)/SR"
    ens = cx(os.path.join(dossier, "nll_results.csv"))
    bilan = []
    vents = {"bandes": [], "nll": []}
    for n in VOILES:
        eb, en = elements(dossier, "bandes", n), elements(dossier, "nll", n)
        if len(eb) != len(en):
            sys.exit("voile %d : %d éléments en bandes, %d en NLL ; l'écart élément par élément suppose les mêmes"
                     % (n, len(eb), len(en)))
        pts = [(e["Center_x(m)"], e["Center_y(m)"], e["Center_z(m)"]) for e in en]
        ecart = [a[cle_aoa] - b[cle_aoa] for a, b in zip(en, eb)]
        ecrire_points(os.path.join(dossier, "interaction_voile-%d.vtk" % n),
                      "ecart d'incidence NLL - bandes, voile %d (ENSM, d'apres les sorties de CN-AeroModels)" % n,
                      pts, scalaires=[("ecart_incidence", ecart)])
        k = len(en) // 2                                   # élément de mi-hauteur
        directions = {}
        for m, e in (("bandes", eb[k]), ("nll", en[k])):
            v = (e["ApparentVelocity_x(m/s)"], e["ApparentVelocity_y(m/s)"], e["ApparentVelocity_z(m/s)"])
            vents[m].append(((e["Center_x(m)"], e["Center_y(m)"], e["Center_z(m)"]), v))
            directions[m] = math.degrees(math.atan2(v[1], v[0]))
        seule = cx(os.path.join(dossier, "nll-seule_voile-%d_results.csv" % n))[0]
        bilan.append({"voile": n, "Cx_seule": seule, "Cx_ensemble": ens[n - 1],
                      "perte_pct": 100.0 * (ens[n - 1] - seule) / abs(seule),
                      "vent_bandes_deg": directions["bandes"], "vent_nll_deg": directions["nll"],
                      "rotation_deg": directions["nll"] - directions["bandes"],
                      "ecart_incidence_mi_hauteur_deg": ecart[k]})
    s1, s2 = sum(b["Cx_seule"] for b in bilan), sum(b["Cx_ensemble"] for b in bilan)
    bilan.append({"voile": "somme", "Cx_seule": s1, "Cx_ensemble": s2, "perte_pct": 100.0 * (s2 - s1) / abs(s1)})
    for m, lst in vents.items():
        ecrire_points(os.path.join(dossier, "vent-local_%s.vtk" % m),
                      "vent apparent local a mi-hauteur, %s (ENSM, d'apres les sorties de CN-AeroModels)" % m,
                      [p for p, _ in lst], scalaires=[("voile", [float(n) for n in VOILES])],
                      vecteurs=[("vent_local", [v for _, v in lst])])
    champs = ["voile", "Cx_seule", "Cx_ensemble", "perte_pct", "vent_bandes_deg", "vent_nll_deg", "rotation_deg",
              "ecart_incidence_mi_hauteur_deg"]
    with open(os.path.join(dossier, "interaction_bilan.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=champs, delimiter=";", restval="")
        w.writeheader()
        for b in bilan:
            w.writerow({k: (("%.4f" % v) if isinstance(v, float) else v) for k, v in b.items()})
    return bilan


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Données de la vue « Interaction » des trois ailes.")
    ap.add_argument("--sortie", default=os.path.join(ICI, "sorties"))
    a = ap.parse_args()
    for b in preparer(a.sortie):
        if b["voile"] == "somme":
            print("   somme des C_x : seules %.4f, ensemble %.4f (%+.0f %%)" % (b["Cx_seule"], b["Cx_ensemble"], b["perte_pct"]))
        else:
            perte = "négatif dès seule" if b["Cx_seule"] < 0 else "%+.0f %%" % b["perte_pct"]
            print("   voile %d : C_x seule %.4f, ensemble %.4f (%s) ; vent local tourné de %+.1f° ; incidence %+.1f°"
                  % (b["voile"], b["Cx_seule"], b["Cx_ensemble"], perte, b["rotation_deg"],
                     b["ecart_incidence_mi_hauteur_deg"]))
