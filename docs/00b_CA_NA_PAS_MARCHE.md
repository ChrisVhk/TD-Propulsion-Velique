# « Ça n'a pas marché »

## WSL, Ubuntu, droits, Windows trop ancien

Ce sont les pannes de l'étape ① du pré-vol : elles sont décrites, avec leurs remèdes, dans le dépannage du cours S5,
`docs/00b_CA_NA_PAS_MARCHE.md` du dépôt <https://github.com/ChrisVhk/Informatique-Appliquee-S5> (virtualisation
désactivée dans le BIOS, pas de droits administrateur, Windows trop ancien, `[ MANQUE ]` de la vérification S5).

## Pannes propres à CN-AeroModels

| Symptôme | Cause | Remède |
|---|---|---|
| `CN-AeroModels: command not found` juste après l'installation | le terminal n'a pas relu `~/.bashrc` | `source ~/.bashrc`, ou fermer et rouvrir le terminal Ubuntu |
| `installer_cnaero.sh` s'arrête au téléchargement | pas de réseau, ou page Releases indisponible | vérifier la connexion (`ping gitlab.com`), relancer ; sinon le signaler à l'enseignant |
| le script dit « Ce script se lance dans le terminal Ubuntu » | lancé depuis PowerShell | ouvrir le terminal **Ubuntu** et relancer |
| `terminate called … unrecognised option '--help'` | l'outil n'a pas d'option `--help` (ni `-h`) | la seule commande est `CN-AeroModels <fichier.yml>` |
| `Please specify an input file` | aucun fichier donné | ajouter le nom du `.yml` (c'est aussi la réponse normale de l'outil lancé seul) |
| `Error opening file …` | pas dans le dossier de la manipulation, ou nom avec espaces sans guillemets | `cd` dans le dossier de la manipulation (tableau 1 de la fiche) ; `bash lancer.sh "mon cas.yml"` |
| `Problem in input data of a lifting line model. Some data may be missing (e.g the file of aerodynamic coefficients).` | l'outil a été lancé directement (`CN-AeroModels aile-caboteur.yml`) dans le dossier de la manipulation, ou le `.yml` lit la table à l'ancien chemin | lancez par `bash lancer.sh FICHIER.yml` : l'outil tourne dans `sorties/`, d'où le chemin de la table se lit ; `lancer.sh` signale un ancien chemin et donne la commande qui le corrige |
| efforts nuls (0), ou qui changent beaucoup avec le nombre d'éléments | calcul en ligne portante non convergé (près du décrochage, ou trop d'éléments, souvent dès 30) | revenir à 10-20 éléments ; comparer 10 et 20 : s'ils diffèrent de plus de 1 %, ne pas retenir le point |
| `[ MANQUE ] aile elliptique : C_L = …` différent de 0,3655 | autre version de l'outil, ou fichier modifié | vérifier la version (v0.5.1) ; refaire `git checkout -- communs/` pour retrouver les fichiers d'origine |
| `ModuleNotFoundError: No module named 'yaml'` | module Python absent | `sudo apt install python3-yaml python3-matplotlib` |
| un résultat de l'outil vous semble faux, ou vous ne savez pas si l'outil marche | à établir | lancez `python3 scripts/test_valeurs_connues.py` depuis le dossier du dépôt et collez **toute** sa sortie dans votre message à l'enseignant |

## Pannes propres à ParaView

| Symptôme | Cause | Remède |
|---|---|---|
| ParaView pour Windows ne trouve pas les fichiers du TD (ni `C:\` ni « Documents ») | les fichiers sont dans WSL, que Windows voit par une adresse réseau | dans le terminal Ubuntu, depuis le dossier de la manipulation : `wslpath -w .` ; coller l'adresse affichée (`\\wsl.localhost\Ubuntu\home\<nom>\…`, ou `\\wsl$\Ubuntu\home\<nom>\…`) dans le champ du nom de fichier |
| après *File > Load State*, seuls le titre, la barre de couleur et le repère x, y, z s'affichent (ni aile, ni mer, ni navire, ni flèches), ou `Could not open file` dans *Output Messages* | ParaView cherche les données à un mauvais endroit, ou les `.vtk` n'ont pas été écrits | TD 1 : vérifier que `ls sorties/*.vtk` montre cinq fichiers dans `TD1_aerodynamique/manip2-et-3_aile-caboteur/` (les quatre de l'outil et la coque `caboteur-serie60.vtk`) (sinon relancer `bash lancer.sh aile-caboteur.yml --vtk 1`) ; recharger l'état `vue.pvsm` (dossier de la manipulation ; les `.vtk` sont dans `sorties/`) avec *Search files under specified directory* et le *Data Directory* **proposé** (il finit par `manip2-et-3_aile-caboteur`), pas *Use File Names From State* |
| `Cannot find …caboteur-serie60.vtk` (ou un autre `.vtk`) au chargement de l'état | chemin **retapé** au clavier : une majuscule ou une lettre change (`Aile-caboteur` au lieu de `aile-caboteur`), et Linux distingue les deux (cas réel du 23/11) | ne retapez jamais le chemin : dans le terminal Ubuntu, depuis le dossier de la manipulation, `wslpath -w .`, copiez l'adresse affichée (**Ctrl+Maj+C**) et collez-la ; recharger l'état avec le *Data Directory* = dossier de la manipulation (TD 1 : il finit par `manip2-et-3_aile-caboteur`) |
| TD 2 : `bash lancer.sh` (sans fichier, manipulation 4) répond « Absent : nll.yml » (ou `pont.yml`) | les fichiers du pied libre et du pont n'ont pas encore été faits, ou sont restés dans l'ancien `cas/aile-caboteur/` | faire d'abord les manipulations du pied libre (`nll.yml`) et du pont (`pont.yml`), dans `TD2_bandes-et-ligne-portante/manip1-a-5_aile-caboteur/` (ou les y ramener : ligne « mise à jour du 26/11 » plus bas), puis relancer `bash lancer.sh` dans ce dossier |
| la vue s'est perdue (aile hors de l'écran, minuscule, ou la tête en bas) | rotation ou zoom à la souris, ou bouton ±X / ±Y | bouton *Reset Camera* pour recadrer ; *Set view direction to +Z* pour la vue de dessus ; pour la vue de départ, recharger l'état |
| `pvpython voir_sans-paraview.py` : aucune fenêtre, ou erreur d'affichage (*display*, *Qt*) | affichage graphique de WSL absent (Windows 10 ancien, ou WSL non à jour) | dans PowerShell : `wsl --update`, puis rouvrir Ubuntu ; sinon ParaView pour Windows (pré-vol, étape ⑤) |

## Après la mise à jour du dépôt (`git pull`)

| Symptôme | Cause | Remède |
|---|---|---|
| TD 1 et 2 : après `git pull` (mise à jour du 26/11), les anciens dossiers `cas/aile-caboteur/` et `cas/exemples/` restent chez vous, avec vos sorties (et parfois `cas/Cas-ENSM_aile-du-caboteur/`, `cas/trois-ailes/`) | les TD 1 et 2 ont été rangés par manipulation dans `TD1_aerodynamique/` et `TD2_bandes-et-ligne-portante/`, les exemples du LHEEA dans `communs/exemples-LHEEA/` ; `git pull` ne déplace pas les fichiers que vous avez produits | gardez d'abord vos `nll.yml` et `pont.yml` du TD 2 (séance 2) : depuis le dossier du dépôt, `mv cas/aile-caboteur/nll.yml cas/aile-caboteur/pont.yml TD2_bandes-et-ligne-portante/manip1-a-5_aile-caboteur/`, puis, dans ce dossier, `sed -i 's#\.\./exemples/airfoil_data/#../../../communs/exemples-LHEEA/airfoil_data/#' nll.yml pont.yml` (nouveau chemin de la table ; `lancer.sh` vous le rappelle) ; ensuite, le reste de `cas/` ne contient que vos anciennes sorties : **supprimez `cas/`** (`rm -r cas`, depuis le dossier du dépôt) |
| TD 3 : après `git pull`, l'ancien dossier `cas/trois-ailes/` reste chez vous (avec `bandes.yml` et des fichiers `1_bandes_*`, `2_nll_*`) | le TD 3 a été rangé par manipulation dans `TD3_rotor-et-interactions/` ; `git pull` ne déplace pas les fichiers que vous avez produits | ce dossier ne contient que vos anciennes sorties : supprimez-le (`rm -r cas/trois-ailes`, depuis le dossier du dépôt ; ou tout `cas/`, ligne ci-dessus) et travaillez dans `TD3_rotor-et-interactions/` |
| après `git pull` (mise à jour du 26/11, noms des dossiers), d'anciens dossiers `manip2-3_…`, `manip1-5_…` ou `manip4-6_…` restent chez vous, vides ou avec seulement `sorties/` | les dossiers qui couvrent plusieurs manipulations s'écrivent maintenant `manip2-et-3_…` (deux manipulations) ou `manip4-a-6_…` (une suite) ; `git pull` déplace les fichiers du dépôt, pas ceux que vous avez produits | si vous y aviez fait une copie (`nll.yml`, `pont.yml`, `bandes.yml`, `sans-plaques.yml`…), déplacez-la d'abord dans le dossier au nouveau nom (`mv`) ; puis supprimez l'ancien dossier (`rm -r`, depuis le dossier du TD) |
| `git pull` refuse : « Your local changes to the following files would be overwritten » | vous avez modifié un fichier du dépôt (souvent le `.yml` du cas) | `git stash`, puis `git pull` ; vos modifications sont mises de côté (`git stash show -p` pour les revoir) |

## « Je suis sur Mac »

Le TD repose sur WSL (Ubuntu sous Windows), qui n'existe pas sous macOS, et CN-AeroModels n'a **pas de binaire macOS** : la page Releases du dépôt de l'outil ne fournit que `linux-x64` et `windows-x64`.

- **Pour l'outil** : travaillez sur le poste Windows de votre binôme (c'est la voie prévue pour la séance).
- **Python et ParaView fonctionnent sous macOS** : `pip3 install pyyaml matplotlib` pour les scripts et les tracés ; ParaView pour macOS depuis <https://www.paraview.org/download/>. Vous pouvez donc ouvrir sur votre Mac les fichiers produits par l'outil sur un autre poste.
- *Piste non testée par l'enseignant* : une machine virtuelle Linux sous UTM (avec Rosetta sur Mac à puce Apple) et VS Code Remote-SSH. Elle n'est pas prise en charge pendant la séance.

Chaque lancement **écrase** `sorties/results.csv` du dossier de la manipulation : le renommer avant de relancer s'il faut le garder.
Ne modifiez pas les fichiers fournis (dossiers des manipulations, `communs/`) : copiez-les d'abord (`cp aile-caboteur.yml essai.yml`) et travaillez sur la copie.
