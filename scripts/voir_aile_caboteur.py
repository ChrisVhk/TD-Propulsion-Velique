#!/usr/bin/env pvpython
# -*- coding: utf-8 -*-
"""
Voir l'aile du caboteur dans ParaView — TD Propulsion vélique (EGN-S7, ENSM)

Repli de l'état ParaView cas/Cas-ENSM_aile-du-caboteur/paraview/aile_caboteur.pvsm :
ce script construit la même vue sans passer par l'état.

UNE LIGNE, dans le terminal Ubuntu (WSL), depuis le dossier du dépôt :

    pvpython scripts/voir_aile_caboteur.py

(pvpython vient avec ParaView de WSL : sudo apt install paraview)

Ce que fait le script :
  1. il copie le cas de l'aile du caboteur et sa table de profil dans un dossier temporaire
     (rien n'est écrit dans le dépôt) et y lance CN-AeroModels avec l'option --vtk 1 ;
  2. il ouvre les quatre fichiers .vtk écrits par l'outil et construit la vue :
       - l'aile, découpée en trois bandes, colorée par le coefficient de portance C_L (Cl) ;
       - une flèche d'effort par bande (dForce, effort par unité de surface, N/m^2) ;
       - le vent vrai (flèches grises, TWS) et la surface de la mer (plan z = 0) ;
       - le repère : les fichiers sont en NED (x vers le nord = l'avant, y vers l'est = tribord,
         z vers le BAS) ; la vue est donc retournée (haut de l'écran = -z) pour voir l'aile debout ;
  3. il ouvre une fenêtre (fermer la fenêtre pour finir), ou écrit une image sans fenêtre.

Options :
  --donnees DOSSIER   ne relance pas l'outil : lit les .vtk déjà écrits dans DOSSIER
  --depot DOSSIER     dossier du dépôt du TD, si le script n'est pas rangé dans son dossier scripts/
  --png FICHIER       écrit une capture (1920 x 1080 par défaut)
  --etat FICHIER      enregistre l'état ParaView (.pvsm) de la vue
  --sans-fenetre      n'ouvre pas de fenêtre (avec --png ou --etat)

Couleurs : charte ENSM (MARINE #1A346D, TEALD #147A6D, TEAL #1A9988, GREY #595959), fond blanc.
CN-AeroModels v0.5.1, LHEEA (Centrale Nantes / CNRS), EPL 2.0 ; vue et script : ENSM.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

from paraview.simple import (Arrow, CellCenters, Clip, ColorBy, CreateView, GetColorTransferFunction,
                             GetOpacityTransferFunction, Glyph, Interact, LegacyVTKReader,
                             PointDatasetInterpolator, Render, SaveScreenshot, SaveState, SetActiveView,
                             Show, Text, Transform)

# --- Charte ENSM (s9gm/visu.py) -------------------------------------------------------------
def _rgb(h):
    return [int(h[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]

MARINE, TEALD, TEAL, GREY = (_rgb(c) for c in ("#1A346D", "#147A6D", "#1A9988", "#595959"))
BLANC = [1.0, 1.0, 1.0]

# --- Fichiers écrits par CN-AeroModels --vtk 1 pour le cas de l'aile du caboteur ----------------
FICHIERS = {
    "aile": "aile-caboteur_WPU-1_0000.vtk",          # bandes de l'aile (triangles), aire, normale
    "efforts": "aile-caboteur_WPU-1_force_0000.vtk",  # une cellule par bande : Cl, Cd, Re, dForce...
    "vent": "wind_0000.vtk",                          # grille du vent vrai, vecteur TWS
    "mer": "FreeSurface_0000.vtk",                    # surface de la mer, plan z = 0
}
ECHELLE_EFFORT = 0.12   # m par N/m^2 : 155 N/m^2 -> flèche de 19 m (aile de 33 m)
ECHELLE_VENT = 1.5      # m par m/s : 10,3 m/s -> flèche de 15 m
PLAGE_CL = [-2.0, 2.0]  # palette de C_L, symétrique : le signe de l'outil se lit dans la couleur
# Dossier des données inscrit dans l'état enregistré (--etat) : celui d'un élève dans WSL. Il ne sert
# qu'à nommer les fichiers ; au chargement, ParaView les cherche dans le dossier qu'on lui indique
# (File > Load State, « Search files under specified directory »).
DOSSIER_NEUTRE = "/home/eleve/TD-Propulsion-Velique/cas/Cas-ENSM_aile-du-caboteur"


def racine_depot(depot=None):
    """Dossier du dépôt TD-Propulsion-Velique (celui qui contient cas/Cas-ENSM_aile-du-caboteur)."""
    ici = os.path.dirname(os.path.abspath(__file__))
    candidats = [depot] if depot else [os.path.dirname(ici), os.path.expanduser("~/TD-Propulsion-Velique")]
    for c in candidats:
        if os.path.isfile(os.path.join(c, "cas", "Cas-ENSM_aile-du-caboteur", "aile_caboteur.yml")):
            return c
    sys.exit("Cas de l'aile du caboteur introuvable : lancez le script depuis le dépôt TD-Propulsion-Velique.")


def trouver_binaire():
    b = shutil.which("CN-AeroModels")
    if b:
        return b
    c = os.path.expanduser("~/outils/CN-AeroModels/bin/CN-AeroModels")
    if os.path.isfile(c):
        return c
    sys.exit("CN-AeroModels introuvable : lancez d'abord  bash scripts/installer_cnaero.sh")


def lancer_cas(depot=None):
    """Copie le cas dans un dossier temporaire, lance l'outil avec --vtk 1, renvoie le dossier des .vtk."""
    racine = racine_depot(depot)
    tmp = tempfile.mkdtemp(prefix="aile_caboteur_vtk_")
    dossier_cas = os.path.join(tmp, "cas", "Cas-ENSM_aile-du-caboteur")
    os.makedirs(dossier_cas)
    shutil.copy(os.path.join(racine, "cas", "Cas-ENSM_aile-du-caboteur", "aile_caboteur.yml"), dossier_cas)
    shutil.copytree(os.path.join(racine, "cas", "exemples", "airfoil_data"),
                    os.path.join(tmp, "cas", "exemples", "airfoil_data"))
    p = subprocess.run([trouver_binaire(), "aile_caboteur.yml", "--vtk", "1"], cwd=dossier_cas,
                       capture_output=True, text=True, timeout=300)
    if p.returncode != 0:
        sys.exit("CN-AeroModels a échoué :\n" + p.stdout + p.stderr)
    print("Cas relancé avec --vtk 1 dans :", dossier_cas)
    return dossier_cas


def construire_vue(dossier, largeur=1920, hauteur=1080):
    """Construit la vue à partir des quatre .vtk de `dossier` ; renvoie la vue."""
    for f in FICHIERS.values():
        if not os.path.isfile(os.path.join(dossier, f)):
            sys.exit(f"Fichier absent : {os.path.join(dossier, f)} (l'outil a-t-il été lancé avec --vtk 1 ?)")
    lire = lambda cle, nom: LegacyVTKReader(registrationName=nom, FileNames=[os.path.join(dossier, FICHIERS[cle])])

    vue = CreateView("RenderView")
    SetActiveView(vue)
    vue.ViewSize = [largeur, hauteur]
    vue.Background = BLANC
    vue.UseColorPaletteForBackground = 0
    vue.OrientationAxesVisibility = 0   # repère dessiné dans la scène, à l'origine
    vue.OrientationAxesLabelColor = MARINE
    vue.OrientationAxesXColor = MARINE
    vue.OrientationAxesYColor = TEALD
    vue.OrientationAxesZColor = GREY

    aile = lire("aile", "Aile (bandes)")
    efforts = lire("efforts", "Efforts par bande")
    vent = lire("vent", "Vent vrai")
    mer = lire("mer", "Surface de la mer")

    # Efforts : une cellule (dégénérée) par bande -> un point par bande, au centre de la bande.
    centres = CellCenters(registrationName="Centres des bandes", Input=efforts)
    centres.VertexCells = 1

    # Aile colorée par C_L : la valeur de chaque bande est portée sur les sommets de l'aile
    # (noyau de Voronoï : le centre de bande le plus proche ; filtre natif, sans Python).
    aile_cl = PointDatasetInterpolator(registrationName="Aile colorée par C_L", Input=centres, Source=aile)
    aile_cl.Kernel = "VoronoiKernel"

    rep_aile = Show(aile_cl, vue)
    rep_aile.SetRepresentationType("Surface With Edges")
    rep_aile.EdgeColor = GREY
    rep_aile.LineWidth = 2.0
    ColorBy(rep_aile, ("POINTS", "Cl"))
    lut = GetColorTransferFunction("Cl")
    lut.ApplyPreset("Cool to Warm", True)
    lut.RGBPoints = [PLAGE_CL[0], *MARINE, 0.0, *BLANC, PLAGE_CL[1], *TEALD]
    lut.AutomaticRescaleRangeMode = "Never"
    lut.RescaleTransferFunction(*PLAGE_CL)
    GetOpacityTransferFunction("Cl").RescaleTransferFunction(*PLAGE_CL)
    rep_aile.SetScalarBarVisibility(vue, True)
    barre = lut.GetScalarBar(vue) if hasattr(lut, "GetScalarBar") else None
    if barre is None:
        from paraview.simple import GetScalarBar
        barre = GetScalarBar(lut, vue)
    barre.Title = "C_L de chaque bande (Cl, signe de l'outil)"
    barre.ComponentTitle = ""
    barre.TitleColor = MARINE
    barre.LabelColor = MARINE
    barre.TitleFontSize = 20
    barre.LabelFontSize = 18
    barre.RangeLabelFormat = "%-#6.3g"
    barre.WindowLocation = "Any Location"
    barre.Position = [0.89, 0.30]
    barre.ScalarBarLength = 0.45

    # Flèches d'effort : une par bande, dans la direction de dForce, longueur proportionnelle.
    fleches = Glyph(registrationName="Flèches d'effort (dForce)", Input=centres, GlyphType="Arrow")
    fleches.OrientationArray = ["POINTS", "dForce(N/m^2)"]
    fleches.ScaleArray = ["POINTS", "dForce(N/m^2)"]
    fleches.ScaleFactor = ECHELLE_EFFORT
    fleches.GlyphMode = "All Points"
    fleches.GlyphType.TipRadius = 0.12
    fleches.GlyphType.ShaftRadius = 0.04
    rep_f = Show(fleches, vue)
    rep_f.ColorArrayName = ["POINTS", ""]
    rep_f.AmbientColor = TEAL
    rep_f.DiffuseColor = TEAL

    # Vent vrai : flèches grises sur la grille de l'outil, réduites à une rangée, au vent de l'aile
    # (côté bâbord, y = -50 m), à mi-hauteur (z = -25 m), pour x = -25, 0 et 25 m : la grille du fichier a 75 points
    # jusqu'à 100 m de haut, qui cacheraient l'aile de 33 m.
    fl_vent = Glyph(registrationName="Flèches du vent vrai (TWS)", Input=vent, GlyphType="Arrow")
    fl_vent.OrientationArray = ["POINTS", "TWS"]
    fl_vent.ScaleArray = ["POINTS", "TWS"]
    fl_vent.ScaleFactor = ECHELLE_VENT
    fl_vent.GlyphMode = "All Points"
    vent_bas = fl_vent
    for nom, origine, normale in (("sous 37 m", [0.0, 0.0, -37.0], [0.0, 0.0, -1.0]),    # garde z > -37
                                  ("au-dessus de 12 m", [0.0, 0.0, -12.0], [0.0, 0.0, 1.0]),  # garde z < -12
                                  ("côté bâbord", [0.0, -25.0, 0.0], [0.0, 1.0, 0.0]),      # garde y < -25
                                  ("x > -37 m", [-37.0, 0.0, 0.0], [-1.0, 0.0, 0.0]),         # garde x > -37
                                  ("x < 37 m", [37.0, 0.0, 0.0], [1.0, 0.0, 0.0])):           # garde x < 37
        vent_bas = Clip(registrationName=f"Vent : {nom}", Input=vent_bas)
        vent_bas.ClipType = "Plane"
        vent_bas.ClipType.Origin = origine
        vent_bas.ClipType.Normal = normale
        vent_bas.Crinkleclip = 1
    rep_v = Show(vent_bas, vue)
    rep_v.ColorArrayName = ["POINTS", ""]
    rep_v.AmbientColor = GREY
    rep_v.DiffuseColor = GREY
    rep_v.Opacity = 0.5

    # Repère NED à l'origine (pied de l'aile) : trois flèches de 20 m, z vers le BAS (sous la mer).
    for nom, rot, couleur, texte, pos in (
            ("x", [0, 0, 0], MARINE, "x : nord (avant)", [23.0, 0.0, 0.0]),
            ("y", [0, 0, 90], MARINE, "y : est (tribord)", [0.0, 23.0, 0.0]),
            ("z", [0, -90, 0], GREY, "z : vers le BAS", [-15.0, -6.0, 15.0])):
        fl = Arrow(registrationName=f"Axe {nom} (NED)")
        fl.TipRadius = 0.06
        fl.ShaftRadius = 0.018
        tr = Transform(registrationName=f"Axe {nom} (NED), 20 m", Input=fl)
        tr.Transform = "Transform"
        tr.Transform.Scale = [20.0, 20.0, 20.0]
        tr.Transform.Rotate = rot
        ra = Show(tr, vue)
        ra.ColorArrayName = ["POINTS", ""]
        ra.AmbientColor = couleur
        ra.DiffuseColor = couleur
        et = Text(registrationName=f"Étiquette {nom}")
        et.Text = texte
        re_ = Show(et, vue)
        re_.TextPropMode = "Billboard 3D Text"
        re_.BillboardPosition = pos
        re_.FontSize = 22
        re_.Bold = 1
        re_.Color = couleur

    # Surface de la mer : plan z = 0.
    rep_mer = Show(mer, vue)
    rep_mer.ColorArrayName = ["POINTS", ""]
    rep_mer.AmbientColor = TEAL
    rep_mer.DiffuseColor = TEAL
    rep_mer.Opacity = 0.22

    # Textes.
    titre = Text(registrationName="Titre")
    titre.Text = "Aile du caboteur : CN-AeroModels v0.5.1, option --vtk 1 (théorie des bandes, 3 bandes)"
    rt = Show(titre, vue)
    rt.WindowLocation = "Upper Left Corner"
    rt.FontSize = 26
    rt.Color = MARINE
    rt.Bold = 1

    legende = Text(registrationName="Légende")
    legende.Text = ("Aile : colorée par C_L (une valeur par bande)\n"
                    "Flèches vertes : effort par bande, dForce (N/m²)\n"
                    "Flèches grises : vent vrai, TWS (m/s), au vent de l'aile, à 25 m de haut\n"
                    "Plan vert pâle : surface de la mer (z = 0)")
    rl = Show(legende, vue)
    rl.WindowLocation = "Lower Left Corner"
    rl.FontSize = 20
    rl.Color = TEALD

    ned = Text(registrationName="Repère NED")
    ned.Text = ("Fichiers en NED : x vers le nord (l'avant), y vers l'est (tribord), z vers le BAS.\n"
                "Vue retournée (haut de l'écran = -z) pour voir l'aile debout : son sommet est à z = -33 m.")
    rn = Show(ned, vue)
    rn.WindowLocation = "Lower Right Corner"
    rn.FontSize = 20
    rn.Color = MARINE

    Render(vue)   # premier rendu d'abord : il recadre la caméra, qu'on pose ensuite
    # Caméra : depuis tribord un peu en arrière, 35° au-dessus de la mer, à mi-chemin entre la normale
    # de l'aile (pour voir ses bandes) et la perpendiculaire aux flèches d'effort (pour les voir en long).
    # Sur l'écran, x (l'avant) part en haut à droite, y (tribord) en bas à droite, l'effort entre
    # les deux ; haut de l'écran = -z (NED).
    vue.CameraFocalPoint = [0.0, -14.0, -10.0]
    vue.CameraPosition = [-41.0, 90.0, -85.0]
    vue.CameraViewUp = [0.0, 0.0, -1.0]
    vue.CameraParallelProjection = 1   # projection parallèle : toutes les flèches à la même échelle
    vue.CameraParallelScale = 40.0     # demi-hauteur de l'écran, en m
    Render(vue)
    return vue


def main():
    ap = argparse.ArgumentParser(description="Vue ParaView de l'aile du caboteur (CN-AeroModels --vtk 1).")
    ap.add_argument("--donnees", help="dossier des .vtk déjà écrits (sinon : le cas est relancé)")
    ap.add_argument("--depot", help="dossier du dépôt TD-Propulsion-Velique, si le script n'y est pas rangé")
    ap.add_argument("--png", help="écrit une capture PNG")
    ap.add_argument("--etat", help="enregistre l'état ParaView (.pvsm)")
    ap.add_argument("--sans-fenetre", action="store_true", help="n'ouvre pas de fenêtre")
    ap.add_argument("--largeur", type=int, default=1920)
    ap.add_argument("--hauteur", type=int, default=1080)
    a = ap.parse_args()

    dossier = os.path.abspath(a.donnees) if a.donnees else lancer_cas(a.depot)
    vue = construire_vue(dossier, a.largeur, a.hauteur)
    if a.png:
        SaveScreenshot(a.png, vue, ImageResolution=[a.largeur, a.hauteur], OverrideColorPalette="WhiteBackground")
        print("Capture écrite :", a.png)
    if a.etat:
        SaveState(a.etat)
        with open(a.etat, encoding="utf-8") as f:
            texte = f.read()
        with open(a.etat, "w", encoding="utf-8") as f:
            f.write(texte.replace(dossier, DOSSIER_NEUTRE))
        print("État écrit :", a.etat)
    if not a.sans_fenetre:
        print("Fenêtre ParaView ouverte : souris pour tourner, molette pour zoomer ; fermer la fenêtre pour finir.")
        Interact(vue)


if __name__ == "__main__":
    main()
