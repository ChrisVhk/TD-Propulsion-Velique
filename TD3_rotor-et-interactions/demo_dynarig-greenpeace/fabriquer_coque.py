#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coque générique et superstructures en blocs pour la démonstration DynaRig du TD 3 (EGN-S7, ENSM) : fichiers .vtk
pour ParaView, et aires projetées pour le fardage (fardage.py).

    python3 fabriquer_coque.py [--sortie DOSSIER]     # écrit coque.vtk et superstructures.vtk (défaut : sorties/)

CHIFFRES PUBLIÉS (armateur, Foundation Zero, lus le 26/11/2026) : longueur 74,95 m, largeur 13,35 m, tirant d'eau de
projet 5,5 m. Tout le reste est une HYPOTHÈSE D'ÉCOLE (aucun plan n'est publié ; ce n'est pas le navire réel) :
  - coque en parallélépipède effilé : murailles verticales, fond plat ; à l'avant, l'étrave se referme en pointe sur les
    12,5 derniers mètres (en plan) ; arrière à tableau ; franc-bord 3,0 m (même valeur que fabriquer_cas.py) ;
  - superstructures en deux blocs : un rouf bas entre les mâts (24 m × 10 m × 2,6 m de haut, sous le pied de la voilure
    à 4 m au-dessus du pont) et une timonerie sur deux niveaux à l'arrière du mât arrière (8 m × 10 m × 5,6 m), en
    dehors du balayage des vergues (±10 m autour des mâts, à x = ±15 m) ;
  - mâts, vergues, garde-corps, embarcations : non représentés.
Repère : celui du navire dans CN-AeroModels (x vers l'avant, y vers tribord, z vers le bas, origine au milieu, à la
flottaison), comme les sorties .vtk de l'outil : la coque se superpose aux voiles dans ParaView.
Interaction voiles-coque : aucune (l'outil ne voit que le pont, en plan de symétrie).
ENSM (Christophe VANHORICK), 26/11/2026, Apache 2.0.
"""
import argparse
import os

L, B, T, FRANC_BORD = 74.95, 13.35, 5.5, 3.0
L_ETRAVE = 12.5
X_AV, X_AR = L / 2.0, -L / 2.0
# Blocs : (nom, x_min, x_max, demi-largeur, z_bas (hauteur au-dessus de l'eau), hauteur)
BLOCS = [("rouf", -12.0, 12.0, 5.0, FRANC_BORD, 2.6),
         ("timonerie", -34.0, -26.0, 5.0, FRANC_BORD, 5.6)]


def coque():
    """Points et faces de la coque (z vers le bas : pont à z = -franc-bord, quille à z = +T)."""
    xe = X_AV - L_ETRAVE
    plan = [(X_AR, -B / 2), (xe, -B / 2), (X_AV, 0.0), (xe, B / 2), (X_AR, B / 2)]   # contour, sens direct vu de dessus
    pts = [(x, y, -FRANC_BORD) for x, y in plan] + [(x, y, T) for x, y in plan]
    n = len(plan)
    faces = [list(range(n)), [n + k for k in reversed(range(n))]]
    faces += [[k, (k + 1) % n, n + (k + 1) % n, n + k] for k in range(n)]
    return pts, faces


def bloc(x0, x1, dy, z_bas, h):
    pts = [(x, y, -z) for z in (z_bas, z_bas + h) for x, y in ((x0, -dy), (x1, -dy), (x1, dy), (x0, dy))]
    faces = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    return pts, faces


def ecrire_vtk(chemin, titre, morceaux):
    pts, faces = [], []
    for p, f in morceaux:
        base = len(pts)
        pts += p
        faces += [[base + i for i in face] for face in f]
    with open(chemin, "w", newline="\n") as fh:
        fh.write("# vtk DataFile Version 3.0\n%s\nASCII\nDATASET POLYDATA\n" % titre)
        fh.write("POINTS %d float\n" % len(pts))
        fh.writelines("%.4f %.4f %.4f\n" % p for p in pts)
        fh.write("POLYGONS %d %d\n" % (len(faces), sum(len(f) + 1 for f in faces)))
        fh.writelines("%d %s\n" % (len(f), " ".join(map(str, f))) for f in faces)


def aires():
    """Paramètres de Fujiwara et al. (2005, Fig. 2) tirés de la géométrie ci-dessus (hauteurs au-dessus de l'eau)."""
    a_coque = L * FRANC_BORD                          # côté de la coque au-dessus de l'eau (murailles verticales)
    morceaux = [(a_coque, 0.0, FRANC_BORD / 2.0)]     # (aire, x du centre, hauteur du centre)
    a_od = 0.0
    for _, x0, x1, dy, zb, h in BLOCS:
        a = (x1 - x0) * h
        a_od += a
        morceaux.append((a, (x0 + x1) / 2.0, zb + h / 2.0))
    a_l = sum(a for a, _, _ in morceaux)
    c = sum(a * x for a, x, _ in morceaux) / a_l
    h_c = sum(a * z for a, _, z in morceaux) / a_l
    # aire frontale : coque + la plus haute des superstructures (même largeur : les projections se recouvrent)
    larg = max(2 * dy for _, _, _, dy, _, _ in BLOCS)
    h_max = max(zb + h for _, _, _, _, zb, h in BLOCS)
    a_f = B * FRANC_BORD + larg * (h_max - FRANC_BORD)
    return dict(L_OA=L, B=B, A_F=a_f, A_L=a_l, A_OD=a_od, C=c, H_C=h_c, H_BR=h_max)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Coque générique et superstructures (VTK) ; aires projetées.")
    ap.add_argument("--sortie", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "sorties"))
    a = ap.parse_args()
    os.makedirs(a.sortie, exist_ok=True)
    ecrire_vtk(os.path.join(a.sortie, "coque.vtk"), "coque generique (ENSM, hypothese d'ecole)", [coque()])
    ecrire_vtk(os.path.join(a.sortie, "superstructures.vtk"), "superstructures en blocs (ENSM, hypothese d'ecole)",
               [bloc(x0, x1, dy, zb, h) for _, x0, x1, dy, zb, h in BLOCS])
    print("coque.vtk et superstructures.vtk écrits dans", a.sortie)
    print(" ; ".join("%s = %.2f" % kv for kv in aires().items()))
