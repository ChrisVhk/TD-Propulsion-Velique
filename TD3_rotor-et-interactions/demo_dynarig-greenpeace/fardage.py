#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fardage de la coque générique et de ses superstructures (démonstration DynaRig du TD 3, EGN-S7, ENSM) par la méthode
empirique de Fujiwara, Ueno et Ikeda (2005), au vent de la démonstration ; comparaison à la poussée des deux mâts.

    python3 fardage.py

SOURCE PRIMAIRE (lue le 26/11/2026 sur le scan J-STAGE) : T. Fujiwara, M. Ueno, Y. Ikeda, « A new estimation method of
wind forces and moments acting on ships on the basis of physical component models », Journal of the Japan Society of
Naval Architects and Ocean Engineers, vol. 2, 2005, p. 243-255, doi:10.2534/jjasnaoe.2.243 :
  - définitions des coefficients, éq. (1)-(2), p. 244 : C_X = X_A / (q_A A_F), C_Y = Y_A / (q_A A_L), q_A = ½ ρ U_A² ;
    paramètres de forme, Fig. 2, p. 244 ; repère Fig. 1 : x vers l'avant, ψ_A = 0 pour un vent apparent de face ;
  - pression dynamique de référence : vent à la hauteur H_L = A_L / L_OA, éq. (2)-(3), p. 245 (q_A = q_HL pour X_A) ;
    on l'applique aussi à Y_A (simplification, dite ici) ;
  - C_X(ψ) et C_Y(ψ) en composantes physiques, éq. (7) et (8), p. 246 ;
  - coefficients séparés pour 0° ≤ ψ ≤ 90° et 90° ≤ ψ ≤ 180° (p. 247) ; régressions éq. (12), (14)-(22), p. 248-249 ;
    coefficients de la Table 3, p. 248 (recopiés ci-dessous tels qu'imprimés).
Domaine de la régression (Table 2, p. 245) : 71 navires de 25 à 351 m. Navire générique d'école : aires tirées de
fabriquer_coque.py (hypothèses) ; mâts, vergues et voiles exclus (la méthode ne les représente pas).
ENSM (Christophe VANHORICK), 26/11/2026, Apache 2.0.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fabriquer_cas as fc      # noqa: E402  vent et vitesse de la démonstration
import fabriquer_coque as co    # noqa: E402  aires projetées

# Table 3, p. 248 : alpha_j, beta_ij, gamma_ij, delta_ij, epsilon_ij (i = 1 : 0-90° ; i = 2 : 90-180°)
ALPHA = (0.404, 0.368, 0.902)
BETA = {1: (-0.922, 0.507, 1.162), 2: (0.018, -5.091, 10.367, -3.011, -0.341)}
GAMMA = {1: (0.116, 3.345), 2: (0.446, 2.192)}
DELTA = {1: (0.458, 3.245, -2.313), 2: (-1.901, 12.727, 24.407, -40.310, -5.481)}
EPSILON = {1: (-0.585, -0.906, 3.239), 2: (-0.314, -1.117)}
RHO_AIR = 1.225


def coefficients(g, i):
    """C_CF (12), C_LF (14)/(15), C_YLI (16)-(18), C_XLI (19)/(20), C_ALF (21)/(22) ; i = 1 (0-90°) ou 2 (90-180°)."""
    L, B, AF, AL, AOD, C, HC, HBR = (g[k] for k in ("L_OA", "B", "A_F", "A_L", "A_OD", "C", "H_C", "H_BR"))
    c_cf = ALPHA[0] + ALPHA[1] * AF / (B * HBR) + ALPHA[2] * HBR / L
    if i == 1:
        b, d, e, gm = BETA[1], DELTA[1], EPSILON[1], GAMMA[1]
        c_lf = b[0] + b[1] * AL / (L * B) + b[2] * C / L
        c_ym = gm[0] + gm[1] * AF / (L * B)
        c_xli = d[0] + d[1] * AL / (L * HBR) + d[2] * AF / (B * HBR)
        c_alf = e[0] + e[1] * AOD / AL + e[2] * B / L
    else:
        b, d, e, gm = BETA[2], DELTA[2], EPSILON[2], GAMMA[2]
        c_lf = b[0] + b[1] * B / L + b[2] * HC / L + b[3] * AOD / L ** 2 + b[4] * AF / B ** 2
        c_ym = gm[0] + gm[1] * AOD / L ** 2
        c_xli = d[0] + d[1] * AL / (L * HBR) + d[2] * AF / AL + d[3] * B / L + d[4] * AF / (B * HBR)
        c_alf = e[0] + e[1] * AOD / AL
    c_yli = math.pi * AL / L ** 2 + c_ym
    return dict(C_CF=c_cf, C_LF=c_lf, C_YLI=c_yli, C_XLI=c_xli, C_ALF=c_alf)


def cx_cy(psi_deg, g):
    """Éq. (7) et (8), p. 246 ; psi : angle du vent apparent compté depuis l'avant (0 : vent de face), 0 à 180°."""
    k = coefficients(g, 1 if psi_deg <= 90.0 else 2)
    s, c = math.sin(math.radians(psi_deg)), math.cos(math.radians(psi_deg))
    cx = k["C_LF"] * c + k["C_XLI"] * (s - 0.5 * s * c ** 2) * s * c + k["C_ALF"] * s * c ** 3
    cy = k["C_CF"] * s ** 2 + k["C_YLI"] * (c + 0.5 * s ** 2 * c) * s * c
    return cx, cy, k


def vent_apparent(z):
    """Vent de la démonstration (fabriquer_cas.py) à la hauteur z : vent vrai de travers + vent dû à la vitesse."""
    vt = fc.TWS * (z / fc.Z_REF) ** fc.ALPHA
    return math.hypot(vt, fc.VITESSE), math.degrees(math.atan2(vt, fc.VITESSE))


if __name__ == "__main__":
    g = co.aires()
    h_l = g["A_L"] / g["L_OA"]
    aws, psi = vent_apparent(h_l)
    cx, cy, k = cx_cy(psi, g)
    q = 0.5 * RHO_AIR * aws ** 2
    X, Y = cx * q * g["A_F"] / 1e3, cy * q * g["A_L"] / 1e3
    print("Navire générique (hypothèses, fabriquer_coque.py) : " + " ; ".join("%s = %.2f" % kv for kv in g.items()))
    print("Vent à H_L = A_L/L_OA = %.2f m : vent apparent %.2f m/s, psi_A = %.1f° de l'avant ; q = %.1f Pa"
          % (h_l, aws, psi, q))
    print("Coefficients (0-90°) : " + " ; ".join("%s = %.3f" % kv for kv in k.items()))
    print("C_X = %.3f ; C_Y = %.3f" % (cx, cy))
    print("Fardage : X_A = %.2f kN (signe : + vers l'avant) ; Y_A = %.2f kN" % (X, Y))
    print("À comparer à la poussée des deux mâts de la démonstration (lancer.sh, 137,1 kN) : %.1f %%" % (100 * X / 137.1))
