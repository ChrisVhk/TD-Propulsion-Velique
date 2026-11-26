#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test des valeurs connues — TD Propulsion vélique (EGN-S7, ENSM)

UNE SEULE LIGNE À LANCER, dans le terminal Ubuntu (WSL), depuis le dossier du dépôt :

    python3 scripts/test_valeurs_connues.py

(ou, si pytest est installé : pytest scripts/test_valeurs_connues.py)

Le script relance CN-AeroModels sur deux cas, dans un dossier temporaire (rien n'est écrit
dans le dépôt), et compare le résultat à une valeur de référence :

  1. aile elliptique (communs/exemples-LHEEA/2- nonlinear lifting line/elliptic.yml) : C_L = 0,3655 ;
  2. aile du caboteur (TD1_aerodynamique/manip2-et-3_aile-caboteur/aile-caboteur.yml)  : F_x = 45 015,9 N.

Les deux valeurs de référence sont celles de l'outil v0.5.1, déjà données dans
scripts/verifie_mon_install.py et dans la fiche du TD S1. Tolérance relative : 1e-3.
Aucune bibliothèque à installer : Python standard seulement (pytest facultatif).
"""

import os
import shutil
import subprocess
import sys
import tempfile

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOLERANCE = 1e-3

CL_ELLIPTIQUE = 0.3655       # aile elliptique, AR = 4 : sortie de CN-AeroModels v0.5.1
FX_CABOTEUR = 45015.9        # aile du caboteur, F_x en N : sortie de CN-AeroModels v0.5.1

CAS_ELLIPTIQUE = os.path.join(RACINE, "communs", "exemples-LHEEA", "2- nonlinear lifting line", "elliptic.yml")
CAS_CABOTEUR = os.path.join(RACINE, "TD1_aerodynamique", "manip2-et-3_aile-caboteur", "aile-caboteur.yml")
TABLE_PROFIL = os.path.join(RACINE, "communs", "exemples-LHEEA", "airfoil_data", "NACA0015_v2.yml")


def trouver_binaire():
    """Chemin de CN-AeroModels, sur le PATH ou à l'emplacement de scripts/installer_cnaero.sh."""
    b = shutil.which("CN-AeroModels")
    if b:
        return b
    candidat = os.path.expanduser("~/outils/CN-AeroModels/bin/CN-AeroModels")
    return candidat if os.path.isfile(candidat) else None


def lancer(dossier, fichier_yml):
    """Lance l'outil dans `dossier` ; renvoie le texte affiché à l'écran."""
    binaire = trouver_binaire()
    if binaire is None:
        raise RuntimeError("CN-AeroModels introuvable — lancez : bash scripts/installer_cnaero.sh")
    p = subprocess.run([binaire, fichier_yml], cwd=dossier, capture_output=True, text=True, timeout=300)
    return p.stdout + p.stderr


def lire_ligne(sortie, nom):
    """Découpe la ligne de résultats qui commence par `nom` en blocs séparés par « | »."""
    for ligne in sortie.splitlines():
        if ligne.strip().startswith(nom) and "|" in ligne:
            return ligne.split("|")
    raise RuntimeError(f"pas de ligne « {nom} » dans la sortie de l'outil — voir docs/00b_CA_NA_PAS_MARCHE.md")


def cl_elliptique():
    with tempfile.TemporaryDirectory() as d:
        shutil.copy(CAS_ELLIPTIQUE, d)
        sortie = lancer(d, "elliptic.yml")
    return float(lire_ligne(sortie, "elliptic")[1].split(",")[4])


def fx_caboteur():
    # Le cas lit sa table par le chemin relatif ../../../communs/exemples-LHEEA/airfoil_data/, depuis le dossier où
    # tourne l'outil (sorties/ du dossier de la manipulation, comme lancer.sh) : on reproduit cette arborescence.
    with tempfile.TemporaryDirectory() as d:
        dossier_cas = os.path.join(d, "TD1_aerodynamique", "manip2-et-3_aile-caboteur")
        dossier_sorties = os.path.join(dossier_cas, "sorties")
        dossier_table = os.path.join(d, "communs", "exemples-LHEEA", "airfoil_data")
        os.makedirs(dossier_sorties)
        os.makedirs(dossier_table)
        shutil.copy(CAS_CABOTEUR, dossier_cas)
        shutil.copy(TABLE_PROFIL, dossier_table)
        sortie = lancer(dossier_sorties, "../aile-caboteur.yml")
    return float(lire_ligne(sortie, "WPU-1")[3].split(",")[0])


def ecart_relatif(obtenu, reference):
    return abs(obtenu - reference) / abs(reference)


# --- Tests au format pytest (pytest est facultatif) -------------------------------------------

def test_cl_aile_elliptique():
    cl = cl_elliptique()
    assert ecart_relatif(cl, CL_ELLIPTIQUE) <= TOLERANCE, f"C_L = {cl} au lieu de {CL_ELLIPTIQUE}"


def test_fx_caboteur():
    fx = fx_caboteur()
    assert ecart_relatif(fx, FX_CABOTEUR) <= TOLERANCE, f"F_x = {fx} N au lieu de {FX_CABOTEUR} N"


# --- Lancement direct : python3 scripts/test_valeurs_connues.py --------------------------------

def main():
    essais = [
        ("aile elliptique", "C_L", "", CL_ELLIPTIQUE, cl_elliptique, "{:.4f}"),
        ("aile du caboteur", "F_x", " N", FX_CABOTEUR, fx_caboteur, "{:.1f}"),
    ]
    print("=" * 64)
    print("  TEST DES VALEURS CONNUES — TD Propulsion vélique (EGN-S7)")
    print("=" * 64)
    nb_echecs = 0
    for nom, grandeur, unite, ref, fonction, fmt in essais:
        try:
            v = fonction()
            bon = ecart_relatif(v, ref) <= TOLERANCE
            statut = "[ OK ]    " if bon else "[ ÉCHEC ]"
            print(f"  {statut} {nom} : {grandeur} = {fmt.format(v)}{unite}"
                  f" (référence {fmt.format(ref)}{unite}, écart relatif {ecart_relatif(v, ref):.1e})")
        except Exception as e:
            bon = False
            print(f"  [ ÉCHEC ]  {nom} : {e}")
        nb_echecs += 0 if bon else 1
    print("-" * 64)
    if nb_echecs == 0:
        print("  OK : les deux valeurs connues sont retrouvées.")
    else:
        print(f"  ÉCHEC : {nb_echecs} test(s) sur 2 — copiez TOUT ce bloc et envoyez-le à l'enseignant.")
    print("=" * 64)
    return 0 if nb_echecs == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
