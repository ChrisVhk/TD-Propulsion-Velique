#!/usr/bin/env pvpython
# -*- coding: utf-8 -*-
"""
Voir les deux DynaRigs d'école sur le navire générique dans ParaView — démonstration du TD 3 (EGN-S7, ENSM)

Repli de l'état ParaView vue.pvsm (même dossier) : ce script construit la même vue sans passer par l'état.
(L'état est enregistré par l'interface graphique de ParaView pour Windows, à partir de la même fonction construire_vue.)

Avant, dans le terminal Ubuntu (WSL) :

    cd ~/TD-Propulsion-Velique/TD3_rotor-et-interactions/demo_dynarig-greenpeace
    bash lancer.sh

Puis, depuis le même dossier : pvpython voir_sans-paraview.py   (options : --png FICHIER, --sans-fenetre)

Ce que montre la vue (deux vues côte à côte, layout « DynaRigs ») :
  - à gauche, 1 · la coque générique et 2 · les superstructures en blocs (hypothèses d'école, fabriquer_coque.py),
    3 · les deux voilures d'école colorées par leur C_L (signe de l'outil), 4 · les tourbillons en fer à cheval de la
    NLL, 5 · le vent apparent à mi-hauteur de la voilure, 6 · les noms des mâts et les poussées calculées ; vue de
    trois-quarts arrière, côté tribord (d'où vient le vent), face aux voiles, un peu plongeante ;
  - à droite, 7 · l'incidence de chaque élément (signe de l'outil) en fonction de sa hauteur au-dessus de l'eau, pour
    le mât avant et le mât arrière : le mât arrière travaille à plus faible incidence (vent dévié par le mât avant) ;
  - 8 · le titre.
Navire générique et voilure d'école : ce n'est pas le navire réel. Aucune image, aucun plan d'origine.
Couleurs : charte ENSM (MARINE #1A346D, TEALD #147A6D, TEAL #1A9988, GREY #595959), fond blanc.
CN-AeroModels v0.5.1, LHEEA (Centrale Nantes / CNRS), EPL 2.0 ; vue et script : ENSM, Apache 2.0.
"""

import argparse
import csv
import math
import os
import sys

from paraview.simple import (AssignViewToLayout, Calculator, CellCenters, Clip, ColorBy, Cone, CreateLayout, CreateView,
                             GetColorTransferFunction, GetOpacityTransferFunction, Interact, LegacyVTKReader,
                             Line, MergeBlocks, PointDatasetInterpolator, Render, SaveScreenshot, SetActiveView,
                             Show, Text)


def _rgb(h):
    return [int(h[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]


MARINE, TEALD, TEAL, GREY = (_rgb(c) for c in ("#1A346D", "#147A6D", "#1A9988", "#595959"))
BLANC = [1.0, 1.0, 1.0]
ORANGE = _rgb("#C55A11")
PLAGE_CL = [-1.2, 1.2]
MATS = (("avant", "mât avant", TEAL, 15.0), ("arriere", "mât arrière", ORANGE, -15.0))
X_COUPE = -35.0                 # m : tourbillons coupés à 35 m en arrière du milieu
ELEVATION = 22.0                # deg : hauteur de la caméra au-dessus de l'horizontale
AZIMUT = 140.0                  # deg : caméra à 140° de l'avant, côté tribord (d'où vient le vent) : face aux voiles
PREFIXE = "nll-deux-mats"


def dossier_par_defaut():
    c = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sorties")
    if os.path.isdir(c):
        return c
    sys.exit("Dossier %s introuvable : lancez d'abord bash lancer.sh dans ce dossier." % c)


def fichiers_attendus():
    f = ["coque.vtk", "superstructures.vtk"]
    for m, _, _, _ in MATS:
        f += ["%s_mat-%s_%s.vtk" % (PREFIXE, m, s) for s in ("voile", "force", "horseshoeVortex")]
    return f


def poussees(dossier):
    """F_x (kN) des deux mâts ensemble et du mât arrière seul, lus dans les results.csv de lancer.sh."""
    def lire(nom):
        with open(os.path.join(dossier, nom)) as f:
            return [float(r["Fx(kN)"]) for r in csv.DictReader(f, delimiter=";")]
    try:
        a, r = lire(PREFIXE + "_results.csv")
        s = lire("nll-arriere-seul_results.csv")[0]
        return a, r, s
    except (OSError, KeyError, ValueError):
        return None


def construire_vue(dossier, largeur=1920, hauteur=1080, vue=None, courbe=None, taille_noms=22):
    manque = [f for f in fichiers_attendus() if not os.path.isfile(os.path.join(dossier, f))]
    if manque:
        sys.exit("Fichiers absents dans %s : %s\n(lancez d'abord : bash lancer.sh)" % (dossier, ", ".join(manque)))
    lire = lambda nom: LegacyVTKReader(registrationName=nom, FileNames=[os.path.join(dossier, nom)])

    if vue is None:
        layout = CreateLayout("DynaRigs")
        vue = CreateView("RenderView")
        AssignViewToLayout(view=vue, layout=layout, hint=0)
        courbe = CreateView("XYChartView")
        layout.SplitHorizontal(0, 0.62)
        AssignViewToLayout(view=courbe, layout=layout, hint=2)
    SetActiveView(vue)
    vue.ViewSize = [int(largeur * 0.62), hauteur]
    vue.Background = BLANC
    vue.UseColorPaletteForBackground = 0
    vue.OrientationAxesVisibility = 0

    lut = GetColorTransferFunction("Cl")
    lut.ApplyPreset("Cool to Warm", True)
    lut.RGBPoints = [PLAGE_CL[0], *MARINE, 0.0, *BLANC, PLAGE_CL[1], *TEALD]
    lut.AutomaticRescaleRangeMode = "Never"

    # 1 et 2 : coque et superstructures (hypothèses d'école)
    for num, nom, coul, op in (("1", "coque", [0.80, 0.80, 0.80], 0.9), ("2", "superstructures", [0.65, 0.65, 0.65], 1.0)):
        o = MergeBlocks(registrationName=f"{num} · {'Coque générique' if nom == 'coque' else 'Superstructures (blocs)'}",
                        Input=lire(nom + ".vtk"))
        r = Show(o, vue)
        r.SetRepresentationType("Surface With Edges")
        r.ColorArrayName = ["POINTS", ""]
        r.AmbientColor = coul
        r.DiffuseColor = coul
        r.EdgeColor = GREY
        r.Opacity = op

    premier = True
    for m, nom, coul, _ in MATS:
        centres = CellCenters(registrationName=f"(calcul) {nom} : centres des éléments",
                              Input=lire("%s_mat-%s_force.vtk" % (PREFIXE, m)))
        centres.VertexCells = 1
        cl = PointDatasetInterpolator(registrationName=f"(calcul) {nom} : C_L porté sur la voile", Input=centres,
                                      Source=lire("%s_mat-%s_voile.vtk" % (PREFIXE, m)))
        cl.Kernel = "VoronoiKernel"
        v = MergeBlocks(registrationName=f"3 · Voilure du {nom}", Input=cl)
        rv = Show(v, vue)
        rv.SetRepresentationType("Surface With Edges")
        rv.EdgeColor = [0.8, 0.8, 0.8]
        rv.Ambient = 1.0
        rv.Diffuse = 0.0
        ColorBy(rv, ("POINTS", "Cl"))
        if premier:
            rv.SetScalarBarVisibility(vue, True)
            premier = False
        coupe = Clip(registrationName=f"4 · Tourbillons NLL : {nom}", Input=lire("%s_mat-%s_horseshoeVortex.vtk" % (PREFIXE, m)))
        coupe.ClipType = "Plane"
        coupe.ClipType.Origin = [X_COUPE, 0.0, 0.0]
        coupe.ClipType.Normal = [1.0, 0.0, 0.0]
        coupe.Invert = 0
        rt = Show(coupe, vue)
        rt.SetRepresentationType("Wireframe")
        rt.ColorArrayName = ["POINTS", ""]
        rt.AmbientColor = GREY
        rt.DiffuseColor = GREY
        rt.Opacity = 0.2
        # 7 : incidence en fonction de la hauteur au-dessus de l'eau
        inc = Calculator(registrationName=f"(calcul) {nom} : incidence", Input=centres)
        inc.ResultArrayName = "incidence (deg)"
        inc.Function = '"AoA(degrees)/SR"'
        h = Calculator(registrationName=f"7 · Courbe : {nom}", Input=inc)
        h.ResultArrayName = "hauteur (m)"
        h.Function = "-coordsZ"
        rc = Show(h, courbe)
        rc.UseIndexForXAxis = 0
        rc.XArrayName = "incidence (deg)"
        rc.SeriesVisibility = ["hauteur (m)"]
        rc.SeriesLabel = ["hauteur (m)", nom]
        rc.SeriesColor = ["hauteur (m)", *[str(c) for c in coul]]
        rc.SeriesLineThickness = ["hauteur (m)", "3"]
        rc.SeriesMarkerStyle = ["hauteur (m)", "4"]
        rc.SeriesMarkerSize = ["hauteur (m)", "7"]

    # 6 : noms des mâts, au-dessus de la voilure
    p = poussees(dossier)
    for k, (m, nom, coul, x) in enumerate(MATS):
        t = Text(registrationName=f"6 · Nom : {nom}")
        t.Text = nom if p is None else "%s : %.1f kN" % (nom, p[k])
        rt_ = Show(t, vue)
        rt_.TextPropMode = "Billboard 3D Text"
        rt_.BillboardPosition = [x - 4.0, 16.0, -4.0]      # au pied du mât, côté tribord (vers la caméra)
        rt_.FontSize = taille_noms
        rt_.Bold = 1
        rt_.Color = coul

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
    barre.WindowLocation = "Any Location"
    barre.Position = [0.03, 0.08]
    barre.ScalarBarLength = 0.33

    # 5 : vent apparent à mi-hauteur (31 m) : il vient de tribord avant, vers 65° de l'avant (results.csv, AWA)
    awa = math.radians(65.0)
    sens = (-math.cos(awa), -math.sin(awa), 0.0)
    pointe_xyz = [-5.0, 22.0, -46.0]
    vent = Line(registrationName="5 · Vent apparent")
    vent.Point1 = [pointe_xyz[i] - 22.0 * sens[i] for i in range(2)] + [pointe_xyz[2]]
    vent.Point2 = pointe_xyz
    rw = Show(vent, vue)
    rw.ColorArrayName = ["POINTS", ""]
    rw.AmbientColor = ORANGE
    rw.DiffuseColor = ORANGE
    rw.LineWidth = 5.0
    pointe = Cone(registrationName="5 · Vent apparent : pointe")
    pointe.Center = [pointe_xyz[i] + 1.5 * sens[i] for i in range(2)] + [pointe_xyz[2]]
    pointe.Direction = list(sens)
    pointe.Height = 4.0
    pointe.Radius = 1.4
    pointe.Resolution = 24
    rpo = Show(pointe, vue)
    rpo.ColorArrayName = ["POINTS", ""]
    rpo.AmbientColor = ORANGE
    rpo.DiffuseColor = ORANGE
    tv = Text(registrationName="6 · Vent apparent : texte")
    tv.Text = "vent apparent"
    rtv = Show(tv, vue)
    rtv.TextPropMode = "Billboard 3D Text"
    rtv.BillboardPosition = [pointe_xyz[0] + 4.0, pointe_xyz[1] + 14.0, pointe_xyz[2] + 4.0]
    rtv.FontSize = taille_noms - 4
    rtv.Color = ORANGE

    titre = Text(registrationName="8 · Titre (texte à l'écran)")
    titre.Text = "Deux DynaRigs d'école au travers"
    rt = Show(titre, vue)
    rt.WindowLocation = "Upper Left Corner"
    rt.FontSize = 18
    rt.Color = MARINE
    rt.Bold = 1

    courbe.ChartTitle = "Incidence des éléments"
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
    courbe.BottomAxisTitle = "incidence (deg, signe de l'outil)"
    courbe.LeftAxisTitle = "hauteur au-dessus de l'eau (m)"
    courbe.BottomAxisUseCustomRange = 1
    courbe.BottomAxisRangeMinimum = -10.0
    courbe.BottomAxisRangeMaximum = 5.0
    courbe.LeftAxisUseCustomRange = 1
    courbe.LeftAxisRangeMinimum = 0.0
    courbe.LeftAxisRangeMaximum = 60.0

    lut.AutomaticRescaleRangeMode = "Never"
    lut.RGBPoints = [PLAGE_CL[0], *MARINE, 0.0, *BLANC, PLAGE_CL[1], *TEALD]
    lut.RescaleTransferFunction(*PLAGE_CL)
    GetOpacityTransferFunction("Cl").RescaleTransferFunction(*PLAGE_CL)

    Render(vue)
    e = math.radians(ELEVATION)
    foyer = [0.0, 0.0, -27.0]
    vue.CameraFocalPoint = foyer
    a = math.radians(AZIMUT)
    d = (math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), -math.sin(e))       # z vers le bas
    vue.CameraPosition = [foyer[i] + 300.0 * d[i] for i in range(3)]
    vue.CameraViewUp = [-math.cos(a) * math.sin(e), -math.sin(a) * math.sin(e), -math.cos(e)]
    vue.CameraParallelProjection = 1
    vue.CameraParallelScale = 38.0
    Render(vue)
    Render(courbe)
    return vue, courbe


def main():
    ap = argparse.ArgumentParser(description="Deux DynaRigs d'école sur le navire générique (ParaView).")
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
