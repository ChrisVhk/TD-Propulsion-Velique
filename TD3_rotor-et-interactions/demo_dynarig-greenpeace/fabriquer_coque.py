#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coque et superstructures du navire de la démonstration DynaRig du TD 3 (EGN-S7, ENSM) : fichiers .vtk pour ParaView,
et aires projetées pour le fardage (fardage.py). COUCHE D'HABILLAGE : le calcul (lancer.sh, ligne portante) n'en dépend
pas ; l'outil ne voit que le pont, en plan de symétrie.

    python3 fabriquer_coque.py [--sortie DOSSIER]     # défaut : sorties/ de ce dossier

Fichiers écrits : coque.vtk (bordé et fond, couleur sombre), pont.vtk (clair), pavois.vtk, ceinture-glace.vtk,
superstructures.vtk (blanches). Python seul, sans module à installer.

CHIFFRES PUBLIÉS (relus le 26/11/2026, voir README.md) : longueur 74,95 m (Foundation Zero ; 75,00 m chez le chantier
Freire), largeur 13,35 m, tirant d'eau 5,5 m ; navire de classe glace (Polar Class 7, chantier Freire ; « ice-class
vessel », Dykstra). Tout le reste est une HYPOTHÈSE D'ÉCOLE (aucun plan n'est publié ; ce n'est pas le navire réel) :
  - carène : la Série 60, carène mère C_B = 0,65 (Todd, 1963, domaine public), celle du caboteur des TD 1 et 2, reprise
    telle qu'elle est publiée dans communs/caboteur-serie60.vtk (construite par communs/construire_coque_serie60.py) et
    mise à l'échelle par morceaux : longueur 110 -> 74,95 m, largeur 17,5 -> 13,35 m, sous la flottaison 6,5 -> 5,5 m,
    au-dessus 2,5 -> 3,0 m (franc-bord de l'hypothèse, même valeur que fabriquer_cas.py). Le navire réel n'a pas cette
    forme : la Série 60 est une carène de cargo d'essais ;
  - pont plat à 3,0 m au-dessus de l'eau ; pavois de 1,0 m de haut sur tout le pourtour du pont ;
  - « classe glace » SUGGÉRÉE par une ceinture plus sombre à la flottaison, sur le quart avant (de 1,0 m sous l'eau à
    1,2 m au-dessus) : aucune forme d'étrave réelle n'est représentée ;
  - superstructures en deux blocs : un rouf bas entre les mâts (24 m × 10 m × 2,6 m de haut, sous le pied de la voilure
    à 4 m au-dessus du pont) et une timonerie sur deux niveaux à l'arrière du mât arrière (8 m × 10 m × 5,6 m), en
    dehors du balayage des vergues. Positions et tailles INVENTÉES (session 16 b), gardées en session 17 : rien n'est
    relevé sur un rendu publié (README.md) ;
  - embarcations, plate-forme d'envol, garde-corps, apparaux : non représentés.
Repère : celui du navire dans CN-AeroModels (x vers l'avant, y vers tribord, z vers le bas, origine au milieu, à la
flottaison), comme les sorties .vtk de l'outil : la coque se superpose aux voiles dans ParaView.
Session 16 b : coque en parallélépipède effilé ; session 17 (ARB-EGN-S7-072) : Série 60, pont, pavois, ceinture.
ENSM (Christophe VANHORICK), 26/11/2026, Apache 2.0.
"""
import argparse
import collections
import os

ICI = os.path.dirname(os.path.abspath(__file__))
SERIE60 = os.path.join(ICI, "..", "..", "communs", "caboteur-serie60.vtk")
L0, B0, T0, F0 = 110.0, 17.5, 6.5, 2.5          # caboteur de communs/ (franc-bord 2,5 m : D = 9,0 m)
L, B, T, FRANC_BORD = 74.95, 13.35, 5.5, 3.0
PAVOIS = 1.0                                     # m, hauteur du pavois au-dessus du pont (hypothèse)
CEINTURE = (-1.2, 1.0, L / 4.0)                  # z haut, z bas (NED) et longueur depuis l'étrave (suggestion)
X_AV, X_AR = L / 2.0, -L / 2.0
# Blocs : (nom, x_min, x_max, demi-largeur, z_bas (hauteur au-dessus de l'eau), hauteur)
BLOCS = [("rouf", -12.0, 12.0, 5.0, FRANC_BORD, 2.6),
         ("timonerie", -34.0, -26.0, 5.0, FRANC_BORD, 5.6)]


def lire_vtk(chemin):
    """Points et triangles d'un .vtk POLYDATA ASCII (celui de communs/)."""
    mots = open(chemin, encoding="ascii").read().split()
    i = mots.index("POINTS")
    n = int(mots[i + 1])
    v = mots[i + 3:i + 3 + 3 * n]
    pts = [(float(v[3 * k]), float(v[3 * k + 1]), float(v[3 * k + 2])) for k in range(n)]
    j = mots.index("POLYGONS")
    m = int(mots[j + 1])
    f, k = [], j + 3
    for _ in range(m):
        c = int(mots[k])
        f.append([int(x) for x in mots[k + 1:k + 1 + c]])
        k += 1 + c
    return pts, f


def echelle(p):
    """Mise à l'échelle par morceaux : z > 0 (sous l'eau, NED) par T/T0, z < 0 (au-dessus) par F/F0."""
    x, y, z = p
    return (x * L / L0, y * B / B0, z * (T / T0 if z > 0 else FRANC_BORD / F0))


def coque():
    """Morceaux de la Série 60 à l'échelle : (bordé et fond, pont, ceinture glace), et contour du pont."""
    pts0, tri = lire_vtk(SERIE60)
    pts = [echelle(p) for p in pts0]
    z_pont = -FRANC_BORD
    bord, pont, ceint = [], [], []
    for t in tri:
        zs = [pts[k][2] for k in t]
        xc = sum(pts[k][0] for k in t) / 3.0
        zc = sum(zs) / 3.0
        if all(abs(z - z_pont) < 1e-6 for z in zs):
            pont.append(t)
        elif CEINTURE[0] <= zc <= CEINTURE[1] and xc >= X_AV - CEINTURE[2]:
            ceint.append(t)
        else:
            bord.append(t)
    demi = collections.defaultdict(float)          # contour du pont : demi-largeur par abscisse
    for p in pts:
        if abs(p[2] - z_pont) < 1e-6:
            demi[round(p[0], 4)] = max(demi[round(p[0], 4)], abs(p[1]))
    contour = sorted(demi.items())
    return (pts, bord), (pts, pont), (pts, ceint), contour


def pavois(contour):
    """Bande verticale de PAVOIS m au-dessus du pont, le long du contour (tribord, bâbord, étrave, tableau)."""
    z0, z1 = -FRANC_BORD, -FRANC_BORD - PAVOIS
    tour = [(x, y) for x, y in contour] + [(x, -y) for x, y in reversed(contour)]   # tribord AR->AV, bâbord AV->AR
    pts, faces = [], []
    for x, y in tour:
        pts += [(x, y, z0), (x, y, z1)]
    n = len(tour)
    for k in range(n):
        a, b = 2 * k, 2 * ((k + 1) % n)
        faces.append([a, b, b + 1, a + 1])
    return pts, faces


def bloc(x0, x1, dy, z_bas, h):
    pts = [(x, y, -z) for z in (z_bas, z_bas + h) for x, y in ((x0, -dy), (x1, -dy), (x1, dy), (x0, dy))]
    faces = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    return pts, faces


def ecrire_vtk(chemin, titre, morceaux):
    """Écrit des morceaux (points, faces) ; seuls les points utilisés sont gardés."""
    pts, faces = [], []
    for p, f in morceaux:
        utiles = sorted({i for face in f for i in face})
        nouveau = {i: len(pts) + k for k, i in enumerate(utiles)}
        pts += [p[i] for i in utiles]
        faces += [[nouveau[i] for i in face] for face in f]
    with open(chemin, "w", newline="\n") as fh:
        fh.write("# vtk DataFile Version 3.0\n%s\nASCII\nDATASET POLYDATA\n" % titre)
        fh.write("POINTS %d float\n" % len(pts))
        fh.writelines("%.4f %.4f %.4f\n" % p for p in pts)
        fh.write("POLYGONS %d %d\n" % (len(faces), sum(len(f) + 1 for f in faces)))
        fh.writelines("%d %s\n" % (len(f), " ".join(map(str, f))) for f in faces)


def aires():
    """Paramètres de Fujiwara et al. (2005, Fig. 2) tirés de la géométrie ci-dessus (hauteurs au-dessus de l'eau).
    Coque vue de côté : la Série 60 s'arrête aux perpendiculaires, sections planes, sans tonture : un rectangle
    L × franc-bord, comme la coque de la session 16 b ; le pavois l'élève de PAVOIS m sur toute la longueur."""
    h_coque = FRANC_BORD + PAVOIS
    morceaux = [(L * h_coque, 0.0, h_coque / 2.0)]    # (aire, x du centre, hauteur du centre)
    a_od = 0.0
    for _, x0, x1, dy, zb, h in BLOCS:
        a = (x1 - x0) * h
        a_od += a
        morceaux.append((a, (x0 + x1) / 2.0, zb + h / 2.0))
    a_l = sum(a for a, _, _ in morceaux) - sum((x1 - x0) * PAVOIS for _, x0, x1, _, _, _ in BLOCS)  # recouvrement
    c = (sum(a * x for a, x, _ in morceaux) - sum((x1 - x0) * PAVOIS * (x0 + x1) / 2 for _, x0, x1, _, _, _ in BLOCS)) / a_l
    h_c = (sum(a * z for a, _, z in morceaux)
           - sum((x1 - x0) * PAVOIS * (FRANC_BORD + PAVOIS / 2) for _, x0, x1, _, _, _ in BLOCS)) / a_l
    # aire frontale : coque et pavois + la plus haute des superstructures au-dessus du pavois (projections recouvertes)
    larg = max(2 * dy for _, _, _, dy, _, _ in BLOCS)
    h_max = max(zb + h for _, _, _, _, zb, h in BLOCS)
    a_f = B * h_coque + larg * (h_max - h_coque)
    return dict(L_OA=L, B=B, A_F=a_f, A_L=a_l, A_OD=a_od, C=c, H_C=h_c, H_BR=h_max)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Coque (Série 60 à l'échelle), pont, pavois, superstructures (VTK) ; aires.")
    ap.add_argument("--sortie", default=os.path.join(ICI, "sorties"))
    a = ap.parse_args()
    os.makedirs(a.sortie, exist_ok=True)
    bord, pont, ceint, contour = coque()
    t = " (ENSM, Serie 60 a l'echelle, hypothese d'ecole)"
    ecrire_vtk(os.path.join(a.sortie, "coque.vtk"), "coque" + t, [bord])
    ecrire_vtk(os.path.join(a.sortie, "pont.vtk"), "pont" + t, [pont])
    ecrire_vtk(os.path.join(a.sortie, "ceinture-glace.vtk"), "ceinture glace suggeree" + t, [ceint])
    ecrire_vtk(os.path.join(a.sortie, "pavois.vtk"), "pavois" + t, [pavois(contour)])
    ecrire_vtk(os.path.join(a.sortie, "superstructures.vtk"), "superstructures en blocs (ENSM, hypothese d'ecole)",
               [bloc(x0, x1, dy, zb, h) for _, x0, x1, dy, zb, h in BLOCS])
    print("coque.vtk, pont.vtk, ceinture-glace.vtk, pavois.vtk et superstructures.vtk écrits dans", a.sortie)
    print(" ; ".join("%s = %.2f" % kv for kv in aires().items()))
