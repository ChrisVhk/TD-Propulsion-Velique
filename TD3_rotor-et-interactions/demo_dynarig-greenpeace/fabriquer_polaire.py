#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polaire d'école d'une plaque mince cambrée à 10 % (section de DynaRig) pour CN-AeroModels — TD 3 (EGN-S7, ENSM).

    python3 fabriquer_polaire.py        # écrit plaque-cambree.yml dans ce dossier

POLAIRE D'ÉCOLE, HYPOTHÈSE : aucune polaire de section de DynaRig n'est publiée. Cette table n'est pas une mesure ni
un calcul de CFD ; elle est construite par les formules ci-dessous, chacune étant une hypothèse d'école :

  - cambrure f/c = 10 % (maquette rigide de Bordogna, 2020, chap. 3 ; plage 0 à 10 % chez Fluck et al., 2022) ;
  - partie attachée, théorie des profils minces (arc de cercle) : C_L = 2π (α − α0), α en radians, incidence de
    portance nulle α0 = −2 f/c = −0,2 rad (−11,46°), de α = −20° à α = +3° ;
  - de +3° à +10°, arrondi parabolique raccordé en valeur et en pente à la droite ; il donne C_L max ≈ 1,97 à 10° ;
  - décroché (au-delà de +10° et en deçà de −20°) : loi de plaque plane C_L = sin 2α (force normale 2 sin α), à
    laquelle l'écart au point de raccord s'efface comme exp(−((α − α_r)/15°)²) ;
  - traînée : C_D = C_D0 + 2 sin² α, C_D0 = 0,02 (frottement et forme d'une plaque mince, ordre de grandeur) ;
    moment : 0 (non utilisé par la démonstration) ;
  - la même table à Re = 10⁶, 10⁷ et 5·10⁷ (hypothèse : effet du Reynolds négligé ; Bordogna le trouve faible sur
    sa maquette, de 2,8 à 5,6·10⁵).

Les mâts, les vergues, la souplesse de la voile et le jeu entre les panneaux ne sont pas représentés.
ENSM (Christophe VANHORICK), 26/11/2026, Apache 2.0 (création ENSM ; voir PROVENANCE.md).
"""
import math
import os

F_SUR_C = 0.10
ALPHA0 = -2.0 * F_SUR_C                 # rad
A_LIN_HAUT, A_MAX, A_LIN_BAS = 3.0, 10.0, -20.0   # deg
LARGEUR = 15.0                          # deg, effacement de l'écart à la loi de plaque
CD0 = 0.02
REYNOLDS = (1.0e6, 1.0e7, 5.0e7)


def cl_lin(a):
    return 2.0 * math.pi * (math.radians(a) - ALPHA0)


PENTE = 2.0 * math.pi * math.pi / 180.0          # par degré
K = PENTE / (2.0 * (A_MAX - A_LIN_HAUT))
CL_MAX = cl_lin(A_LIN_HAUT) + K * (A_MAX - A_LIN_HAUT) ** 2


def cl_plaque(a):
    return math.sin(2.0 * math.radians(a))


def cl(a):
    if A_LIN_BAS <= a <= A_LIN_HAUT:
        return cl_lin(a)
    if A_LIN_HAUT < a <= A_MAX:
        return CL_MAX - K * (a - A_MAX) ** 2
    ar, c_r = (A_MAX, CL_MAX) if a > A_MAX else (A_LIN_BAS, cl_lin(A_LIN_BAS))
    return cl_plaque(a) + (c_r - cl_plaque(ar)) * math.exp(-((a - ar) / LARGEUR) ** 2)


def cd(a):
    return CD0 + 2.0 * math.sin(math.radians(a)) ** 2


def incidences():
    a = list(range(-180, -30, 5)) + [x * 0.5 for x in range(-60, 61)] + list(range(35, 181, 5))
    return sorted(set(float(x) for x in a))


def texte():
    aoa = incidences()
    fmt = lambda v: ",".join("%.6g" % x for x in v)
    l = ["# Polaire d'école, hypothèse : aucune polaire de section de DynaRig n'est publiée.",
         "# Plaque mince cambrée à 10 % : profils minces (pente 2 pi, alpha0 = -2 f/c) raccordés à une loi de plaque",
         "# décrochée ; C_D = 0,02 + 2 sin^2 alpha ; C_m = 0 ; même table à tous les Re. Fabriquée par",
         "# fabriquer_polaire.py (ENSM, 26/11/2026, Apache 2.0). Ce n'est ni une mesure ni un calcul de CFD.",
         "- type: plaque-cambree-10pc"]
    for re_ in REYNOLDS:
        l += ["- Re: %d # polaire d'école (hypothèse)" % re_,
              "  AoA: {unit: deg, values: [%s]}" % fmt(aoa),
              "  lift coefficient: [%s]" % fmt(cl(a) for a in aoa),
              "  drag coefficient: [%s]" % fmt(cd(a) for a in aoa),
              "  moment coefficient: [%s]" % fmt(0.0 for _ in aoa)]
    return "\n".join(l) + "\n"


if __name__ == "__main__":
    ici = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(ici, "plaque-cambree.yml"), "w", newline="\n") as f:
        f.write(texte())
    print("plaque-cambree.yml écrit : C_L(0°) = %.3f ; C_L max = %.3f à %.0f° ; alpha0 = %.2f° ; C_D(5°) = %.4f"
          % (cl(0), CL_MAX, A_MAX, math.degrees(ALPHA0), cd(5)))
