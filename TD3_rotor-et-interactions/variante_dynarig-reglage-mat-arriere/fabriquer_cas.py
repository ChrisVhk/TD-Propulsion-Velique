#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deux DynaRigs d'école sur un navire générique aux dimensions publiées du navire de Greenpeace — TD 3 (EGN-S7, ENSM),
démonstration de l'enseignant et variante V-DynaRig. Écrit les fichiers d'entrée de CN-AeroModels.

    python3 fabriquer_cas.py                       # les trois fichiers de la démonstration (ce dossier)
    python3 fabriquer_cas.py --elements 40 --avant -70 --arriere -60 --sortie essai.yml   # un fichier sur mesure

CHIFFRES PUBLIÉS (lus le 26/11/2026) : longueur 74,95 m, largeur 13,35 m, tirant d'eau 5,5 m, tirant d'air 57,85 m,
1 746 m² de voilure (Foundation Zero, « Greenpeace », 12/10/2026) ; deux mâts DynaRig tournants, 1 746 m²
(Dykstra Naval Architects, billet du 25/11/2026). Chiffres d'armateur et d'architecte, présentés comme tels.
Relus le 26/11/2026 (session 17) : 2 000 m² annoncés en 2024, au contrat (Southern Spars, contrat avec Greenpeace
International du 6 août 2024, « sail area of 2000 square metres, supplied by North Sails ») ; 1 746 m² publiés en 2026
(Foundation Zero ; chantier Freire). Deux mâts de 60 m chacun, construits par Southern Spars en Pologne (Yacht,
S. Gehlhaus, 15/08/2026) ; contre 57,85 m de tirant d'air, la longueur du mât compte sans doute sa partie sous le pont
(hypothèse). Voir README.md. On garde 1 746 m² ; 2 000 m² donneraient environ +15 %.

HYPOTHÈSES D'ÉCOLE (aucun plan de gréement n'est publié ; rien ici n'est le navire réel) :
  - voilure : 1 746 m² retenus, soit 873 m² par mât ; 2 000 m² (chiffre de 2024) donneraient environ +15 % ;
  - cinq panneaux par mât, de même hauteur (9,6 m) : trois bas identiques, deux hauts plus étroits, cordes dans le
    rapport 1 / 1 / 1 / 0,9 / 0,7 (forme décrite par M. Reche-Vilanova) : corde des panneaux bas 19,77 m ;
  - franc-bord 3,0 m ; pied de la voilure 4 m au-dessus du pont (écart de l'étude de Reche-Vilanova, J2) ; hauteur de
    voilure 48 m : sommet à 55 m au-dessus de l'eau, sous le tirant d'air publié (57,85 m) ;
    allongement H²/S = 48² / 873 = 2,64 par mât ;
  - deux mâts sur l'axe, à x = +15 m et x = −15 m du milieu (30 m, soit 1,5 corde) : sur 75 m, les vergues (±10 m
    autour du mât) restent dans la longueur et ne se croisent pas en tournant ;
  - pont en plan de symétrie (z = −3 m) : il fait miroir sous la voilure ; interaction avec la coque et les
    superstructures : aucune (non modélisée) ;
  - vent vrai de 12 m/s à 10 m, loi puissance d'exposant 0,143 (comme l'essai du 25/11), venant de tribord par le
    travers (TWA 90° ; direction 270° dans l'outil, celle vers laquelle souffle le vent) ; navire à 10 nœuds cap au
    nord ; vent apparent vers 70° à mi-hauteur de la voilure ;
  - la polaire n'est pas symétrique (voile cambrée) : à cette amure, la cambrure porte vers l'avant ; l'autre amure
    demanderait la polaire retournée ;
  - section : polaire d'école `plaque-cambree.yml` (fabriquer_polaire.py) ; ligne portante non linéaire (NLL).
  - le vent porte un bloc `output` (maillage de sortie, sans effet sur les efforts) : sans lui, CN-AeroModels v0.5.1
    s'arrête en erreur de segmentation avec `--vtk 1` et un vent en loi puissance (constaté le 26/11/2026).

Une ligne portante n'est pas validée pour un DynaRig : allongement < 4 (le LHEEA la valide surtout au-delà), voile
souple, mâts et vergues absents ; et Bordogna (2020) montre que le modèle à tourbillons en fer à cheval qu'il a testé ne
prédit pas correctement l'interaction entre deux DynaRigs. Ce cas montre ce que l'outil calcule, pas ce que fait le
navire. ENSM (Christophe VANHORICK), 26/11/2026, Apache 2.0.
"""
import argparse
import os

SURFACE_PAR_MAT = 1746.0 / 2.0
FRANC_BORD, JEU_PONT, H = 3.0, 4.0, 48.0
Z_PONT = -FRANC_BORD                     # repère du navire : z vers le bas, origine à la flottaison
Z_PIED = Z_PONT - JEU_PONT
RAPPORTS = (1.0, 1.0, 1.0, 0.9, 0.7)
H_PANNEAU = H / len(RAPPORTS)
CORDE = SURFACE_PAR_MAT / (H_PANNEAU * sum(RAPPORTS))
PANNEAUX = [(H_PANNEAU, CORDE * r) for r in RAPPORTS]
X_MATS = {"mat_avant": 15.0, "mat_arriere": -15.0}
TWS, Z_REF, ALPHA, VITESSE, DIRECTION = 12.0, 10.0, 0.143, 5.144, 270.0
ELEMENTS = 40                            # par mât : F_x à 1 % de 80 éléments au réglage de la démonstration
                                         # (10, 20, 40, 80 : +5 %, +2 %, +1 %) ; près du maximum de la polaire, rien ne converge
REGLAGE = -70.0                          # deg ; réglage de la démonstration : partie attachée de la polaire, où le
                                         # calcul converge (au réglage de poussée maximale, -55°, il ne converge pas)
POLAIRE = "plaque-cambree.yml"


def allongement():
    return H ** 2 / sum(h * c for h, c in PANNEAUX)


def elements(n_par_mat):
    n = n_par_mat // len(PANNEAUX)
    out, z = [], Z_PIED
    for h, c in PANNEAUX:
        dz = h / n
        out += [(z - dz * (k + 0.5), c) for k in range(n)]
        z -= h
    return out


def bloc_unite(nom, n_par_mat):
    l = ["          - name: %s" % nom, "            geometry: 3D", "            data:"]
    for i, (zc, c) in enumerate(elements(n_par_mat), start=1):
        l += ["              - element: %d" % i,
              "                center:",
              "                    x: {value: %s, unit: m}" % X_MATS[nom],
              "                    y: {value: 0., unit: m}",
              "                    z: {value: %.4f, unit: m}" % zc,
              "                chord: {value: %.4f, unit: m}" % c,
              "                foil data:",
              "                  - file: %s" % POLAIRE]
    return "\n".join(l)


def yml(n_par_mat=ELEMENTS, reglages=None, mats=("mat_avant", "mat_arriere")):
    reglages = reglages or {m: REGLAGE for m in mats}
    unites = "\n".join(bloc_unite(m, n_par_mat) for m in mats)
    cmds = "\n".join("  - name: %s\n    t: [0, 100]\n    setting: {unit: deg, values: [%s, %s]}"
                     % (m, reglages[m], reglages[m]) for m in mats)
    return f"""# Deux DynaRigs d'école sur un navire générique aux dimensions publiées du navire de Greenpeace (TD 3, ENSM).
# Fichier écrit par fabriquer_cas.py : hypothèses d'école en tête de ce script ; polaire d'école {POLAIRE}.
# {len(mats)} mât(s), {n_par_mat} éléments par mât, réglages : {", ".join("%s %s°" % (m, reglages[m]) for m in mats)}.
rotations convention: [psi, theta', phi'']

environmental constants:
    g: {{value: 9.8067, unit: m/s^2}}
    rho: {{value: 1025., unit: kg/m^3}}
    nu: {{value: 1.48e-5, unit: m^2/s}}
    air rho: {{value: 1.225, unit: kg/m^3}}

environment models:
  - model: power law wind profile
    velocity: {{unit: m/s, value: {TWS}}}
    direction: {{unit: deg, value: {DIRECTION}}}
    reference height: {{unit: m, value: {Z_REF}}}
    alpha: {ALPHA}
    output:
        frame of reference: NED
        mesh:
            xmin: {{value: -45., unit: m}}
            xmax: {{value: 45., unit: m}}
            nx: 7
            ymin: {{value: -20., unit: m}}
            ymax: {{value: 20., unit: m}}
            ny: 3
            zmin: {{value: 0., unit: m}}
            zmax: {{value: -58., unit: m}}
            nz: 6
  - model: no waves
    constant sea elevation in NED frame: {{value: 0, unit: m}}

bodies:
  - name: ship
    position of body frame relative to mesh:
        frame: mesh
        x: {{value: 0., unit: m}}
        y: {{value: 0, unit: m}}
        z: {{value: 0., unit: m}}
        phi: {{value: 3.1415926535, unit: rad}}
        theta: {{value: 0, unit: rad}}
        psi: {{value: 0, unit: rad}}
    initial position of body frame relative to NED:
        frame: NED
        x: {{value: 0., unit: m}}
        y: {{value: 0., unit: m}}
        z: {{value: 0., unit: m}}
        phi: {{value: 0, unit: rad}}
        theta: {{value: 0, unit: rad}}
        psi: {{value: 0, unit: rad}}
    initial velocity of body frame relative to NED:
        frame: ship
        u: {{value: {VITESSE}, unit: m/s}}
        v: {{value: 0, unit: m/s}}
        w: {{value: 0, unit: m/s}}
        p: {{value: 0, unit: rad/s}}
        q: {{value: 0, unit: rad/s}}
        r: {{value: 0, unit: rad/s}}
    dynamics:
        hydrodynamic forces calculation point in body frame:
            x: {{value: 0., unit: m}}
            y: {{value: 0., unit: m}}
            z: {{value: 0., unit: m}}
        centre of inertia:
            frame: ship
            x: {{value: 0, unit: m}}
            y: {{value: 0, unit: m}}
            z: {{value: 0., unit: m}}
        rigid body inertia matrix at the center of gravity and projected in the body frame:
            row 1: [1E6,0,0,0,0,0]
            row 2: [0,1E6,0,0,0,0]
            row 3: [0,0,1E6,0,0,0]
            row 4: [0,0,0,1E6,0,0]
            row 5: [0,0,0,0,1E6,0]
            row 6: [0,0,0,0,0,1E6]
        added mass matrix at the center of gravity and projected in the body frame:
            row 1: [0,0,0,0,0,0]
            row 2: [0,0,0,0,0,0]
            row 3: [0,0,0,0,0,0]
            row 4: [0,0,0,0,0,0]
            row 5: [0,0,0,0,0,0]
            row 6: [0,0,0,0,0,0]
    external forces:
      - model: nonlinear lifting line
        name: dynarig
        control: commands
        options:
            useAWSsquare: false
            useBentHorseshoeVortex: false
            verbose: false
        plane of symmetry:
            point:
                x: {{value: 0., unit: m}}
                y: {{value: 0., unit: m}}
                z: {{value: {Z_PONT}, unit: m}}
            normal vector:
                x: {{value: 0., unit: m}}
                y: {{value: 0., unit: m}}
                z: {{value: -1., unit: m}}
            frame: ship
        wind propulsion system:
{unites}

commands:
{cmds}
"""


FICHIERS = {"dynarig-deux-mats.yml": ("mat_avant", "mat_arriere"),
            "dynarig-mat-avant-seul.yml": ("mat_avant",),
            "dynarig-mat-arriere-seul.yml": ("mat_arriere",)}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Fichiers d'entrée du cas DynaRig d'école.")
    ap.add_argument("--elements", type=int, default=ELEMENTS, help="éléments par mât (multiple de 5)")
    ap.add_argument("--avant", type=float, help="réglage du mât avant (deg)")
    ap.add_argument("--arriere", type=float, help="réglage du mât arrière (deg)")
    ap.add_argument("--mats", default="mat_avant,mat_arriere")
    ap.add_argument("--sortie", help="un seul fichier, au lieu des trois de la démonstration")
    a = ap.parse_args()
    ici = os.path.dirname(os.path.abspath(__file__))
    if a.sortie:
        mats = tuple(a.mats.split(","))
        r = {"mat_avant": a.avant if a.avant is not None else REGLAGE,
             "mat_arriere": a.arriere if a.arriere is not None else REGLAGE}
        jobs = {a.sortie: (mats, r)}
    else:
        jobs = {f: (m, None) for f, m in FICHIERS.items()}
    for f, (mats, r) in jobs.items():
        with open(os.path.join(ici, f) if not os.path.isabs(f) else f, "w", newline="\n") as fh:
            fh.write(yml(a.elements, r, mats))
        print("écrit :", f)
    print("Voilure par mât %.1f m² ; corde des panneaux bas %.2f m ; allongement H²/S = %.2f ; sommet à %.1f m"
          % (sum(h * c for h, c in PANNEAUX), CORDE, allongement(), -(Z_PIED - H)))
