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

Deux onglets (session 17, ARB-EGN-S7-074).

Onglet « Interaction » (celui qui s'ouvre ; deux vues côte à côte) :
  - à gauche, 9 · une seule rangée de voiles (NLL), colorée par l'ÉCART D'INCIDENCE NLL − bandes de chaque élément
    (degrés, barre divergente centrée sur 0) : l'effet des réglages, différents d'une voile à l'autre, disparaît ; il
    reste ce que l'interaction (et l'effet 3D) retire à chaque élément ; 12 · le bilan chiffré : C_x de chaque voile
    seule et ensemble (NLL), et la perte ;
  - à droite, la vue de dessus, l'avant en haut : 10 · le vent apparent local à mi-hauteur de chaque voile, au quart de
    corde, en théorie des bandes (gris : le même pour les trois) et 11 · en NLL (bleu : il tourne de voile en voile),
    d'après les colonnes ApparentVelocity des sorties par élément de l'outil, vitesses induites comprises, et l'angle
    dont il a tourné ; les voiles (9) vues par la tranche.
Données : fabriquer_interaction.py (lancé par lancer.sh) : interaction_voile-N.vtk, vent-local_*.vtk,
interaction_bilan.csv.

Onglet « Bandes et NLL » (l'ancienne vue, gardée ; deux vues côte à côte) :
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

import csv

from paraview.simple import (AssignViewToLayout, Calculator, CellCenters, Clip, ColorBy, Cone, CreateLayout, CreateView,
                             GetColorTransferFunction, GetOpacityTransferFunction, Glyph, Interact, LegacyVTKReader,
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


PLAGE_ECART = [-6.0, 6.0]                            # deg : écart d'incidence NLL − bandes (−2 à −5° ici)
ECHELLE_VENT = 0.024                                 # m par m/s : 25 m/s -> flèche de 0,6 m (voiles à 0,75 m)


def fichiers_attendus():
    f = []
    for pre, _, _ in CALCULS:
        for n in VOILES:
            f += ["%s_voile-%d_aile.vtk" % (pre, n), "%s_voile-%d_force.vtk" % (pre, n)]
    f += ["interaction_voile-%d.vtk" % n for n in VOILES] + ["vent-local_bandes.vtk", "vent-local_nll.vtk"]
    return f + ["nll_voile-%d_horseshoeVortex.vtk" % n for n in VOILES]


def bilan(dossier):
    """Lignes de interaction_bilan.csv (fabriquer_interaction.py), ou None."""
    try:
        with open(os.path.join(dossier, "interaction_bilan.csv"), newline="") as f:
            return list(csv.DictReader(f, delimiter=";"))
    except OSError:
        return None


def _v(x, n=3):
    return ("%.*f" % (n, float(x))).replace("-", "−").replace(".", ",")


def texte_bilan(lignes):
    if not lignes:
        return "Bilan : lancez bash lancer.sh"
    t = ["C_x (NLL)     seule   ensemble"]
    for r in lignes:
        nom = "somme  " if r["voile"] == "somme" else "voile %s" % r["voile"]
        s, e = float(r["Cx_seule"]), float(r["Cx_ensemble"])
        fin = "(négatif dès seule)" if s < 0 else "(%s %%)" % _v(r["perte_pct"], 0)
        t.append("%s   %6s   %6s   %s" % (nom, _v(s), _v(e), fin))
    return "\n".join(t)


def construire_vue(dossier, largeur=1920, hauteur=1080, vue=None, courbe=None, taille_noms=22, inter=None,
                   dessus=None):
    """Construit les deux onglets à partir des .vtk de `dossier` ; renvoie (vue, courbe, inter, dessus) : l'ancienne
    vue et ses courbes (onglet « Bandes et NLL »), la vue de l'interaction et la vue de dessus (onglet « Interaction »).
    Vues déjà rangées dans des layouts (interface graphique) ; sinon, vues et layouts sont créés."""
    manque = [f for f in fichiers_attendus() if not os.path.isfile(os.path.join(dossier, f))]
    if manque:
        sys.exit("Fichiers absents dans %s : %s\n(lancez d'abord : bash lancer.sh)" % (dossier, ", ".join(manque)))
    lecteurs = {}

    def lire(nom):              # un lecteur par fichier, partagé par les deux onglets (noms uniques)
        if nom not in lecteurs:
            lecteurs[nom] = LegacyVTKReader(registrationName=nom, FileNames=[os.path.join(dossier, nom)])
        return lecteurs[nom]

    if inter is None:
        lay_i = CreateLayout("Interaction")
        inter = CreateView("RenderView")
        AssignViewToLayout(view=inter, layout=lay_i, hint=0)
        lay_i.SplitHorizontal(0, 0.55)
        dessus = CreateView("RenderView")
        AssignViewToLayout(view=dessus, layout=lay_i, hint=2)
    if vue is None:
        layout = CreateLayout("Bandes et NLL")
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
            rc.SeriesLabel = ["hauteur (m)", f"{nom}, v{n}"]
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
    courbe.LegendLocation = "BottomRight"     # session 17 : en haut à droite, la légende était coupée à 1366
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
    construire_interaction(dossier, lire, inter, dessus, taille_noms, largeur, hauteur)
    return vue, courbe, inter, dessus


def construire_interaction(dossier, lire, inter, dessus, taille_noms, largeur, hauteur):
    """Onglet « Interaction » : écart d'incidence NLL − bandes (couleur), vent local vu de dessus, bilan chiffré."""
    for v, frac in ((inter, 0.55), (dessus, 0.45)):
        SetActiveView(v)
        v.ViewSize = [int(largeur * frac), hauteur]
        v.Background = BLANC
        v.UseColorPaletteForBackground = 0
        v.OrientationAxesVisibility = 0
    lut = GetColorTransferFunction("ecart_incidence")
    lut.ApplyPreset("Cool to Warm", True)
    lut.AutomaticRescaleRangeMode = "Never"
    lut.RGBPoints = [PLAGE_ECART[0], *ORANGE, 0.0, *BLANC, PLAGE_ECART[1], *TEAL]
    lut.RescaleTransferFunction(*PLAGE_ECART)
    GetOpacityTransferFunction("ecart_incidence").RescaleTransferFunction(*PLAGE_ECART)
    premier = True
    for n in VOILES:
        ec = PointDatasetInterpolator(registrationName=f"(calcul) voile {n} : écart d'incidence porté sur l'aile",
                                      Input=lire("interaction_voile-%d.vtk" % n), Source=lire("nll_voile-%d_aile.vtk" % n))
        ec.Kernel = "VoronoiKernel"
        o = MergeBlocks(registrationName=f"9 · Interaction : voile {n}", Input=ec)
        for v in (inter, dessus):
            r = Show(o, v)
            if v is dessus:                  # vue par la tranche : les arêtes, épaisses, montrent la corde
                r.SetRepresentationType("Wireframe")
                r.LineWidth = 5.0
            else:
                r.SetRepresentationType("Surface With Edges")
                r.EdgeColor = [0.8, 0.8, 0.8]
            r.Ambient = 1.0
            r.Diffuse = 0.0
            ColorBy(r, ("POINTS", "ecart_incidence"))
        if premier:
            Show(o, inter).SetScalarBarVisibility(inter, True)
            premier = False
        t = Text(registrationName=f"12 · Interaction : nom de la voile {n}")
        t.Text = f"voile {n}"
        rt_ = Show(t, inter)
        rt_.TextPropMode = "Billboard 3D Text"
        rt_.BillboardPosition = [(0.84, 0.09, -0.66)[n - 1] + 0.15, 0.25, 0.05]
        rt_.FontSize = taille_noms + 4
        rt_.Color = COULEURS_VOILES[n]
    barre = lut.GetScalarBar(inter) if hasattr(lut, "GetScalarBar") else None
    if barre is None:
        from paraview.simple import GetScalarBar
        barre = GetScalarBar(lut, inter)
    barre.Title = "incidence NLL − bandes (deg)"
    barre.ComponentTitle = ""
    barre.TitleColor = MARINE
    barre.LabelColor = MARINE
    barre.TitleFontSize = 12
    barre.LabelFontSize = 11
    barre.AutomaticLabelFormat = 1
    barre.AddRangeLabels = 0
    barre.WindowLocation = "Any Location"
    barre.Position = [0.86, 0.40]
    barre.ScalarBarLength = 0.33
    axe = Line(registrationName="13 · Axe du navire (x), onglet Interaction")
    axe.Point1 = [-1.2, 0.0, 0.0]
    axe.Point2 = [1.6, 0.0, 0.0]
    for v in (inter, dessus):
        ra = Show(axe, v)
        ra.ColorArrayName = ["POINTS", ""]
        ra.AmbientColor = TEAL
        ra.DiffuseColor = TEAL
        ra.LineWidth = 3.0
    # Bilan chiffré (lu dans interaction_bilan.csv : sorties de lancer.sh)
    b = bilan(dossier)
    tb = Text(registrationName="12 · Bilan chiffré (texte à l'écran)")
    tb.Text = texte_bilan(b)
    rb = Show(tb, inter)
    rb.WindowLocation = "Lower Left Corner"
    rb.FontSize = 10           # l'interface de ParaView rend les textes 2D environ deux fois plus gros que pvpython
    rb.Color = MARINE
    rb.FontFamily = "Courier"
    rb.Justification = "Left"
    ti = Text(registrationName="14 · Titre de l'onglet Interaction (texte à l'écran)")
    ti.Text = "Ce que l'interaction retire à chaque voile"
    rti = Show(ti, inter)
    rti.WindowLocation = "Upper Left Corner"
    rti.FontSize = 14
    rti.Color = MARINE
    rti.Bold = 1
    # Vent apparent local à mi-hauteur, au quart de corde : bandes (gris, dessous) et NLL (bleu, dessus)
    for pre, num, coul, dz in (("bandes", "10", [0.70, 0.70, 0.70], 0.02), ("nll", "11", MARINE, -0.02)):
        g = Glyph(registrationName=f"{num} · Vent local, {'bandes' if pre == 'bandes' else 'NLL'}",
                  Input=lire("vent-local_%s.vtk" % pre), GlyphType="Arrow")
        g.OrientationArray = ["POINTS", "vent_local"]
        g.ScaleArray = ["POINTS", "vent_local"]
        g.ScaleFactor = ECHELLE_VENT
        g.GlyphMode = "All Points"
        g.GlyphType.TipLength = 0.18
        g.GlyphType.TipRadius = 0.06
        g.GlyphType.ShaftRadius = 0.02
        g.GlyphTransform.Translate = [0.0, 0.0, dz]
        rg = Show(g, dessus)
        rg.ColorArrayName = ["POINTS", ""]
        rg.AmbientColor = coul
        rg.DiffuseColor = coul
        rg.Ambient = 1.0
        rg.Diffuse = 0.0
    if b:
        for r in b:
            if r["voile"] == "somme":
                continue
            n = int(r["voile"])
            t = Text(registrationName=f"11 · Vent local NLL : angle, voile {n}")
            t.Text = f"voile {n} : vent tourné de {_v(r['rotation_deg'], 1)}°"
            rt_ = Show(t, dessus)
            rt_.TextPropMode = "Billboard 3D Text"
            rt_.BillboardPosition = [(0.84, 0.09, -0.66)[n - 1] + 0.05, 0.12, -1.0]
            rt_.FontSize = taille_noms + 2
            rt_.Color = COULEURS_VOILES[n]
    td = Text(registrationName="14 · Titre de la vue de dessus (texte à l'écran)")
    td.Text = "Vent local, vu de dessus (avant en haut)\ngris : bandes ; bleu : NLL"
    rtd = Show(td, dessus)
    rtd.WindowLocation = "Lower Right Corner"
    rtd.Justification = "Right"
    rtd.FontSize = 10
    rtd.Color = MARINE
    # Caméras : la rangée NLL en plongée, du côté du vent (comme l'ancienne vue) ; dessus : l'avant en haut
    Render(inter)
    e = math.radians(ELEVATION)
    foyer = [0.10, 0.0, -0.75]
    inter.CameraFocalPoint = foyer
    inter.CameraPosition = [foyer[0], foyer[1] + 8.0 * math.cos(e), foyer[2] - 8.0 * math.sin(e)]
    inter.CameraViewUp = [0.0, -math.sin(e), -math.cos(e)]
    inter.CameraParallelProjection = 1
    inter.CameraParallelScale = 1.45
    Render(dessus)
    foyer = [-0.10, 0.25, -0.7]
    dessus.CameraFocalPoint = foyer
    dessus.CameraPosition = [foyer[0], foyer[1], foyer[2] - 8.0]       # au-dessus (z vers le bas)
    dessus.CameraViewUp = [1.0, 0.0, 0.0]                              # l'avant (x) en haut de l'écran
    dessus.CameraParallelProjection = 1
    dessus.CameraParallelScale = 1.2
    # Palette fixée après coup : ColorBy la recale sur les données (centrée sur 0, symétrique)
    lut.AutomaticRescaleRangeMode = "Never"
    lut.RGBPoints = [PLAGE_ECART[0], *ORANGE, 0.0, *BLANC, PLAGE_ECART[1], *TEAL]
    lut.RescaleTransferFunction(*PLAGE_ECART)
    GetOpacityTransferFunction("ecart_incidence").RescaleTransferFunction(*PLAGE_ECART)
    Render(inter)
    Render(dessus)


def main():
    ap = argparse.ArgumentParser(description="Trois ailes de Malmek au près : C_L par élément, bandes et NLL (ParaView).")
    ap.add_argument("--donnees", help="dossier des .vtk (défaut : sorties/ à côté de ce script)")
    ap.add_argument("--png", help="écrit une capture PNG du layout")
    ap.add_argument("--sans-fenetre", action="store_true", help="n'ouvre pas de fenêtre")
    ap.add_argument("--largeur", type=int, default=1920)
    ap.add_argument("--hauteur", type=int, default=1080)
    a = ap.parse_args()
    dossier = os.path.abspath(a.donnees) if a.donnees else dossier_par_defaut()
    vue, courbe, inter, dessus = construire_vue(dossier, a.largeur, a.hauteur)
    if a.png:
        from paraview.simple import GetLayout
        racine, ext = os.path.splitext(a.png)
        for v, nom in ((inter, a.png), (vue, racine + "_bandes-et-nll" + ext)):
            SaveScreenshot(nom, GetLayout(v), ImageResolution=[a.largeur, a.hauteur],
                           OverrideColorPalette="WhiteBackground")
            print("Capture écrite :", nom)
    if not a.sans_fenetre:
        print("Fenêtre ParaView ouverte : souris pour tourner, molette pour zoomer ; fermer la fenêtre pour finir.")
        Interact(vue)


if __name__ == "__main__":
    main()
