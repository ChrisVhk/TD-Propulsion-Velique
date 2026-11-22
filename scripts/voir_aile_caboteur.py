#!/usr/bin/env pvpython
# -*- coding: utf-8 -*-
"""
Voir l'aile du caboteur dans ParaView — TD Propulsion vélique (EGN-S7, ENSM)

Repli de l'état ParaView cas/Cas-ENSM_aile-du-caboteur/aile_caboteur.pvsm :
ce script construit la même vue sans passer par l'état. (L'état lui-même est fabriqué par l'enseignant dans
l'interface graphique de ParaView pour Windows, à partir de la même fonction construire_vue : un état destiné
à l'interface se fabrique et se teste dans l'interface.)

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
       - à l'écran : un titre court, la barre de couleur de C_L et les étiquettes x, y, z ; la légende des
         objets et la note sur le repère NED sont dans la fiche du TD (manipulation 2 bis), pas dans la vue ;
       - caméra de côté, depuis tribord, un peu en arrière et un peu au-dessus de la mer ;
  3. il ouvre une fenêtre (fermer la fenêtre pour finir), ou écrit une image sans fenêtre.

Options :
  --donnees DOSSIER   ne relance pas l'outil : lit les .vtk déjà écrits dans DOSSIER
  --depot DOSSIER     dossier du dépôt du TD, si le script n'est pas rangé dans son dossier scripts/
  --png FICHIER       écrit une capture (1920 x 1080 par défaut)
  --sans-fenetre      n'ouvre pas de fenêtre (avec --png)

Couleurs : charte ENSM (MARINE #1A346D, TEALD #147A6D, TEAL #1A9988, GREY #595959), fond blanc.
CN-AeroModels v0.5.1, LHEEA (Centrale Nantes / CNRS), EPL 2.0 ; vue et script : ENSM.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

from paraview.simple import (Arrow, AssignViewToLayout, CellCenters, Clip, ColorBy, CreateLayout, CreateView,
                             GetColorTransferFunction, GetOpacityTransferFunction, Glyph, Interact,
                             LegacyVTKReader, MergeBlocks, PointDatasetInterpolator, Render, SaveScreenshot,
                             SetActiveView, Show, Text, Transform)

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
# Graduations de la barre : format automatique, sans étiquettes d'extrémité. Aucune chaîne de format n'est alors
# utilisée : ni avertissement « printf format » (ParaView 6.1 et plus), ni « {:.1f} » affiché en clair (ParaView 6.0,
# qui ne connaît pas encore la syntaxe std::format). Le pré-vol accepte toute version 6.x.
# Caméra de côté : point visé, direction de visée (du point visé vers la caméra) et demi-hauteur de l'écran.
# Depuis tribord (+y), 20° en arrière du travers (-x), 30° au-dessus de la mer (-z en NED) : on voit la face
# de l'aile (ses trois bandes) et les flèches d'effort presque en long ; à l'écran, x (l'avant) part à droite
# en montant, y (tribord) à droite en descendant, l'effort entre les deux.
CAMERA_VISEE = [0.0, -12.0, -14.0]
CAMERA_DIRECTION = [-0.296, 0.814, -0.500]
CAMERA_DEMI_HAUTEUR = 39.0   # m (projection parallèle)


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


def construire_vue(dossier, largeur=1920, hauteur=1080, vue=None, taille_etiquettes=28):
    """Construit la vue à partir des quatre .vtk de `dossier` ; renvoie la vue.

    La vue est rangée dans un layout (sans layout, l'interface graphique n'affiche rien après Load State).
    `vue` : vue de rendu déjà rangée dans un layout (interface graphique) ; sinon, vue et layout sont créés.
    `taille_etiquettes` : police des étiquettes x, y, z (texte 3D). L'interface graphique les rend environ deux fois
    plus petites que pvpython à même valeur (constaté sous 6.1.1 et 6.2.1) : construire_etat.py passe 32, pvpython garde 28."""
    for f in FICHIERS.values():
        if not os.path.isfile(os.path.join(dossier, f)):
            sys.exit(f"Fichier absent : {os.path.join(dossier, f)} (l'outil a-t-il été lancé avec --vtk 1 ?)")
    # Noms du Pipeline Browser (session 11 h) : chaque nom est unique ; les fichiers lus portent leur nom de fichier ;
    # les objets visibles sont numérotés dans l'ordre de la légende de la fiche (1 à 5, puis 6 pour le titre) ;
    # les filtres intermédiaires commencent par « (calcul) » et ne sont pas affichés (œil éteint).
    lire = lambda cle: LegacyVTKReader(registrationName=FICHIERS[cle],
                                       FileNames=[os.path.join(dossier, FICHIERS[cle])])

    if vue is None:
        vue = CreateView("RenderView")
        AssignViewToLayout(view=vue, layout=CreateLayout("Aile du caboteur"), hint=0)
    SetActiveView(vue)
    vue.ViewSize = [largeur, hauteur]
    vue.Background = BLANC
    vue.UseColorPaletteForBackground = 0
    vue.OrientationAxesVisibility = 0   # repère dessiné dans la scène, à l'origine
    vue.OrientationAxesLabelColor = MARINE
    vue.OrientationAxesXColor = MARINE
    vue.OrientationAxesYColor = TEALD
    vue.OrientationAxesZColor = GREY

    aile = lire("aile")
    efforts = lire("efforts")
    vent = lire("vent")
    mer = lire("mer")

    # Efforts : une cellule (dégénérée) par bande -> un point par bande, au centre de la bande.
    centres = CellCenters(registrationName="(calcul) centres des bandes", Input=efforts)
    centres.VertexCells = 1

    # Aile colorée par C_L : la valeur de chaque bande est portée sur les sommets de l'aile
    # (noyau de Voronoï : le centre de bande le plus proche ; filtre natif, sans Python).
    # Ce filtre a deux entrées : le Pipeline Browser l'affiche sous chacune (lien) et une fois pour lui-même. Il reste
    # donc un intermédiaire, et l'aile affichée est sa copie à une seule entrée (Merge Blocks : copie à l'identique
    # d'un jeu de données simple), qui n'apparaît qu'une fois dans l'arbre.
    aile_cl = PointDatasetInterpolator(registrationName="(calcul) C_L de chaque bande porté sur l'aile",
                                       Input=centres, Source=aile)
    aile_cl.Kernel = "VoronoiKernel"
    aile_vue = MergeBlocks(registrationName="1 · Aile (3 bandes, colorée par C_L)", Input=aile_cl)

    rep_aile = Show(aile_vue, vue)
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
    barre.Title = "C_L (Cl)"
    barre.ComponentTitle = ""
    barre.TitleColor = MARINE
    barre.LabelColor = MARINE
    barre.TitleFontSize = 16
    barre.LabelFontSize = 14
    barre.AutomaticLabelFormat = 1
    barre.AddRangeLabels = 0
    barre.WindowLocation = "Upper Right Corner"
    barre.ScalarBarLength = 0.4

    # Flèches d'effort : une par bande, dans la direction de dForce, longueur proportionnelle.
    fleches = Glyph(registrationName="2 · Efforts par bande (flèches dForce)", Input=centres, GlyphType="Arrow")
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
    fl_vent = Glyph(registrationName="(calcul) flèches du vent sur toute la grille", Input=vent, GlyphType="Arrow")
    fl_vent.OrientationArray = ["POINTS", "TWS"]
    fl_vent.ScaleArray = ["POINTS", "TWS"]
    fl_vent.ScaleFactor = ECHELLE_VENT
    fl_vent.GlyphMode = "All Points"
    vent_bas = fl_vent
    decoupes = (("sous 37 m", [0.0, 0.0, -37.0], [0.0, 0.0, -1.0]),    # garde z > -37
                                  ("au-dessus de 12 m", [0.0, 0.0, -12.0], [0.0, 0.0, 1.0]),  # garde z < -12
                                  ("côté bâbord", [0.0, -25.0, 0.0], [0.0, 1.0, 0.0]),      # garde y < -25
                                  ("x > -37 m", [-37.0, 0.0, 0.0], [-1.0, 0.0, 0.0]),         # garde x > -37
                                  ("x < 37 m", [37.0, 0.0, 0.0], [1.0, 0.0, 0.0]))            # garde x < 37
    for k, (nom, origine, normale) in enumerate(decoupes):
        # La dernière découpe est l'objet affiché : elle porte le nom de ce qu'on voit.
        nom_objet = "3 · Vent vrai (flèches TWS)" if k == len(decoupes) - 1 else f"(calcul) vent : {nom}"
        vent_bas = Clip(registrationName=nom_objet, Input=vent_bas)
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
            ("x", [0, 0, 0], MARINE, "x", [21.0, 0.0, 1.0]),
            ("y", [0, 0, 90], MARINE, "y", [0.0, 21.5, 1.0]),
            ("z (vers le bas)", [0, -90, 0], GREY, "z", [1.0, 0.0, 21.0])):
        fl = Arrow(registrationName=f"(calcul) flèche de l'axe {texte}")
        fl.TipRadius = 0.06
        fl.ShaftRadius = 0.018
        tr = Transform(registrationName=f"5 · Repère NED : axe {nom}", Input=fl)
        tr.Transform = "Transform"
        tr.Transform.Scale = [20.0, 20.0, 20.0]
        tr.Transform.Rotate = rot
        ra = Show(tr, vue)
        ra.ColorArrayName = ["POINTS", ""]
        ra.AmbientColor = couleur
        ra.DiffuseColor = couleur
        et = Text(registrationName=f"5 · Repère NED : lettre {texte}")
        et.Text = texte
        re_ = Show(et, vue)
        re_.TextPropMode = "Billboard 3D Text"
        re_.BillboardPosition = pos
        re_.FontSize = taille_etiquettes
        re_.Bold = 1
        re_.Color = couleur

    # Surface de la mer : plan z = 0 (copie à une entrée du fichier lu, qui garde le nom du fichier).
    rep_mer = Show(MergeBlocks(registrationName="4 · Surface de la mer", Input=mer), vue)
    rep_mer.ColorArrayName = ["POINTS", ""]
    rep_mer.AmbientColor = TEAL
    rep_mer.DiffuseColor = TEAL
    rep_mer.Opacity = 0.22

    # Un seul texte à l'écran, court (ARB-EGN-S7-032) : la légende des objets et le repère NED sont dans la fiche.
    titre = Text(registrationName="6 · Titre (texte à l'écran)")
    titre.Text = "Aile du caboteur (CN-AeroModels --vtk 1)"
    rt = Show(titre, vue)
    rt.WindowLocation = "Upper Left Corner"
    rt.FontSize = 18
    rt.Color = MARINE
    rt.Bold = 1

    Render(vue)   # premier rendu d'abord : il recadre la caméra, qu'on pose ensuite
    # Caméra de côté, depuis tribord, un peu en arrière et un peu au-dessus de la mer : l'aile debout
    # (haut de l'écran = -z, NED), ses trois bandes, les flèches d'effort vers l'avant et le repère au pied.
    vue.CameraFocalPoint = CAMERA_VISEE
    vue.CameraPosition = [CAMERA_VISEE[i] + 200.0 * CAMERA_DIRECTION[i] for i in range(3)]
    vue.CameraViewUp = [0.0, 0.0, -1.0]
    vue.CameraParallelProjection = 1   # projection parallèle : toutes les flèches à la même échelle
    vue.CameraParallelScale = CAMERA_DEMI_HAUTEUR
    Render(vue)
    return vue


def main():
    ap = argparse.ArgumentParser(description="Vue ParaView de l'aile du caboteur (CN-AeroModels --vtk 1).")
    ap.add_argument("--donnees", help="dossier des .vtk déjà écrits (sinon : le cas est relancé)")
    ap.add_argument("--depot", help="dossier du dépôt TD-Propulsion-Velique, si le script n'y est pas rangé")
    ap.add_argument("--png", help="écrit une capture PNG")
    ap.add_argument("--sans-fenetre", action="store_true", help="n'ouvre pas de fenêtre")
    ap.add_argument("--largeur", type=int, default=1920)
    ap.add_argument("--hauteur", type=int, default=1080)
    a = ap.parse_args()

    dossier = os.path.abspath(a.donnees) if a.donnees else lancer_cas(a.depot)
    vue = construire_vue(dossier, a.largeur, a.hauteur)
    if a.png:
        SaveScreenshot(a.png, vue, ImageResolution=[a.largeur, a.hauteur], OverrideColorPalette="WhiteBackground")
        print("Capture écrite :", a.png)
    if not a.sans_fenetre:
        print("Fenêtre ParaView ouverte : souris pour tourner, molette pour zoomer ; fermer la fenêtre pour finir.")
        Interact(vue)


if __name__ == "__main__":
    main()
