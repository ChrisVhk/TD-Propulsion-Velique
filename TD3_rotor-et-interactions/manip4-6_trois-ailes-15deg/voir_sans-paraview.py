#!/usr/bin/env pvpython
# -*- coding: utf-8 -*-
"""
Voir les trois ailes de Malmek au près dans ParaView — TD 3 Propulsion vélique (EGN-S7, ENSM), manipulation 6

Repli de l'état ParaView vue.pvsm (même dossier) : ce script construit la même vue sans passer par l'état.
(L'état lui-même est enregistré par l'interface graphique de ParaView pour Windows, à partir de la même fonction
construire_vue : un état destiné à l'interface se fabrique et se teste dans l'interface.)

Avant : les deux calculs, dans le terminal Ubuntu (WSL) :

    cd ~/TD-Propulsion-Velique/TD3_rotor-et-interactions/manip4-6_trois-ailes-15deg
    bash lancer.sh

Puis, UNE LIGNE, depuis le même dossier (pvpython vient avec ParaView de WSL : sudo apt install paraview) :

    pvpython voir_sans-paraview.py

Ce que montre la vue (deux vues côte à côte, dans un layout « Trois ailes ») :
  - à gauche, les trois ailes de l'exemple 9 (cas à 15° du LHEEA, réglages −5, −10, −15°) vues en plongée du côté
    d'où vient le vent (l'avant du navire à droite), deux fois : 1 · en théorie des bandes (rangée du haut), 2 · en NLL
    (rangée du bas) ; chaque élément a la couleur de son C_L (Cl, signe de l'outil) ;
    3 · les tourbillons en fer à cheval de la NLL, coupés à 2 m en aval ; 4 · le vent apparent (15° de l'axe du
    navire) ; 5 · l'axe du navire (x, vers l'avant) ; 6 · les noms des deux rangées et des voiles ;
  - à droite, 7 · l'incidence de chaque élément (signe de l'outil, celui de la colonne AoA de results.csv) en fonction
    de sa hauteur, une courbe par voile et par modèle : on y lit ce que la NLL retire à chaque voile, et si les
    éléments travaillent dans le domaine de la table de profil ;
  - 8 · le titre.
Les fichiers lus sont ceux qu'écrit lancer.sh dans sorties/ : bandes_voile-N_*, nll_voile-N_*.

Options :
  --donnees DOSSIER   dossier des .vtk (défaut : sorties/ à côté de ce script)
  --png FICHIER       écrit une capture du layout (1920 x 1080 par défaut)
  --sans-fenetre      n'ouvre pas de fenêtre (avec --png)

Couleurs : charte ENSM (MARINE #1A346D, TEALD #147A6D, TEAL #1A9988, GREY #595959), fond blanc.
CN-AeroModels v0.5.1, LHEEA (Centrale Nantes / CNRS), EPL 2.0 ; exemple 9 (Malmek, 2023) ; vue et script : ENSM.
"""

import argparse
import math
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
PLAGE_CL = [-1.0, 1.0]   # C_L du cas à 15° : entre -0,3 et 1,1 (signe de l'outil)

# Les deux calculs : préfixe des fichiers (lancer.sh), nom affiché, décalage de la rangée (m, y).
CALCULS = (("bandes", "Bandes", -1.6), ("nll", "NLL", 0.0))
VOILES = (1, 2, 3)                                   # voile 1 à l'avant (x = +0,86 m), voile 3 à l'arrière
COULEURS_VOILES = {1: TEAL, 2: MARINE, 3: ORANGE}    # courbes de droite, une couleur par voile
VENT = (-0.9659, -0.2588, 0.0)                       # sens du vent apparent dans le repère des sorties (15° de -x)
X_COUPE = -2.0                                       # m : tourbillons NLL coupés à 2 m en arrière de l'origine
ELEVATION = 55.0                                     # deg : hauteur de la caméra au-dessus de l'horizontale


def dossier_par_defaut():
    ici = os.path.dirname(os.path.abspath(__file__))
    c = os.path.join(ici, "sorties")
    if os.path.isdir(c):
        return c
    sys.exit("Dossier %s introuvable : lancez d'abord bash lancer.sh dans ce dossier." % c)


def fichiers_attendus():
    f = []
    for pre, _, _ in CALCULS:
        for n in VOILES:
            f += ["%s_voile-%d_aile.vtk" % (pre, n), "%s_voile-%d_force.vtk" % (pre, n)]
    return f + ["nll_voile-%d_horseshoeVortex.vtk" % n for n in VOILES]


def construire_vue(dossier, largeur=1920, hauteur=1080, vue=None, courbe=None, taille_noms=22):
    """Construit les deux vues à partir des .vtk de `dossier` ; renvoie (vue de rendu, vue des courbes).
    `vue`, `courbe` : vues déjà rangées dans un layout (interface graphique) ; sinon, vues et layout sont créés."""
    manque = [f for f in fichiers_attendus() if not os.path.isfile(os.path.join(dossier, f))]
    if manque:
        sys.exit("Fichiers absents dans %s : %s\n(lancez d'abord : bash lancer.sh)" % (dossier, ", ".join(manque)))
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
            rep.SetRepresentationType("Surface With Edges")    # arêtes claires : une voile à C_L nul reste visible
            rep.EdgeColor = [0.8, 0.8, 0.8]
            rep.LineWidth = 1.0
            rep.Ambient = 1.0        # couleur sans ombrage : la teinte lue est celle de la barre de C_L
            rep.Diffuse = 0.0
            ColorBy(rep, ("POINTS", "Cl"))
            if premier:
                rep.SetScalarBarVisibility(vue, True)
                premier = False
            # Courbe : incidence, signe de l'outil (axe horizontal), en fonction de la hauteur (axe vertical, z vers le bas)
            inc = Calculator(registrationName=f"(calcul) {cle} : incidence", Input=centres)
            inc.ResultArrayName = "incidence (deg)"
            inc.Function = '"AoA(degrees)/SR"'
            h = Calculator(registrationName=f"7 · Courbe : {cle}", Input=inc)
            h.ResultArrayName = "hauteur (m)"
            h.Function = "-coordsZ"
            rc = Show(h, courbe)
            rc.UseIndexForXAxis = 0
            rc.XArrayName = "incidence (deg)"
            rc.SeriesVisibility = ["hauteur (m)"]
            rc.SeriesLabel = ["hauteur (m)", f"{k + 1}. {nom}, voile {n}"]
            rc.SeriesColor = ["hauteur (m)", *[str(c) for c in COULEURS_VOILES[n]]]
            rc.SeriesLineThickness = ["hauteur (m)", "3" if pre == "nll" else "1"]
            rc.SeriesLineStyle = ["hauteur (m)", "1" if pre == "nll" else "2"]      # NLL plein, bandes tirets
            rc.SeriesMarkerStyle = ["hauteur (m)", "4" if pre == "nll" else "2"]
            rc.SeriesMarkerSize = ["hauteur (m)", "7"]
        # Nom de la rangée, au-dessus de la voile 1
        et = Text(registrationName=f"6 · Nom de la rangée {k + 1}")
        et.Text = f"{k + 1}. {nom}"
        re_ = Show(et, vue)
        re_.TextPropMode = "Billboard 3D Text"
        re_.BillboardPosition = [1.45, dy - 0.25, -1.4]
        re_.FontSize = taille_noms
        re_.Bold = 1
        re_.Color = MARINE if pre == "nll" else GREY

    # Numéros des voiles, au-dessus de la rangée NLL
    for n, x in zip(VOILES, (0.84, 0.09, -0.66)):
        t = Text(registrationName=f"6 · Voile {n}")
        t.Text = f"voile {n}"
        rt_ = Show(t, vue)
        rt_.TextPropMode = "Billboard 3D Text"
        rt_.BillboardPosition = [x + 0.15, 0.25, 0.05]     # au pied de la voile, sous la rangée NLL
        rt_.FontSize = taille_noms - 4
        rt_.Color = COULEURS_VOILES[n]

    # Tourbillons en fer à cheval (NLL), coupés à X_COUPE
    for n in VOILES:
        coupe = Clip(registrationName=f"3 · Tourbillons NLL : voile {n}", Input=lire("nll_voile-%d_horseshoeVortex.vtk" % n))
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
    barre.WindowLocation = "Any Location"     # à droite, entre les deux rangées, hors des textes
    barre.Position = [0.84, 0.55]
    barre.ScalarBarLength = 0.3

    # Vent apparent : une flèche (trait) qui arrive de l'avant, à 15° de l'axe, à mi-hauteur
    p2 = [1.25, 0.15, -1.2]
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
    rtv.BillboardPosition = [p2[0] + 0.05, p2[1] + 0.35, p2[2] + 0.3]   # sous la flèche, à droite de la voile 1
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
    titre.Text = "Trois ailes au près, vues du côté du vent"
    rt = Show(titre, vue)
    rt.WindowLocation = "Upper Left Corner"
    rt.FontSize = 18
    rt.Color = MARINE
    rt.Bold = 1

    courbe.ChartTitle = "Incidence de chaque élément"
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
    courbe.LegendLocation = "TopRight"
    courbe.BottomAxisTitle = "incidence (deg, signe de l'outil)"
    courbe.LeftAxisTitle = "hauteur au-dessus du plan (m)"
    courbe.BottomAxisUseCustomRange = 1
    courbe.BottomAxisRangeMinimum = -5.0
    courbe.BottomAxisRangeMaximum = 25.0     # place à droite pour la légende
    courbe.LeftAxisUseCustomRange = 1
    courbe.LeftAxisRangeMinimum = 0.0
    courbe.LeftAxisRangeMaximum = 1.4

    # Palette fixée après coup : ColorBy la recale sur les données du premier objet coloré
    lut.AutomaticRescaleRangeMode = "Never"
    lut.RGBPoints = [PLAGE_CL[0], *MARINE, 0.0, *BLANC, PLAGE_CL[1], *TEALD]
    lut.RescaleTransferFunction(*PLAGE_CL)
    GetOpacityTransferFunction("Cl").RescaleTransferFunction(*PLAGE_CL)

    Render(vue)
    # Vue plongeante du côté d'où vient le vent (ELEVATION au-dessus de l'horizontale), l'avant du navire à droite :
    # au près, les voiles sont presque dans l'axe et une vue de dessus n'en montrerait que la tranche ; ici, on voit
    # leur surface colorée par C_L, l'angle de leur corde avec l'axe et le vent, et les tourbillons NLL qui partent
    # dans le sens du vent. Rangée 1 (bandes) en haut, rangée 2 (NLL) en bas.
    e = math.radians(ELEVATION)
    foyer = [0.45, -0.8, -0.7]
    vue.CameraFocalPoint = foyer
    vue.CameraPosition = [foyer[0], foyer[1] + 8.0 * math.cos(e), foyer[2] - 8.0 * math.sin(e)]   # z vers le bas
    vue.CameraViewUp = [0.0, -math.sin(e), -math.cos(e)]
    vue.CameraParallelProjection = 1
    vue.CameraParallelScale = 1.55
    Render(vue)
    Render(courbe)
    return vue, courbe


def main():
    ap = argparse.ArgumentParser(description="Trois ailes de Malmek au près : C_L par élément, bandes et NLL (ParaView).")
    ap.add_argument("--donnees", help="dossier des .vtk (défaut : sorties/ à côté de ce script)")
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
