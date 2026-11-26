# Démonstration — deux DynaRigs d'école sur le navire de Greenpeace (TD 3)

Démonstration de l'enseignant (5 min, fin de la partie 2 du TD 3) et point 6 du compte rendu (fardage).

```bash
cd ~/TD-Propulsion-Velique/TD3_rotor-et-interactions/demo_dynarig-greenpeace
bash lancer.sh          # calcul NLL (deux mâts, puis chaque mât seul) et sorties ParaView dans sorties/
python3 fardage.py      # compte rendu, point 6
```

Dans ParaView pour Windows : *File > Load State* > `vue.pvsm` (ce dossier), *Search files under specified directory*,
*Data Directory* proposé. Repli sans l'interface : `pvpython voir_sans-paraview.py`.

**Le navire réel n'est pas représenté.** Les chiffres publiés ci-dessous fixent les dimensions ; tout le reste est une
hypothèse d'école, écrite en tête de `fabriquer_cas.py` (calcul), `fabriquer_coque.py` (coque et superstructures) et
`fabriquer_polaire.py` (polaire). Aucune image, aucun plan, aucune livrée ni aucun logo du navire n'est dans ce dépôt.

## Chiffres publiés (relus le 26/11/2026)

| Donnée | Valeur | Source |
|---|---|---|
| Longueur, largeur, tirant d'eau | 75,00 × 13,35 m, 5,50 m (74,95 m chez Foundation Zero, valeur du calcul) | chantier Freire, page « Greenpeace International » ; Foundation Zero |
| Vitesse, personnes | 14,10 nœuds ; 38 personnes | chantier Freire |
| Classe glace | Polar Class 7 (eaux polaires avec glace) | chantier Freire ; Dykstra : « ice-class vessel » |
| Équipements | plate-forme d'envol (hélicoptère et drones), embarcations annexes, ROV, AUV, submersibles, laboratoires | chantier Freire ; Dykstra (« ROV and submersible deployment ») |
| Voilure | **2 000 m²** annoncés en 2024, au contrat ; **1 746 m²** publiés en 2026 | voir ci-dessous |
| Mâts | deux DynaRigs tournants, **60 m chacun**, construits par Southern Spars en Pologne | *Yacht*, 15/08/2026 ; Southern Spars |
| Tirant d'air | 57,85 m | Foundation Zero |

**Voilure : un écart daté.** 2 000 m² est le chiffre annoncé en 2024, au contrat : Southern Spars, « Southern Spars
contract with Greenpeace » (contrat avec Greenpeace International, 6 août 2024) : « a substantial sail area of 2000
square metres, supplied by North Sails » (southernspars.com/portfolio/southern-spars-contract-with-greenpeace/), repris
par *Yacht* le 15/08/2026 (« 2,000 square metres of North Sails canvas »). 1 746 m² est le chiffre publié en 2026 :
Foundation Zero, et le chantier Freire (« dos velas de casi 1.746 m2 »). L'écart est écrit tel quel ; aucune source
n'écrit que le projet a changé. **Le calcul garde 1 746 m²** (873 m² par mât) ; 2 000 m² donneraient environ +15 %.

**Mâts de 60 m et tirant d'air de 57,85 m.** *Yacht* (yacht.de, « Construction update: 75-metre-long DynaRig for
Greenpeace », S. Gehlhaus, 15/08/2026) : « Two masts, each 60 metres long, are being built at Southern Spars in Poland ».
Le tirant d'air publié est de 57,85 m au-dessus de l'eau, et le pont de l'hypothèse est à 3 m : la longueur du mât compte
sans doute sa partie sous le pont, jusqu'à son emplanture. **C'est une hypothèse** : aucune source ne le dit.

Pages relues le 26/11/2026 : southernspars.com (page du contrat ; brochure DynaRig, juillet 2026) ; yacht.de/en ;
freireshipyard.com (page « Greenpeace International ») ; dykstra-na.nl (« 75 m Greenpeace / Dynarig Vessel »). Le
chiffre de 1 746 m² chez afloat.ie (« two rotating masts carrying a combined 1,746 square metres of sail ») : page non
relue le 26/11 par l'agent, à vérifier.

## Le rendu : une couche d'habillage (session 17, ARB-EGN-S7-072)

**Le calcul porte sur la ligne portante, le rendu montre le gréement.** Dans la vue, la surface plane colorée par C_L
est celle que l'outil calcule (une par mât, 40 éléments) ; tout le reste est un habillage construit par script, qui ne
change aucun effort (137,1 kN au total, valeurs inchangées). Scripts : `fabriquer_coque.py` (coque, pont, pavois,
superstructures), `fabriquer_greement.py` (mâts, vergues, voiles), lancés par `lancer.sh` après le calcul.

| Élément | Ce qui est relevé (source) | Ce qui est inventé (hypothèse d'école) |
|---|---|---|
| Coque | longueur 74,95 m, largeur 13,35 m, tirant d'eau 5,5 m (Foundation Zero ; Freire) | la forme : Série 60, C_B = 0,65 (Todd, 1963, domaine public ; celle du caboteur, `communs/caboteur-serie60.vtk`, construite par `communs/construire_coque_serie60.py`), mise à l'échelle par morceaux ; franc-bord 3,0 m ; pont plat ; pavois de 1,0 m |
| Classe glace | « Polar Class 7 » (Freire), « ice-class vessel » (Dykstra) | une ceinture plus sombre à la flottaison sur le quart avant, qui la **suggère** ; l'étrave réelle n'est pas représentée |
| Superstructures | **rien** : les rendus publics (pages de Dykstra et de Foundation Zero) n'ont pas pu être regardés dans cette session ; proportions à vérifier par l'enseignant | rouf bas entre les mâts (24 × 10 × 2,6 m) et timonerie à l'arrière (8 × 10 × 5,6 m), positions et tailles de la session 16 b, gardées |
| Mâts | deux mâts tournants (Dykstra) ; 60 m de long chacun (*Yacht*, 15/08/2026) | cylindres de 1,0 m de rayon, du pont à 57 m au-dessus de l'eau (sous le tirant d'air publié, 57,85 m) ; placés au quart de la corde, là où l'outil met l'axe de la voile |
| Vergues | **six par mât**, courbes, fixées au mât, aux limites de cinq voiles sans jour entre elles : Maltese Falcon (« Each of Maltese Falcon's masts supports six yards, which [...] have built-in camber of 12% », Wikipedia, « Maltese Falcon (yacht) », lu le 26/11/2026) ; Southern Spars, brochure DynaRig (juillet 2026) : « curved yard arms », cinq voiles par mât, « one sail per yard arm ». Pour le navire de Greenpeace, le nombre n'est pas publié : six **par analogie** avec le Maltese Falcon | cambrure des vergues 10 %, celle de la polaire d'école (le Maltese Falcon : 12 %) ; tubes de 0,35 m de rayon |
| Voiles | 1 746 m² au total (voir plus haut) | cinq panneaux par mât, cordes 19,77 / 19,77 / 19,77 / 17,79 / 13,84 m, 9,6 m de haut (ceux du calcul) ; voiles creuses en arc de cambrure 10 % (polaire d'école), creux vers l'avant, au réglage de la démonstration (−70°) |
| Couleurs | — | neutres : coque sombre, pont clair, superstructures blanches, voiles claires ; C_L en couleur sur la surface de calcul seulement ; **aucune livrée, aucun logo** |

**Fardage refait** (`fardage.py`, compte rendu, point 6). Le pavois élève la coque vue de côté et de face de 1,0 m :
A_L 332,1 → 375,0 m², A_F 96,1 → 99,4 m² (C, H_C changent un peu ; A_OD et H_BR non). Au vent de la démonstration :
**X_A = −2,14 kN** (contre −2,6 kN en session 16 b : 1,6 % de la poussée des deux mâts, contre 1,9 %) et
**Y_A = 27,5 kN** (contre 23,2 kN). La coque Série 60, vue de côté et de face, a les mêmes aires que la coque de la
session 16 b (elle s'arrête aux perpendiculaires, sans tonture) : seul le pavois change le fardage.
