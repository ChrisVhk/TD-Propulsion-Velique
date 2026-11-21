#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vérification de l'installation — TD Propulsion vélique (EGN-S7, ENSM)

UNE SEULE LIGNE À LANCER, dans le terminal Ubuntu (WSL), depuis le dossier du dépôt :

    python3 scripts/verifie_mon_install.py

Le script ne casse jamais : il liste ce qui va et ce qui ne va pas, en clair, lance
CN-AeroModels sur l'aile elliptique (cas/exemples/2- nonlinear lifting line/elliptic.yml)
dans un dossier temporaire, compare le C_L obtenu à la valeur de référence (0,3655 : sortie de l'outil v0.5.1
pour ce cas, en accord avec la théorie de Prandtl), puis
affiche un bloc à recopier et à renvoyer à l'enseignant.
Sur le modèle de scripts/verifie_mon_install.py du dépôt Informatique-Appliquee-S5.
Aucune bibliothèque à installer : Python standard seulement.
"""

import os
import platform
import shutil
import subprocess
import sys
import tempfile
import importlib.util

OK, KO, WARN = "[ OK ]", "[ MANQUE ]", "[ NOTE ]"
CL_REF = 0.3655              # aile elliptique, AR = 4 : sortie de CN-AeroModels v0.5.1 (04/11/2026), accord avec Prandtl
lignes, bloc_retour = [], []


def dit(statut, message, detail_retour=None):
    lignes.append((statut, message))
    bloc_retour.append(f"{statut} {detail_retour or message}")


RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. Python
v = sys.version_info
dit(OK if v >= (3, 8) else KO, f"Python {v.major}.{v.minor}.{v.micro}", f"Python {v.major}.{v.minor}")

# 2. Système : WSL ?
rel = platform.release().lower()
if platform.system() == "Linux" and ("microsoft" in rel or "wsl" in rel):
    dit(OK, "Vous êtes bien dans WSL (Ubuntu sous Windows)", "WSL")
elif platform.system() == "Linux":
    dit(OK, "Vous êtes sous Linux (hors WSL)", "Linux")
else:
    dit(KO, f"Système '{platform.system()}' : ouvrez le terminal Ubuntu, pas PowerShell",
        f"{platform.system()} (PAS WSL)")

# 3. Modules Python du TD
for module, paquet in [("yaml", "python3-yaml"), ("matplotlib", "python3-matplotlib")]:
    if importlib.util.find_spec(module) is None:
        dit(KO, f"module '{module}' absent — bash scripts/installer_cnaero.sh (ou sudo apt install {paquet})",
            f"{module} MANQUE")
    else:
        dit(OK, f"module '{module}' présent", f"{module} OK")

# 4. CN-AeroModels sur le PATH
binaire = shutil.which("CN-AeroModels")
if binaire is None:
    candidat = os.path.expanduser("~/outils/CN-AeroModels/bin/CN-AeroModels")
    if os.path.isfile(candidat):
        dit(WARN, "CN-AeroModels installé mais pas sur le PATH : fermez et rouvrez le terminal "
                  "(ou : source ~/.bashrc)", "CN-AeroModels hors PATH")
        binaire = candidat
    else:
        dit(KO, "CN-AeroModels introuvable — lancez : bash scripts/installer_cnaero.sh", "CN-AeroModels MANQUE")
else:
    dit(OK, f"CN-AeroModels trouvé : {binaire}", "CN-AeroModels OK")

# 5. Le cas de contrôle : aile elliptique
cas = os.path.join(RACINE, "cas", "exemples", "2- nonlinear lifting line", "elliptic.yml")
if binaire and os.path.isfile(cas):
    with tempfile.TemporaryDirectory() as d:
        shutil.copy(cas, d)
        try:
            p = subprocess.run([binaire, "elliptic.yml"], cwd=d, capture_output=True, text=True, timeout=120)
            sortie = p.stdout + p.stderr
        except Exception as e:  # binaire non exécutable, délai dépassé…
            sortie = f"ERREUR {e}"
    cl = None
    for l in sortie.splitlines():
        if l.strip().startswith("elliptic") and "|" in l:
            try:
                cl = float(l.split("|")[1].split(",")[4])
            except (IndexError, ValueError):
                pass
    if cl is None:
        dit(KO, "l'aile elliptique n'a pas donné de résultat lisible — voir docs/00b_CA_NA_PAS_MARCHE.md",
            "elliptic : pas de résultat")
    elif abs(cl - CL_REF) < 5e-5:
        dit(OK, f"aile elliptique : C_L = {cl:.4f}, valeur de référence {CL_REF}", f"elliptic C_L {cl:.4f} OK")
    else:
        dit(KO, f"aile elliptique : C_L = {cl:.4f} au lieu de {CL_REF} — vérifiez la version (v0.5.1)",
            f"elliptic C_L {cl:.4f} FAUX")
elif not os.path.isfile(cas):
    dit(KO, "cas/…/elliptic.yml introuvable — lancez le script depuis le dossier du dépôt", "cas introuvable")

# Bilan
print("\n" + "=" * 64)
print("  VÉRIFICATION — TD Propulsion vélique (EGN-S7)")
print("=" * 64)
for statut, message in lignes:
    print(f"  {statut:10} {message}")
nb_ko = sum(1 for s, _ in lignes if s == KO)
print("-" * 64)
if nb_ko == 0:
    print("  Tout est prêt pour le TD.")
else:
    print(f"  {nb_ko} point(s) BLOQUANT(S) — voir docs/00b_CA_NA_PAS_MARCHE.md")
print("\n  >>> À COPIER-COLLER ET RENVOYER À L'ENSEIGNANT <<<")
print("  " + "- " * 30)
print(f"  machine : {platform.system()} / {platform.release()}   python : {sys.version.split()[0]}")
for r in bloc_retour:
    print(f"  {r}")
print("  " + "- " * 30)
