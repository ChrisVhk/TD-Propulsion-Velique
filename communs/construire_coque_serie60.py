# -*- coding: utf-8 -*-
"""
Coque du caboteur pour la vue ParaView du TD 1 (session 11 i, ARB-EGN-S7-033 à 035).

Géométrie : Série 60, carène mère C_B = 0,65 (modèle 4211W), table 4 de
    F. H. Todd, « Series 60 — Methodical experiments with models of single-screw merchant ships »,
    David Taylor Model Basin, Report 1712, juillet 1963 (domaine public ; scan Internet Archive
    `methodicalexperi00todd`, Biodiversity Heritage Library, DOI 10.5962/bhl.title.47452),
    page 52 du PDF (page V-8 du rapport). Particularités du modèle 4211W : table 2, page 19 du PDF (page IV-1).
mise à l'échelle du caboteur d'école d'EGN-S9 (L = 110 m, B = 17,5 m, T = 6,5 m, D = 9,0 m), en NED :
étrave (FP) en x = +55 m, perpendiculaire arrière (AP) en x = -55 m, flottaison en z = 0, quille en z = +6,5 m,
pont en z = -2,5 m (ARB-EGN-S7-035). La Série 60 n'a pas de bulbe (rapport, chap. IV, § f) : la coque non plus.

Deux usages :
  python3 construire_coque_serie60.py --pdf DTMB-1712_Todd-1963_Series60.pdf
      relève la table 4 dans la couche texte du PDF (pdftotext), deux fois (-layout et -bbox), applique les
      corrections d'OCR listées dans CORRECTIONS_OCR (chacune vérifiée sur l'image de la page), compare les deux
      relevés, fait la relecture automatique (contrôles), écrit serie60_cb065_table4.csv, puis construit la coque ;
  python3 construire_coque_serie60.py
      repart du relevé versionné serie60_cb065_table4.csv (sans le PDF), refait les contrôles et construit la coque.
Sorties : --vtk (défaut : caboteur-serie60.vtk dans ce dossier) et serie60_verification.json (contrôles et
vérification chiffrée : L, B, T, D relus sur la surface, volume sous z = 0, C_B recalculé). La coque publiée est
communs/caboteur-serie60.vtk du dépôt public TD-Propulsion-Velique (session 17 ; avant : cas/aile-caboteur/) ; pour la
mettre à jour : --vtk ~/Work_ENSM/TD-Propulsion-Velique/communs/caboteur-serie60.vtk.

Ce que la coque ne reproduit pas (non tabulé dans la table 4) : l'étrave en avant de FP et la voûte arrière en
arrière de AP au-dessus de la flottaison (contours de la figure 11 du rapport, graphiques), la tonture et le
dévers du pont : la coque s'arrête aux perpendiculaires (sections planes en FP et en AP) et le pont est plat.
Aucune donnée D-ICE. Script ENSM, Apache 2.0 ; la table relevée est du domaine public.
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys

import numpy as np
from scipy.interpolate import PchipInterpolator

ICI = os.path.dirname(os.path.abspath(__file__))
PAGE = 52                                     # page du PDF (V-8 du rapport)
STATIONS = ["FP", "1/2", "1", "1 1/2"] + [str(k) for k in range(2, 18)] + ["18", "18 1/2", "19", "19 1/2", "AP"]
S_NUM = [0.0, 0.5, 1.0, 1.5] + [float(k) for k in range(2, 18)] + [18.0, 18.5, 19.0, 19.5, 20.0]
COLONNES = ["Tan.", "0.075", "0.25", "0.50", "0.75", "1.00", "1.25", "1.50"]
H_WL = [0.0, 0.075, 0.25, 0.50, 0.75, 1.00, 1.25, 1.50]   # hauteur au-dessus de la ligne de base / T ; Tan. = base
# Corrections d'OCR (complément du 22/11, 11 h 10), chacune vérifiée sur l'image de la page à 400 dpi (session 11 i).
# (station, colonne) : (lu, corrigé, raison)
CORRECTIONS_OCR = {
    ("FP", "0.75"): ("9.000", "0.000", "zéro mal imprimé ; toute la ligne FP est nulle jusqu'à W.L. 1.00 "
                                       "(le complément le situait en W.L. 1.00 : il est en W.L. 0.75)"),
    ("5", "Tan."): ("9.408", "0.408", "zéro mal imprimé ; 0.239 (station 4) < 0.408 < 0.604 (station 6)"),
}
# Table 2 du rapport (modèle 4211W) : valeurs publiées pour la relecture automatique.
PUBLIE = {"C_B": 0.650, "C_X": 0.982, "C_P": 0.661, "C_PF": 0.651, "C_PA": 0.672, "C_W": 0.746,
          "LCB_pct_LBP_arriere": 0.5, "K_R": 0.205}
# Caboteur d'école d'EGN-S9 (Cours/EGN-S9_Performances-Navire/01_Navire-Nomenclature.md, fil rouge).
L, B, T, D = 110.0, 17.5, 6.5, 9.0
C_B_CABOTEUR = 0.66


# ------------------------------------------------------------------ relevé A : pdftotext -layout
def releve_layout(pdf):
    txt = subprocess.run(["pdftotext", "-layout", "-f", str(PAGE), "-l", str(PAGE), pdf, "-"],
                         capture_output=True, text=True, check=True).stdout
    lignes = txt.splitlines()
    debut = next(i for i, l in enumerate(lignes) if "Table 4" in l)
    rangs, max_hb, libelles = [], None, []
    for l in lignes[debut:]:
        nombres = re.findall(r"\d\.\d{3}", l)
        if l.strip().startswith("Max. half beam"):
            max_hb = nombres
            break
        if len(nombres) == 9:
            libelles.append(l[:l.index(nombres[0])].strip())
            rangs.append(nombres)
    return rangs, max_hb, libelles


# ------------------------------------------------------------------ relevé B : pdftotext -bbox (mots et positions)
def releve_bbox(pdf):
    html = subprocess.run(["pdftotext", "-bbox", "-f", str(PAGE), "-l", str(PAGE), pdf, "-"],
                          capture_output=True, text=True, check=True).stdout
    mots = [(float(a), float(b), m) for a, b, m in
            re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)"[^>]*>([^<]*)</word>', html)]
    y_titre = next(y for x, y, m in mots if m == "4" and any(mm == "Table" and abs(yy - y) < 3 and xx < x
                                                             for xx, yy, mm in mots))
    mots = [w for w in mots if w[1] > y_titre]
    # Colonnes : abscisses des en-têtes de la ligne d'en-tête (Tan., 0.075 ... 1.50)
    y_tan = next(y for x, y, m in mots if m == "Tan.")
    entetes = sorted((x, m) for x, y, m in mots if abs(y - y_tan) < 3 and re.fullmatch(r"Tan\.|\d\.\d{2,3}", m))
    xs = [x for x, _ in entetes]
    # Rangées : mots numériques regroupés par ordonnée voisine (le scan penche : quelques dixièmes de point d'écart).
    nums = sorted((y, x, m) for x, y, m in mots if y > y_tan + 3 and re.fullmatch(r"\d[./]\d{3}", m))
    groupes = []
    for y, x, m in nums:
        if groupes and y - groupes[-1][0] < 2.0:
            groupes[-1][1].append((x, m))
        else:
            groupes.append([y, [(x, m)]])
    lignes = [[m for _, m in sorted(cel)] for _, cel in groupes]
    # Une rangée = 9 valeurs (8 lignes d'eau + aire), la dernière (Max. half beam) en a 8.
    return [l for l in lignes if len(l) == 9], [l for l in lignes if len(l) == 8], xs


def corriger(rangs_bruts):
    """Applique CORRECTIONS_OCR ; renvoie les valeurs corrigées (float) et la liste des corrections faites."""
    faites, table = [], []
    for st, rang in zip(STATIONS, rangs_bruts):
        vals = list(rang)
        for j, col in enumerate(COLONNES):
            c = CORRECTIONS_OCR.get((st, col))
            if c:
                if vals[j] != c[0]:
                    sys.exit(f"Correction attendue introuvable : station {st}, {col} lu {vals[j]} (attendu {c[0]})")
                vals[j] = c[1]
                faites.append({"station": st, "colonne": col, "lu": c[0], "corrige": c[1], "raison": c[2]})
        table.append([float(v) for v in vals])
    return np.array(table), faites


# ------------------------------------------------------------------ relecture automatique
def section_y(f, mhb, row):
    """Demi-largeurs absolues (fraction de B/2) d'une station aux hauteurs H_WL."""
    return np.array(row[:8]) * np.array(mhb)


def aire_section(y_frac, h_max=1.0, n=2001):
    """Aire de la section jusqu'à h_max·T, en fraction de B·T (interpolation monotone en hauteur)."""
    hh = np.linspace(0.0, h_max, n)
    yy = PchipInterpolator(H_WL, y_frac)(hh)
    return np.trapezoid(yy, hh)   # (2·∫ y dh)/(B·T) avec y en fraction de B/2 : 2·(B/2)·T/(B·T) = 1


def controles(table, mhb):
    res = {"violations": []}
    v = res["violations"]
    # 1. bornes : 0 <= f <= 1 (demi-largeur <= demi-largeur max de la ligne d'eau <= B/2)
    for i, st in enumerate(STATIONS):
        for j, col in enumerate(COLONNES + ["aire"]):
            if not 0.0 <= table[i, j] <= 1.0:
                v.append(f"hors [0, 1] : station {st}, {col} = {table[i, j]}")
    if not all(0.0 < m <= 1.0 for m in mhb):
        v.append("Max. half beam hors ]0, 1]")
    # 2. symétrie : la table est une demi-coque ; la symétrie est vérifiée sur la surface construite (miroir exact).
    # 3. monotonie en hauteur : demi-largeur absolue non décroissante de la quille au pont (pas de rentrée), tolérance
    #    0,002 B/2 (station 8 : 0.996 en W.L. 0.50, 0.995 en W.L. 0.75, imprimé tel quel).
    for i, st in enumerate(STATIONS):
        y = section_y(None, mhb, table[i])
        for k in range(7):
            if y[k + 1] < y[k] - 0.002:
                v.append(f"demi-largeur décroissante en montant : station {st}, {COLONNES[k]} -> {COLONNES[k + 1]}")
    res["tolerance_monotonie_hauteur"] = 0.002
    # 4. monotonie en longueur : chaque ligne d'eau croît de FP jusqu'au maximum puis décroît jusqu'à AP
    for j, col in enumerate(COLONNES + ["aire"]):
        c = table[:, j]
        k = int(np.argmax(c))
        if np.any(np.diff(c[:k + 1]) < -1e-9) or np.any(np.diff(c[k:]) > 1e-9):
            v.append(f"ligne d'eau {col} non unimodale de FP à AP")
    # 5. aire de chaque section (jusqu'à W.L. 1.00) recalculée sur les cotes, contre la colonne « Area »
    aires = np.array([aire_section(section_y(None, mhb, table[i])) for i in range(len(STATIONS))])
    c_x = aires[STATIONS.index("10")]
    frac = aires / c_x
    ecart = frac - table[:, 8]
    res["aire_section_max_ecart"] = float(np.max(np.abs(ecart)))
    res["aire_section_station_max_ecart"] = STATIONS[int(np.argmax(np.abs(ecart)))]
    for i, st in enumerate(STATIONS):
        if abs(ecart[i]) > 0.015:
            v.append(f"aire de section recalculée {frac[i]:.3f} contre {table[i, 8]:.3f} publiée : station {st}")
    res["C_X_recalcule"] = float(c_x)
    if abs(c_x - PUBLIE["C_X"]) > 0.005:
        v.append(f"C_X recalculé {c_x:.4f} contre {PUBLIE['C_X']} publié")
    # 6. coefficients de forme intégrés sur la colonne « Area » (stations), contre la table 2
    s = np.array(S_NUM)
    a = table[:, 8]
    cp = np.trapezoid(PchipInterpolator(s, a)(np.linspace(0, 20, 4001)), np.linspace(0, 20, 4001)) / 20
    sf = np.linspace(0, 10, 2001); sa = np.linspace(10, 20, 2001)
    cpf = np.trapezoid(PchipInterpolator(s, a)(sf), sf) / 10
    cpa = np.trapezoid(PchipInterpolator(s, a)(sa), sa) / 10
    wl = table[:, 5] * mhb[5]
    cw = np.trapezoid(PchipInterpolator(s, wl)(np.linspace(0, 20, 4001)), np.linspace(0, 20, 4001)) / 20
    ss = np.linspace(0, 20, 4001)
    lcb = np.trapezoid(PchipInterpolator(s, a)(ss) * (ss - 10), ss) / np.trapezoid(PchipInterpolator(s, a)(ss), ss)
    res.update(C_P_colonne_aire=float(cp), C_PF=float(cpf), C_PA=float(cpa), C_W=float(cw),
               C_B_colonne_aire_x_C_X_publie=float(cp * PUBLIE["C_X"]),
               LCB_pct_LBP_arriere=float(lcb / 20 * 100))
    for cle, val, tol in (("C_P", cp, 0.005), ("C_PF", cpf, 0.005), ("C_PA", cpa, 0.005), ("C_W", cw, 0.005)):
        if abs(val - PUBLIE[cle]) > tol:
            v.append(f"{cle} recalculé {val:.4f} contre {PUBLIE[cle]} publié")
    if abs(lcb / 20 * 100 - PUBLIE["LCB_pct_LBP_arriere"]) > 0.2:
        v.append(f"LCB recalculé {lcb / 20 * 100:.2f} % LBP contre 0,5 % publié")
    # 7. bouchain : rayon publié K_R = R/sqrt(B·H) (modèle : B/H = 2,50) ; demi-largeur au pied et en W.L. 0.075
    bb, hh = 55.17, 22.09
    r = PUBLIE["K_R"] * np.sqrt(bb * hh)
    y_tan = (bb / 2 - r) / (bb / 2)
    y_075 = (bb / 2 - r + np.sqrt(r * r - (r - 0.075 * hh) ** 2)) / (bb / 2)
    res["bouchain_cercle_modele"] = {"R_ft": float(r), "Tan_calcule": float(y_tan), "Tan_publie": mhb[0],
                                     "WL0075_calcule": float(y_075), "WL0075_publie": mhb[1]}
    if abs(y_tan - mhb[0]) > 0.02 or abs(y_075 - mhb[1]) > 0.02:
        v.append("bouchain : demi-largeurs de Max. half beam incohérentes avec le rayon publié")
    res["conforme"] = not v
    return res


# ------------------------------------------------------------------ surface
def surface(table, mhb, ns=81, n_bas=11, n_haut=31):
    """Grille demi-largeur y(s, h) interpolée (PCHIP en hauteur puis en longueur), fermée au pont (h = D/T)."""
    h_pont = D / T
    # Les lignes d'eau de la table (dont la flottaison h = 1) sont des niveaux exacts de la grille.
    hh = np.unique(np.concatenate([np.linspace(0.0, 0.25, n_bas), np.linspace(0.25, h_pont, n_haut),
                                   [h for h in H_WL if h <= h_pont]]))
    hh = hh[np.concatenate([[True], np.diff(hh) > 1e-6])]
    y_st = np.array([PchipInterpolator(H_WL, section_y(None, mhb, table[i]))(hh) for i in range(len(STATIONS))])
    ss = np.linspace(0.0, 20.0, ns)
    y = PchipInterpolator(np.array(S_NUM), y_st, axis=0)(ss)
    return ss, hh, np.clip(y, 0.0, 1.0)


def maillage(ss, hh, y):
    """Points (NED) et triangles d'une coque fermée : bordé tribord et bâbord, fond plat, pont, sections FP et AP.
    Orientation : normales vers l'extérieur."""
    xs = L / 2 - ss * L / 20          # FP (s = 0) en x = +55 m, AP (s = 20) en x = -55 m
    zs = T - hh * T                   # quille z = +T (vers le bas en NED), pont z = T - D
    ns, nh = y.shape
    pts, idx = [], {}

    def p(i, j, cote):
        cle = (i, j, cote)
        if cle not in idx:
            idx[cle] = len(pts)
            pts.append((xs[i], cote * y[i, j] * B / 2, zs[j]))
        return idx[cle]

    tri = []

    def quad(a, b, c, d):            # a-b-c-d dans le sens direct vu de l'extérieur
        tri.append((a, b, c)); tri.append((a, c, d))

    for i in range(ns - 1):
        for j in range(nh - 1):
            # tribord (+y) : vu de l'extérieur (+y), x vers la gauche... ordre fixé puis vérifié par le volume signé
            quad(p(i, j, 1), p(i + 1, j, 1), p(i + 1, j + 1, 1), p(i, j + 1, 1))
            quad(p(i, j, -1), p(i, j + 1, -1), p(i + 1, j + 1, -1), p(i + 1, j, -1))
        # fond (h = 0) et pont (h = D/T)
        quad(p(i, 0, -1), p(i + 1, 0, -1), p(i + 1, 0, 1), p(i, 0, 1))
        quad(p(i, nh - 1, 1), p(i + 1, nh - 1, 1), p(i + 1, nh - 1, -1), p(i, nh - 1, -1))
    for j in range(nh - 1):          # sections planes en FP (i = 0) et AP (i = ns-1)
        quad(p(0, j, 1), p(0, j + 1, 1), p(0, j + 1, -1), p(0, j, -1))
        quad(p(ns - 1, j, -1), p(ns - 1, j + 1, -1), p(ns - 1, j + 1, 1), p(ns - 1, j, 1))
    pts = np.array(pts)
    tri = np.array(tri)
    # Orientation : volume signé (théorème de flux) positif = normales sortantes ; sinon, on retourne tout.
    if volume_signe(pts, tri) < 0:
        tri = tri[:, ::-1]
    # Triangles dégénérés (demi-largeur nulle de part et d'autre de l'axe) : retirés.
    a = np.linalg.norm(np.cross(pts[tri[:, 1]] - pts[tri[:, 0]], pts[tri[:, 2]] - pts[tri[:, 0]]), axis=1)
    return pts, tri[a > 1e-10]


def volume_signe(pts, tri):
    p0, p1, p2 = pts[tri[:, 0]], pts[tri[:, 1]], pts[tri[:, 2]]
    return float(np.sum(np.einsum("ij,ij->i", p0, np.cross(p1, p2))) / 6.0)


def volume_sous_flottaison(pts, tri):
    """Volume de la coque fermée sous la flottaison (z >= 0 en NED), par le flux de (0, 0, z) à travers la surface
    découpée au plan z = 0 (le couvercle z = 0 n'apporte rien) : V = somme des aires projetées signées x z moyen."""
    vol = 0.0
    for t in tri:
        poly = [pts[k] for k in t]
        dec = []                                        # Sutherland-Hodgman, demi-espace z >= 0
        for k in range(3):
            a, b = poly[k], poly[(k + 1) % 3]
            if a[2] >= 0:
                dec.append(a)
            if (a[2] >= 0) != (b[2] >= 0):
                u = a[2] / (a[2] - b[2])
                dec.append(a + u * (b - a))
        for k in range(1, len(dec) - 1):
            q0, q1, q2 = dec[0], dec[k], dec[k + 1]
            n_z = 0.5 * ((q1[0] - q0[0]) * (q2[1] - q0[1]) - (q1[1] - q0[1]) * (q2[0] - q0[0]))
            vol += n_z * (q0[2] + q1[2] + q2[2]) / 3.0
    return vol


def ecrire_vtk(chemin, pts, tri):
    with open(chemin, "w", encoding="ascii", newline="\n") as f:
        f.write("# vtk DataFile Version 4.2\n")
        f.write("Caboteur : Serie 60 C_B 0.65 (Todd 1963, DTMB 1712, table 4), L 110 B 17.5 T 6.5 D 9.0 m, NED\n")
        f.write("ASCII\nDATASET POLYDATA\n")
        f.write(f"POINTS {len(pts)} double\n")
        for x, y, z in pts:
            f.write(f"{x:.4f} {y:.4f} {z:.4f}\n")
        f.write(f"POLYGONS {len(tri)} {4 * len(tri)}\n")
        for a, b, c in tri:
            f.write(f"3 {a} {b} {c}\n")


def lire_csv(chemin):
    with open(chemin, encoding="utf-8") as f:
        rangs = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    entete, corps = rangs[0], rangs[1:]
    table = np.array([[float(v) for v in r[2:11]] for r in corps if r[0] != "Max. half beam"])
    mhb = [float(v) for v in next(r for r in corps if r[0] == "Max. half beam")[2:10]]
    return table, mhb


def ecrire_csv(chemin, table, mhb, faites):
    with open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Série 60, carène mère C_B = 0,65, modèle 4211W : table 4 de Todd (1963), DTMB Report 1712, page V-8\n")
        f.write("# (page 52 du PDF Internet Archive methodicalexperi00todd ; BHL, DOI 10.5962/bhl.title.47452), "
                "domaine public.\n")
        f.write("# Demi-largeurs en fraction de la demi-largeur maximale de chaque ligne d'eau ; dernière ligne : "
                "demi-largeur maximale de chaque ligne d'eau en fraction de B/2.\n")
        f.write("# Lignes d'eau en fraction du tirant d'eau T (W.L. 1.00 = flottaison de projet ; Tan. = ligne de "
                "base, la section maîtresse n'a pas d'acculement). Stations régulières sur LBP, FP = 0, AP = 20.\n")
        f.write("# « Area » : aire de la section jusqu'à W.L. 1.00, en fraction de l'aire maximale.\n")
        for c in faites:
            f.write(f"# Correction d'OCR (vérifiée sur l'image) : station {c['station']}, {c['colonne']} : "
                    f"lu {c['lu']}, retenu {c['corrige']} ({c['raison']}).\n")
        f.write("# Appel de note « a » sur « Max. half beam » : aucun texte de note sur les pages 51 à 54 du PDF.\n")
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["station", "s"] + COLONNES + ["Area"])
        for st, s, r in zip(STATIONS, S_NUM, table):
            w.writerow([st, f"{s:g}"] + [f"{v:.3f}" for v in r])
        w.writerow(["Max. half beam", ""] + [f"{v:.3f}" for v in mhb] + [""])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--pdf", help="rapport DTMB 1712 (PDF) : relevé de la table 4 dans sa couche texte")
    ap.add_argument("--csv", default=os.path.join(ICI, "serie60_cb065_table4.csv"))
    ap.add_argument("--vtk", default=os.path.join(ICI, "caboteur-serie60.vtk"))
    ap.add_argument("--json", default=os.path.join(ICI, "serie60_verification.json"))
    a = ap.parse_args()

    rapport = {"source": "Todd 1963, DTMB Report 1712, table 4 (modèle 4211W), page V-8 = page 52 du PDF",
               "publie_table2": PUBLIE}
    if a.pdf:
        rangs_a, mhb_a, libelles = releve_layout(a.pdf)
        rangs_b, mhb_b, _ = releve_bbox(a.pdf)
        if len(rangs_a) != 25 or len(rangs_b) != 25:
            sys.exit(f"Table incomplète : {len(rangs_a)} rangées (-layout), {len(rangs_b)} (-bbox), 25 attendues")
        diff = [(STATIONS[i], j) for i in range(25) for j in range(9) if rangs_a[i][j] != rangs_b[i][j]]
        diff += [("Max. half beam", j) for j in range(8) if mhb_a[j] != mhb_b[-1][j]]
        rapport["double_releve"] = {"rangees": 25, "cellules": 25 * 9 + 8, "differences_layout_bbox": diff,
                                    "libelles_lus": dict(zip(STATIONS, libelles))}
        # La relecture automatique sur le relevé brut doit trouver les erreurs d'OCR (preuve que les contrôles mordent).
        brut = np.array([[float(v) for v in r] for r in rangs_a])
        rapport["controles_releve_brut"] = controles(brut, [float(m) for m in mhb_a])["violations"]
        table, faites = corriger(rangs_a)
        mhb = [float(m) for m in mhb_a]
        rapport["corrections_ocr"] = faites
        ecrire_csv(a.csv, table, mhb, faites)
    else:
        table, mhb = lire_csv(a.csv)
    rapport["controles"] = controles(table, mhb)
    if not rapport["controles"]["conforme"]:
        print(json.dumps(rapport, ensure_ascii=False, indent=2))
        sys.exit("Relecture automatique non conforme : coque non construite.")

    ss, hh, y = surface(table, mhb)
    pts, tri = maillage(ss, hh, y)
    # Symétrie : chaque point (x, y, z) a son miroir (x, -y, z)
    cle = {(round(p[0], 6), round(p[1], 6), round(p[2], 6)) for p in pts}
    sym = all((round(p[0], 6), round(-p[1], 6), round(p[2], 6)) in cle for p in pts)
    v_total = volume_signe(pts, tri)
    v_carene = volume_sous_flottaison(pts, tri)
    # Volume par la grille (contrôle indépendant du maillage) : 2 ∫∫ y dh dx sous la flottaison
    hm = hh <= 1.0 + 1e-12
    v_grille = 2 * np.trapezoid(np.trapezoid(y[:, hm] * B / 2, hh[hm] * T, axis=1), ss * L / 20)
    lx, ly, lz = (pts[:, k].max() - pts[:, k].min() for k in range(3))
    mesure = {
        "L_m": float(pts[:, 0].max() - pts[:, 0].min()), "x_FP": float(pts[:, 0].max()), "x_AP": float(pts[:, 0].min()),
        "B_m": float(2 * pts[:, 1].max()), "y_min": float(pts[:, 1].min()), "y_max": float(pts[:, 1].max()),
        "T_m": float(pts[:, 2].max()), "D_m": float(pts[:, 2].max() - pts[:, 2].min()), "z_pont": float(pts[:, 2].min()),
        "symetrie_babord_tribord": sym, "points": int(len(pts)), "triangles": int(len(tri)),
        "volume_coque_fermee_m3": v_total, "volume_carene_sous_z0_m3": v_carene,
        "volume_carene_par_la_grille_m3": float(v_grille),
        "C_B_recalcule": v_carene / (L * B * T), "C_B_attendu_serie60": PUBLIE["C_B"],
        "C_B_caboteur_EGN_S9": C_B_CABOTEUR,
        "deplacement_t_rho1025": v_carene * 1.025,
        "ecart_volume_a_CB_066_pct": (v_carene / (C_B_CABOTEUR * L * B * T) - 1) * 100,
    }
    rapport["verification_chiffree"] = mesure
    ecrire_vtk(a.vtk, pts, tri)
    rapport["vtk"] = os.path.basename(a.vtk)
    with open(a.json, "w", encoding="utf-8") as f:
        json.dump(rapport, f, ensure_ascii=False, indent=2)
    print(json.dumps(rapport, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
