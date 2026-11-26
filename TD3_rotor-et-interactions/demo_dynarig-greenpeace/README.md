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
