#!/usr/bin/env pvpython
# -*- coding: utf-8 -*-
"""
Voir la portance le long de l'envergure dans ParaView — TD 2 Propulsion vélique (EGN-S7, ENSM), manipulation 2 ter

Repli de l'état ParaView cas/TD2_envergure/envergure.pvsm : ce script construit la même vue sans passer par l'état.
(L'état lui-même est enregistré par l'interface graphique de ParaView pour Windows, à partir de la même fonction
construire_vue : un état destiné à l'interface se fabrique et se teste dans l'interface.)

Avant : les trois calculs, dans le terminal Ubuntu (WSL) :

    cd ~/TD-Propulsion-Velique/cas/TD2_envergure
    bash lancer_les_trois.sh

Puis, UNE LIGNE, depuis le dossier du dépôt (pvpython vient avec ParaView de WSL : sudo apt install paraview) :

    pvpython scripts/voir_envergure.py

Ce que montre la vue (deux vues côte à côte, dans un layout « Envergure ») :
  - à gauche, les trois ailes côte à côte, chacune découpée en ses éléments et colorée par le C_L de chaque élément
    (Cl, même palette qu'au TD 1) : 1 · théorie des bandes (3 bandes), 2 · NLL pied libre (20 éléments),
    3 · NLL pont en miroir (20 éléments) ; 4 · l'aile image que l'outil place sous le pont pour le calcul 3
    (plan de symétrie, LH p. 40) ; 5 · le pont (z = -2,5 m, vu par la tranche) ; 6 · les noms des trois calculs ;
  - à droite, 7 · |C_L| de chaque élément en fonction de sa hauteur au-dessus du pont, une courbe par calcul :
    la perte en bout d'aile et l'effet du pont au pied se lisent sur les courbes ;
  - 8 · le titre.
Les fichiers lus sont ceux qu'écrit lancer_les_trois.sh : 1_bandes_*, 2_nll-pied-libre_*, 3_nll-pont_*.

Options :
  --donnees DOSSIER   dossier des .vtk (défaut : cas/TD2_envergure du dépôt)
  --png FICHIER       écrit une capture du layout (1920 x 1080 par défaut)
  --sans-fenetre      n'ouvre pas de fenêtre (avec --png)

Couleurs : charte ENSM (MARINE #1A346D, TEALD #147A6D, TEAL #1A9988, GREY #595959), fond blanc.
CN-AeroModels v0.5.1, LHEEA (Centrale Nantes / CNRS), EPL 2.0 ; vue et script : ENSM.
"""

import argparse
import os
import sys

from paraview.simple import (AssignViewToLayout, Calculator, CellCenters, ColorBy, CreateLayout, CreateView,
                             GetColorTransferFunction, GetOpacityTransferFunction, Interact, LegacyVTKReader,
                             MergeBlocks, Line, PointDatasetInterpolator, Render, SaveScreenshot, SetActiveView,
                             Show, Text, Transform)

def _rgb(h):
    return [int(h[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]

MARINE, TEALD, TEAL, GREY = (_rgb(c) for c in ("#1A346D", "#147A6D", "#1A9988", "#595959"))
BLANC = [1.0, 1.0, 1.0]
GRIS_CLAIR = _rgb("#D9D9D9")
PLAGE_CL = [-2.0, 2.0]   # palette de C_L du TD 1 (symétrique : le signe de l'outil se lit dans la couleur)
Z_PONT = -2.5            # pont du caboteur (NED, z vers le bas), pied de l'aile

# Les trois calculs : préfixe des fichiers (lancer_les_trois.sh), nom affiché, couleur de la courbe.
CALCULS = (("1_bandes", "Bandes", GREY),
           ("2_nll-pied-libre", "NLL, pied libre", TEAL),
           ("3_nll-pont", "NLL, pont", MARINE))
COURT = ("Bandes", "NLL libre", "NLL pont")
# Corde de l'aile au réglage du cas, dans le plan horizontal (lue dans les .vtk : du bord d'attaque au bord de fuite).
CORDE = (-0.8257, 0.5641, 0.0)
NORMALE = (0.5641, 0.8257, 0.0)      # perpendiculaire à l'aile, dans le plan horizontal : on regarde l'aile de face
ECART = 28.0                          # m entre deux ailes, le long de la corde (corde de 11 m)
CAMERA_DEMI_HAUTEUR = 45.0            # m (projection parallèle) : noms, ailes (35,5 m) et aile image (33 m sous le pont)
Z_VISEE = -5.0                        # m : centre de l'écran (place pour le titre et les noms au-dessus des ailes)


def dossier_par_defaut():
    ici = os.path.dirname(os.path.abspath(__file__))
    for c in (os.path.join(os.path.dirname(ici), "cas", "TD2_envergure"),
              os.path.expanduser("~/TD-Propulsion-Velique/cas/TD2_envergure")):
        if os.path.isdir(c):
            return c
    sys.exit("Dossier cas/TD2_envergure introuvable : lancez le script depuis le dépôt TD-Propulsion-Velique.")


def fichiers_attendus():
    f = []
    for pre, _, _ in CALCULS:
        f += [pre + "_aile.vtk", pre + "_force.vtk"]
    return f + ["3_nll-pont_mirror.vtk"]


def construire_vue(dossier, largeur=1920, hauteur=1080, vue=None, courbe=None, taille_noms=26):
    """Construit les deux vues à partir des .vtk de `dossier` ; renvoie (vue de rendu, vue des courbes).
    `vue`, `courbe` : vues déjà rangées dans un layout (interface graphique) ; sinon, vues et layout sont créés."""
    manque = [f for f in fichiers_attendus() if not os.path.isfile(os.path.join(dossier, f))]
    if manque:
        sys.exit("Fichiers absents dans %s : %s\n(lancez d'abord : bash lancer_les_trois.sh)" % (dossier, ", ".join(manque)))
    lire = lambda nom: LegacyVTKReader(registrationName=nom, FileNames=[os.path.join(dossier, nom)])

    if vue is None:
        layout = CreateLayout("Envergure")
        vue = CreateView("RenderView")
        AssignViewToLayout(view=vue, layout=layout, hint=0)
        courbe = CreateView("XYChartView")
        layout.SplitHorizontal(0, 0.58)
        AssignViewToLayout(view=courbe, layout=layout, hint=2)
    SetActiveView(vue)
    vue.ViewSize = [int(largeur * 0.58), hauteur]
    vue.Background = BLANC
    vue.UseColorPaletteForBackground = 0
    vue.OrientationAxesVisibility = 0

    lut = GetColorTransferFunction("Cl")
    lut.ApplyPreset("Cool to Warm", True)
    lut.RGBPoints = [PLAGE_CL[0], *MARINE, 0.0, *BLANC, PLAGE_CL[1], *TEALD]
    lut.AutomaticRescaleRangeMode = "Never"
    lut.RescaleTransferFunction(*PLAGE_CL)
    GetOpacityTransferFunction("Cl").RescaleTransferFunction(*PLAGE_CL)

    # Objets affichés numérotés dans l'ordre de la légende de la fiche ; intermédiaires « (calcul) », œil éteint.
    for k, (pre, nom, couleur) in enumerate(CALCULS):
        decalage = [ECART * k * c for c in CORDE]
        centres = CellCenters(registrationName=f"(calcul) {nom} : centres des éléments", Input=lire(pre + "_force.vtk"))
        centres.VertexCells = 1
        aile_cl = PointDatasetInterpolator(registrationName=f"(calcul) {nom} : C_L porté sur l'aile",
                                           Input=centres, Source=lire(pre + "_aile.vtk"))
        aile_cl.Kernel = "VoronoiKernel"
        place = Transform(registrationName=f"{k + 1} · Aile : {nom}", Input=MergeBlocks(
            registrationName=f"(calcul) {nom} : aile colorée", Input=aile_cl))
        place.Transform = "Transform"
        place.Transform.Translate = decalage
        rep = Show(place, vue)
        rep.SetRepresentationType("Surface With Edges")
        rep.EdgeColor = GREY
        rep.LineWidth = 1.5
        ColorBy(rep, ("POINTS", "Cl"))
        if k == 0:
            rep.SetScalarBarVisibility(vue, True)
        # Nom du calcul au-dessus de son aile (6 · …)
        et = Text(registrationName=f"6 · Nom du calcul {k + 1}")
        et.Text = f"{k + 1}. {COURT[k]}"   # nom court au-dessus de l'aile (lisible dans une petite fenêtre)
        re_ = Show(et, vue)
        re_.TextPropMode = "Billboard 3D Text"
        re_.BillboardPosition = [decalage[0] - 2.0 * CORDE[0], decalage[1] - 2.0 * CORDE[1], -40.0]
        re_.FontSize = taille_noms
        re_.Bold = 1
        re_.Color = couleur
        # Courbe : |C_L| (axe horizontal) en fonction de la hauteur au-dessus du pont (axe vertical)
        abs_cl = Calculator(registrationName=f"(calcul) {nom} : |C_L|", Input=centres)
        abs_cl.ResultArrayName = "|C_L|"
        abs_cl.Function = "abs(Cl)"
        h = Calculator(registrationName=f"7 · Courbe : {nom}", Input=abs_cl)
        h.ResultArrayName = "hauteur au-dessus du pont (m)"
        h.Function = f"-coordsZ+{Z_PONT}"
        rc = Show(h, courbe)
        rc.UseIndexForXAxis = 0
        rc.XArrayName = "|C_L|"
        rc.SeriesVisibility = ["hauteur au-dessus du pont (m)"]
        rc.SeriesLabel = ["hauteur au-dessus du pont (m)", f"{k + 1}. {nom}"]
        rc.SeriesColor = ["hauteur au-dessus du pont (m)", *[str(c) for c in couleur]]
        rc.SeriesLineThickness = ["hauteur au-dessus du pont (m)", "3"]
        rc.SeriesMarkerStyle = ["hauteur au-dessus du pont (m)", "4"]   # cercles : un point par élément
        rc.SeriesMarkerSize = ["hauteur au-dessus du pont (m)", "8"]
        if k == 2:   # aile image du pont en miroir, sous le pont, à la place de l'aile 3
            img = Transform(registrationName="4 · Aile image sous le pont (calcul 3)",
                            Input=MergeBlocks(registrationName="(calcul) aile image", Input=lire("3_nll-pont_mirror.vtk")))
            img.Transform = "Transform"
            img.Transform.Translate = decalage
            ri = Show(img, vue)
            ri.SetRepresentationType("Wireframe")
            ri.ColorArrayName = ["POINTS", ""]
            ri.AmbientColor = GREY
            ri.DiffuseColor = GREY
            ri.Opacity = 0.5

    barre = lut.GetScalarBar(vue) if hasattr(lut, "GetScalarBar") else None
    if barre is None:
        from paraview.simple import GetScalarBar
        barre = GetScalarBar(lut, vue)
    barre.Title = "C_L (Cl)"
    barre.ComponentTitle = ""
    barre.TitleColor = MARINE
    barre.LabelColor = MARINE
    barre.TitleFontSize = 16
    barre.LabelFontSize = 14
    barre.AutomaticLabelFormat = 1
    barre.AddRangeLabels = 0
    barre.WindowLocation = "Lower Left Corner"   # coin vide : sous les ailes 1 et 2
    barre.ScalarBarLength = 0.35

    # Pont (z = -2,5 m), vu par la tranche : un trait sous les trois ailes, le long de la corde
    pont = Line(registrationName="5 · Pont (z = -2,5 m)")
    pont.Point1 = [-10.0 * CORDE[i] for i in range(2)] + [Z_PONT]
    pont.Point2 = [(2 * ECART + 18.0) * CORDE[i] for i in range(2)] + [Z_PONT]
    rp = Show(pont, vue)
    rp.ColorArrayName = ["POINTS", ""]
    rp.AmbientColor = TEAL
    rp.DiffuseColor = TEAL
    rp.LineWidth = 4.0

    titre = Text(registrationName="8 · Titre (texte à l'écran)")
    titre.Text = "Aile du caboteur : C_L le long de l'envergure"
    rt = Show(titre, vue)
    rt.WindowLocation = "Upper Left Corner"
    rt.FontSize = 18
    rt.Color = MARINE
    rt.Bold = 1

    # Courbes : axes nommés, plages fixées (les trois courbes se comparent à la même échelle)
    courbe.ChartTitle = "|C_L| de chaque élément"
    courbe.ShowLegend = 1
    courbe.LegendFontSize = 13
    courbe.ChartTitleFontSize = 18
    courbe.LeftAxisTitleFontSize = 15
    courbe.BottomAxisTitleFontSize = 15
    courbe.LeftAxisTitleBold = 0
    courbe.BottomAxisTitleBold = 0
    courbe.ChartTitleColor = MARINE
    courbe.LeftAxisTitleColor = MARINE
    courbe.BottomAxisTitleColor = MARINE
    courbe.LegendLocation = "TopRight"
    courbe.BottomAxisTitle = "|C_L| de l'élément"
    courbe.LeftAxisTitle = "hauteur au-dessus du pont (m)"
    courbe.BottomAxisUseCustomRange = 1
    courbe.BottomAxisRangeMinimum = 0.0
    courbe.BottomAxisRangeMaximum = 3.0   # place à droite pour la légende, sans cacher de point
    courbe.LeftAxisUseCustomRange = 1
    courbe.LeftAxisRangeMinimum = 0.0
    courbe.LeftAxisRangeMaximum = 33.0

    Render(vue)
    # On regarde l'aile de face, depuis le côté où les ailes 1, 2, 3 se lisent de gauche à droite.
    centre = [ECART * CORDE[i] - 4.0 * CORDE[i] for i in range(2)] + [Z_VISEE]
    vue.CameraFocalPoint = centre
    vue.CameraPosition = [centre[i] - 200.0 * NORMALE[i] for i in range(2)] + [Z_VISEE]
    vue.CameraViewUp = [0.0, 0.0, -1.0]
    vue.CameraParallelProjection = 1
    vue.CameraParallelScale = CAMERA_DEMI_HAUTEUR
    Render(vue)
    Render(courbe)
    return vue, courbe


def main():
    ap = argparse.ArgumentParser(description="C_L le long de l'envergure : bandes, NLL pied libre, NLL pont (ParaView).")
    ap.add_argument("--donnees", help="dossier des .vtk (défaut : cas/TD2_envergure du dépôt)")
    ap.add_argument("--png", help="écrit une capture PNG du layout")
    ap.add_argument("--sans-fenetre", action="store_true", help="n'ouvre pas de fenêtre")
    ap.add_argument("--largeur", type=int, default=1920)
    ap.add_argument("--hauteur", type=int, default=1080)
    a = ap.parse_args()
    dossier = os.path.abspath(a.donnees) if a.donnees else dossier_par_defaut()
    vue, courbe = construire_vue(dossier, a.largeur, a.hauteur)
    if a.png:
        from paraview.simple import GetLayout
        SaveScreenshot(a.png, GetLayout(vue), ImageResolution=[a.largeur, a.hauteur],
                       OverrideColorPalette="WhiteBackground")
        print("Capture écrite :", a.png)
    if not a.sans_fenetre:
        print("Fenêtre ParaView ouverte : souris pour tourner, molette pour zoomer ; fermer la fenêtre pour finir.")
        Interact(vue)


if __name__ == "__main__":
    main()
