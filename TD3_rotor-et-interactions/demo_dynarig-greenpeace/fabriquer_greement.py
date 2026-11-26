#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gréement de la démonstration DynaRig du TD 3 (EGN-S7, ENSM) : mâts, vergues courbes et voiles creuses, en .vtk pour
ParaView. COUCHE D'HABILLAGE : le calcul porte sur la ligne portante (surface plane de l'outil, colorée par C_L dans la
vue) ; le rendu montre le gréement. Rien ici ne change un effort calculé.

    python3 fabriquer_greement.py [--sortie DOSSIER]   # après le calcul (lancer.sh) : lit l'orientation des voiles
                                                       # dans sorties/nll-deux-mats_mat-*_voile.vtk

Fichiers écrits : mats.vtk, vergues.vtk, voiles.vtk. Python seul, sans module à installer.

Ce qui vient du calcul (fabriquer_cas.py) : position des mâts (x = ±15 m, sur l'axe), cinq panneaux par mât de 9,6 m de
haut, cordes 19,77 / 19,77 / 19,77 / 17,79 / 13,84 m, pied de la voilure à 7 m et tête à 55 m au-dessus de l'eau,
réglage de la démonstration (−70°) : chaque voile est posée sur la corde de la surface de calcul que l'outil écrit
(bord d'attaque, bord de fuite), lue dans ses .vtk ; l'outil place l'axe de rotation (le mât) au quart de la corde.
Ce qui vient des sources (README.md) : six vergues par mât, une à chaque limite des cinq panneaux, courbes, fixées
au mât, cinq voiles sans jour entre elles. Sources : Maltese Falcon, « Each of Maltese Falcon's masts supports six
yards, which [...] have built-in camber of 12% » et « no gaps in the sail plan of each mast » (Wikipedia, « Maltese
Falcon (yacht) », lu le 26/11/2026) ; Southern Spars, brochure DynaRig (juillet 2026) : « curved yard arms », « Each mast
would carry five sails » (Maltese Falcon), « one sail per yard arm ». Pour le navire de Greenpeace, le nombre de
vergues n'est pas publié : six par mât PAR ANALOGIE avec le Maltese Falcon.
HYPOTHÈSES D'ÉCOLE : vergues et voiles en arc de cambrure 10 % (celle de la polaire d'école, plaque-cambree.yml ; le
Maltese Falcon a des vergues à 12 %), arc parabolique, creux vers l'avant (côté de la portance) ; mâts cylindriques de
1,0 m de rayon, du pont (3 m) à 57 m au-dessus de l'eau (sous le tirant d'air publié, 57,85 m) ; vergues : tubes de
0,35 m de rayon, de la longueur de la plus grande des deux voiles qu'elles bordent.
ENSM (Christophe VANHORICK), 26/11/2026, Apache 2.0.
"""
import argparse
import math
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import fabriquer_cas as fc      # noqa: E402  panneaux, pied, positions des mâts

CAMBRURE = 0.10                 # f/c, celle de la polaire d'école
R_MAT, R_VERGUE = 1.0, 0.35     # m
Z_PONT, Z_TETE = -fc.FRANC_BORD, -57.0
PREFIXE = "nll-deux-mats"
N_ARC = 24                      # segments le long d'un arc


def lire_points(chemin):
    mots = open(chemin, encoding="ascii").read().split()
    i = mots.index("POINTS")
    n = int(mots[i + 1])
    v = mots[i + 3:i + 3 + 3 * n]
    return [(float(v[3 * k]), float(v[3 * k + 1]), float(v[3 * k + 2])) for k in range(n)]


def corde(dossier, nom, x_mat):
    """Bord d'attaque et direction de la corde (unitaire) de la surface de calcul, au pied de la voilure.
    Deux points par niveau ; le mât (x_mat, 0) est au quart de la corde depuis le bord d'attaque."""
    pts = lire_points(os.path.join(dossier, "%s_mat-%s_voile.vtk" % (PREFIXE, nom)))
    z0 = max(p[2] for p in pts)
    a, b = [p for p in pts if abs(p[2] - z0) < 1e-6][:2]
    c = math.hypot(b[0] - a[0], b[1] - a[1])
    t = math.hypot(x_mat - a[0], a[1]) / c
    if abs(t - 0.25) > abs(t - 0.75):        # le bord d'attaque est l'autre point
        a, b = b, a
    d = ((b[0] - a[0]) / c, (b[1] - a[1]) / c)
    n = (d[1], -d[0]) if d[1] > 0 else (-d[1], d[0])
    if n[0] < 0:                             # creux du côté de la portance : celui qui pousse vers l'avant
        n = (-n[0], -n[1])
    return d, n


def arc(x_mat, d, n, c, z):
    """Points de l'arc de corde c, mât au quart de corde, cambrure CAMBRURE, à la hauteur z (NED)."""
    pts = []
    for k in range(N_ARC + 1):
        s = k / N_ARC
        u = (s - 0.25) * c                   # le long de la corde, depuis le mât
        w = 4.0 * CAMBRURE * c * s * (1.0 - s)
        pts.append((x_mat + u * d[0] + w * n[0], u * d[1] + w * n[1], z))
    return pts


def tube(ligne, r, m=8):
    """Tube de rayon r autour d'une ligne horizontale (points), m côtés ; fermé aux bouts."""
    pts, faces = [], []
    for k, p in enumerate(ligne):
        q = ligne[min(k + 1, len(ligne) - 1)]
        o = ligne[max(k - 1, 0)]
        tx, ty = q[0] - o[0], q[1] - o[1]
        nt = math.hypot(tx, ty)
        hx, hy = -ty / nt, tx / nt               # normale horizontale
        for j in range(m):
            a = 2 * math.pi * j / m
            pts.append((p[0] + r * math.cos(a) * hx, p[1] + r * math.cos(a) * hy, p[2] + r * math.sin(a)))
    for k in range(len(ligne) - 1):
        for j in range(m):
            a, b = k * m + j, k * m + (j + 1) % m
            faces.append([a, b, b + m, a + m])
    faces.append(list(range(m))[::-1])
    faces.append([(len(ligne) - 1) * m + j for j in range(m)])
    return pts, faces


def cylindre(x, y, z0, z1, r, m=24):
    pts = [(x + r * math.cos(2 * math.pi * j / m), y + r * math.sin(2 * math.pi * j / m), z) for z in (z0, z1)
           for j in range(m)]
    faces = [[j, (j + 1) % m, m + (j + 1) % m, m + j] for j in range(m)]
    faces += [list(range(m))[::-1], [m + j for j in range(m)]]
    return pts, faces


def nappe(bas, haut):
    """Surface entre deux arcs de même nombre de points."""
    pts = bas + haut
    n = len(bas)
    return pts, [[k, k + 1, n + k + 1, n + k] for k in range(n - 1)]


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


def greement(dossier):
    mats, vergues, voiles = [], [], []
    cordes = [c for _, c in fc.PANNEAUX]
    limites = [fc.Z_PIED - sum(h for h, _ in fc.PANNEAUX[:k]) for k in range(len(fc.PANNEAUX) + 1)]   # 6 limites
    for nom_cas, x in fc.X_MATS.items():
        nom = nom_cas.replace("mat_", "")
        d, n = corde(dossier, nom, x)
        mats.append(cylindre(x, 0.0, Z_PONT, Z_TETE, R_MAT))
        for k, z in enumerate(limites):           # six vergues : une à chaque limite de panneau
            c = max(cordes[max(k - 1, 0)], cordes[min(k, len(cordes) - 1)])
            vergues.append(tube(arc(x, d, n, c, z), R_VERGUE))
        for k, c in enumerate(cordes):            # cinq voiles creuses, entre deux vergues
            voiles.append(nappe(arc(x, d, n, c, limites[k]), arc(x, d, n, c, limites[k + 1])))
    return mats, vergues, voiles, len(limites)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Gréement d'habillage (mâts, vergues courbes, voiles creuses), VTK.")
    ap.add_argument("--sortie", default=os.path.join(ICI, "sorties"))
    a = ap.parse_args()
    try:
        mats, vergues, voiles, nv = greement(a.sortie)
    except (OSError, ValueError) as e:
        sys.exit("Surface de calcul illisible dans %s (%s) : lancez d'abord bash lancer.sh." % (a.sortie, e))
    t = " (ENSM, habillage, hypothese d'ecole)"
    ecrire_vtk(os.path.join(a.sortie, "mats.vtk"), "mats" + t, mats)
    ecrire_vtk(os.path.join(a.sortie, "vergues.vtk"), "vergues courbes" + t, vergues)
    ecrire_vtk(os.path.join(a.sortie, "voiles.vtk"), "voiles creuses" + t, voiles)
    print("mats.vtk, vergues.vtk (%d par mât), voiles.vtk écrits dans %s" % (nv, a.sortie))
