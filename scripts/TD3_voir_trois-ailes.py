#!/usr/bin/env pvpython
# -*- coding: utf-8 -*-
"""
Voir les trois ailes de Malmek dans ParaView — TD 3 Propulsion vélique (EGN-S7, ENSM), manipulation 6

Repli de l'état ParaView cas/trois-ailes/TD3_trois-ailes.pvsm : ce script construit la même vue sans passer par l'état.
(L'état lui-même est enregistré par l'interface graphique de ParaView pour Windows, à partir de la même fonction
construire_vue : un état destiné à l'interface se fabrique et se teste dans l'interface.)

Avant : les deux calculs, dans le terminal Ubuntu (WSL) :

    cd ~/TD-Propulsion-Velique/cas/trois-ailes
    bash TD3_lancer_les_deux.sh

Puis, UNE LIGNE, depuis le dossier du dépôt (pvpython vient avec ParaView de WSL : sudo apt install paraview) :

    pvpython scripts/TD3_voir_trois-ailes.py

Ce que montre la vue (deux vues côte à côte, dans un layout « Trois ailes ») :
  - à gauche, les trois ailes de l'exemple 9 vues de dessus (l'avant du navire en haut), deux fois : 1 · en théorie
    des bandes (rangée de gauche), 2 · en NLL (rangée de droite) ; chaque élément a la couleur de son C_L (Cl, signe de l'outil) ;
    3 · les tourbillons en fer à cheval de la NLL, coupés à 2 m en aval ; 4 · le vent apparent (15° de l'axe du
    navire) ; 5 · l'axe du navire (x, vers l'avant) ; 6 · les noms des deux rangées et des voiles ;
  - à droite, 7 · l'incidence de chaque élément (valeur absolue) en fonction de sa hauteur, une courbe par voile et
    par modèle : on y lit si les éléments travaillent dans le domaine de la table de profil ;
  - 8 · le titre.
Les fichiers lus sont ceux qu'écrit TD3_lancer_les_deux.sh : 1_bandes_voile-N_*, 2_nll_voile-N_*.

Options :
  --donnees DOSSIER   dossier des .vtk (défaut : cas/trois-ailes du dépôt)
  --png FICHIER       écrit une capture du layout (1920 x 1080 par défaut)
  --sans-fenetre      n'ouvre pas de fenêtre (avec --png)

Couleurs : charte ENSM (MARINE #1A346D, TEALD #147A6D, TEAL #1A9988, GREY #595959), fond blanc.
CN-AeroModels v0.5.1, LHEEA (Centrale Nantes / CNRS), EPL 2.0 ; exemple 9 (Malmek, 2023) ; vue et script : ENSM.
"""

import argparse
import os
import sys

from paraview.simple import (AssignViewToLayout, Calculator, CellCenters, Clip, ColorBy, Cone, CreateLayout, CreateView,
                             GetColorTransferFunction, GetOpacityTransferFunction, Interact, LegacyVTKReader,
                             Line, MergeBlocks, PointDatasetInterpolator, Render, SaveScreenshot, SetActiveView,
                             Show, Text, Transform)


def _rgb(h):
    return [int(h[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]


MARINE, TEALD, TEAL, GREY = (_rgb(c) for c in ("#1A346D", "#147A6D", "#1A9988", "#595959"))
BLANC = [1.0, 1.0, 1.0]
ORANGE = _rgb("#C55A11")
PLAGE_CL = [-1.0, 1.0]   # C_L de l'exemple 9 : entre -0,8 et 0 (signe de l'outil)

# Les deux calculs : préfixe des fichiers (TD3_lancer_les_deux.sh), nom affiché, décalage de la rangée (m, y).
CALCULS = (("1_bandes", "Bandes", -1.6), ("2_nll", "NLL", 0.0))
VOILES = (1, 2, 3)                                   # voile 1 à l'avant (x = +0,86 m), voile 3 à l'arrière
COULEURS_VOILES = {1: TEAL, 2: MARINE, 3: ORANGE}    # courbes de droite, une couleur par voile
VENT = (-0.9659, -0.2588, 0.0)                       # sens du vent apparent dans le repère des sorties (15° de -x)
X_COUPE = -2.0                                       # m : tourbillons NLL coupés à 2 m en arrière de l'origine


def dossier_par_defaut():
    ici = os.path.dirname(os.path.abspath(__file__))
    for c in (os.path.join(os.path.dirname(ici), "cas", "trois-ailes"),
              os.path.expanduser("~/TD-Propulsion-Velique/cas/trois-ailes")):
        if os.path.isdir(c):
            return c
    sys.exit("Dossier cas/trois-ailes introuvable : lancez le script depuis le dépôt TD-Propulsion-Velique.")


def fichiers_attendus():
    f = []
    for pre, _, _ in CALCULS:
        for n in VOILES:
            f += ["%s_voile-%d_aile.vtk" % (pre, n), "%s_voile-%d_force.vtk" % (pre, n)]
    return f + ["2_nll_voile-%d_horseshoeVortex.vtk" % n for n in VOILES]


def construire_vue(dossier, largeur=1920, hauteur=1080, vue=None, courbe=None, taille_noms=22):
    """Construit les deux vues à partir des .vtk de `dossier` ; renvoie (vue de rendu, vue des courbes).
    `vue`, `courbe` : vues déjà rangées dans un layout (interface graphique) ; sinon, vues et layout sont créés."""
    manque = [f for f in fichiers_attendus() if not os.path.isfile(os.path.join(dossier, f))]
    if manque:
        sys.exit("Fichiers absents dans %s : %s\n(lancez d'abord : bash TD3_lancer_les_deux.sh)" % (dossier, ", ".join(manque)))
    lire = lambda nom: LegacyVTKReader(registrationName=nom, FileNames=[os.path.join(dossier, nom)])

    if vue is None:
        layout = CreateLayout("Trois ailes")
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
    premier = True
    for k, (pre, nom, dy) in enumerate(CALCULS):
        for n in VOILES:
            cle = "%s, voile %d" % (nom, n)
            centres = CellCenters(registrationName=f"(calcul) {cle} : centres des éléments",
                                  Input=lire("%s_voile-%d_force.vtk" % (pre, n)))
            centres.VertexCells = 1
            aile_cl = PointDatasetInterpolator(registrationName=f"(calcul) {cle} : C_L porté sur l'aile",
                                               Input=centres, Source=lire("%s_voile-%d_aile.vtk" % (pre, n)))
            aile_cl.Kernel = "VoronoiKernel"
            place = Transform(registrationName=f"{k + 1} · {nom} : voile {n}", Input=MergeBlocks(
                registrationName=f"(calcul) {cle} : aile colorée", Input=aile_cl))
            place.Transform = "Transform"
            place.Transform.Translate = [0.0, dy, 0.0]
            rep = Show(place, vue)
            rep.SetRepresentationType("Surface With Edges")
            rep.EdgeColor = GREY
            rep.LineWidth = 1.5
            ColorBy(rep, ("POINTS", "Cl"))
            if premier:
                rep.SetScalarBarVisibility(vue, True)
                premier = False
            # Courbe : |incidence| (axe horizontal) en fonction de la hauteur (axe vertical, z vers le bas)
            inc = Calculator(registrationName=f"(calcul) {cle} : |incidence|", Input=centres)
            inc.ResultArrayName = "|incidence| (deg)"
            inc.Function = 'abs("AoA(degrees)/SR")'
            h = Calculator(registrationName=f"7 · Courbe : {cle}", Input=inc)
            h.ResultArrayName = "hauteur (m)"
            h.Function = "-coordsZ"
            rc = Show(h, courbe)
            rc.UseIndexForXAxis = 0
            rc.XArrayName = "|incidence| (deg)"
            rc.SeriesVisibility = ["hauteur (m)"]
            rc.SeriesLabel = ["hauteur (m)", f"{k + 1}. {nom}, voile {n}"]
            rc.SeriesColor = ["hauteur (m)", *[str(c) for c in COULEURS_VOILES[n]]]
            rc.SeriesLineThickness = ["hauteur (m)", "3" if pre == "2_nll" else "1"]
            rc.SeriesLineStyle = ["hauteur (m)", "1" if pre == "2_nll" else "2"]      # NLL plein, bandes tirets
            rc.SeriesMarkerStyle = ["hauteur (m)", "4" if pre == "2_nll" else "2"]
            rc.SeriesMarkerSize = ["hauteur (m)", "7"]
        # Nom de la rangée, au-dessus de la voile 1
        et = Text(registrationName=f"6 · Nom de la rangée {k + 1}")
        et.Text = f"{k + 1}. {nom}"
        re_ = Show(et, vue)
        re_.TextPropMode = "Billboard 3D Text"
        re_.BillboardPosition = [1.45, dy - 0.25, -1.4]
        re_.FontSize = taille_noms
        re_.Bold = 1
        re_.Color = MARINE if pre == "2_nll" else GREY

    # Numéros des voiles, au-dessus de la rangée NLL
    for n, x in zip(VOILES, (0.84, 0.09, -0.66)):
        t = Text(registrationName=f"6 · Voile {n}")
        t.Text = f"voile {n}"
        rt_ = Show(t, vue)
        rt_.TextPropMode = "Billboard 3D Text"
        rt_.BillboardPosition = [x + 0.1, 0.4, -1.4]
        rt_.FontSize = taille_noms - 4
        rt_.Color = COULEURS_VOILES[n]

    # Tourbillons en fer à cheval (NLL), coupés à X_COUPE
    for n in VOILES:
        coupe = Clip(registrationName=f"3 · Tourbillons NLL : voile {n}", Input=lire("2_nll_voile-%d_horseshoeVortex.vtk" % n))
        coupe.ClipType = "Plane"
        coupe.ClipType.Origin = [X_COUPE, 0.0, 0.0]
        coupe.ClipType.Normal = [1.0, 0.0, 0.0]
        coupe.Invert = 0
        rv = Show(coupe, vue)
        rv.SetRepresentationType("Wireframe")
        rv.ColorArrayName = ["POINTS", ""]
        rv.AmbientColor = GREY
        rv.DiffuseColor = GREY
        rv.Opacity = 0.6

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
    barre.WindowLocation = "Lower Left Corner"
    barre.ScalarBarLength = 0.3

    # Vent apparent : une flèche (trait) qui arrive de l'avant, à 15° de l'axe, à mi-hauteur
    p2 = [1.2, 0.8, -1.4]
    vent = Line(registrationName="4 · Vent apparent (15°)")
    vent.Point1 = [p2[i] - 0.8 * VENT[i] for i in range(2)] + [p2[2]]
    vent.Point2 = p2
    rw = Show(vent, vue)
    rw.ColorArrayName = ["POINTS", ""]
    rw.AmbientColor = ORANGE
    rw.DiffuseColor = ORANGE
    rw.LineWidth = 5.0
    pointe = Cone(registrationName="4 · Vent apparent : pointe")
    pointe.Center = [p2[i] + 0.06 * VENT[i] for i in range(2)] + [p2[2]]
    pointe.Direction = list(VENT)
    pointe.Height = 0.15
    pointe.Radius = 0.05
    pointe.Resolution = 24
    rpo = Show(pointe, vue)
    rpo.ColorArrayName = ["POINTS", ""]
    rpo.AmbientColor = ORANGE
    rpo.DiffuseColor = ORANGE
    tv = Text(registrationName="6 · Vent apparent : texte")
    tv.Text = "vent apparent (15°)"
    rtv = Show(tv, vue)
    rtv.TextPropMode = "Billboard 3D Text"
    rtv.BillboardPosition = [p2[0] - 0.2, p2[1] - 0.15, p2[2]]   # sous la pointe (l'avant est en haut)
    rtv.FontSize = taille_noms - 4
    rtv.Color = ORANGE

    # Axe du navire (x), au pied des voiles, sous les deux rangées
    for k, (pre, nom, dy) in enumerate(CALCULS):
        axe = Line(registrationName=f"5 · Axe du navire (x), rangée {k + 1}")
        axe.Point1 = [-1.2, dy, 0.0]
        axe.Point2 = [1.6, dy, 0.0]
        ra = Show(axe, vue)
        ra.ColorArrayName = ["POINTS", ""]
        ra.AmbientColor = TEAL
        ra.DiffuseColor = TEAL
        ra.LineWidth = 3.0

    titre = Text(registrationName="8 · Titre (texte à l'écran)")
    titre.Text = "Exemple 9 vu de dessus : voiles et vent apparent"
    rt = Show(titre, vue)
    rt.WindowLocation = "Upper Left Corner"
    rt.FontSize = 18
    rt.Color = MARINE
    rt.Bold = 1

    courbe.ChartTitle = "|incidence| de chaque élément"
    courbe.ShowLegend = 1
    courbe.LegendFontSize = 12
    courbe.ChartTitleFontSize = 18
    courbe.LeftAxisTitleFontSize = 15
    courbe.BottomAxisTitleFontSize = 15
    courbe.LeftAxisTitleBold = 0
    courbe.BottomAxisTitleBold = 0
    courbe.ChartTitleColor = MARINE
    courbe.LeftAxisTitleColor = MARINE
    courbe.BottomAxisTitleColor = MARINE
    courbe.LegendLocation = "BottomLeft"
    courbe.BottomAxisTitle = "|incidence| de l'élément (deg)"
    courbe.LeftAxisTitle = "hauteur au-dessus du plan (m)"
    courbe.BottomAxisUseCustomRange = 1
    courbe.BottomAxisRangeMinimum = 0.0
    courbe.BottomAxisRangeMaximum = 90.0
    courbe.LeftAxisUseCustomRange = 1
    courbe.LeftAxisRangeMinimum = 0.0
    courbe.LeftAxisRangeMaximum = 1.4

    # Palette fixée après coup : ColorBy la recale sur les données du premier objet coloré
    lut.AutomaticRescaleRangeMode = "Never"
    lut.RGBPoints = [PLAGE_CL[0], *MARINE, 0.0, *BLANC, PLAGE_CL[1], *TEALD]
    lut.RescaleTransferFunction(*PLAGE_CL)
    GetOpacityTransferFunction("Cl").RescaleTransferFunction(*PLAGE_CL)

    Render(vue)
    # Vue de dessus, un peu inclinée, l'avant du navire en haut de l'écran : on y lit l'angle entre la corde de
    # chaque voile et le vent apparent, et les tourbillons NLL qui partent dans le sens du vent
    vue.CameraFocalPoint = [0.3, -0.6, -0.7]
    vue.CameraPosition = [0.3 - 1.2, -0.6, -0.7 - 6.0]
    vue.CameraViewUp = [1.0, 0.0, 0.0]
    vue.CameraParallelProjection = 1
    vue.CameraParallelScale = 1.8
    Render(vue)
    Render(courbe)
    return vue, courbe


def main():
    ap = argparse.ArgumentParser(description="Trois ailes de Malmek : C_L par élément, bandes et NLL (ParaView).")
    ap.add_argument("--donnees", help="dossier des .vtk (défaut : cas/trois-ailes du dépôt)")
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
