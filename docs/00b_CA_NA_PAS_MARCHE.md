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
| `Error opening file …` | pas dans le dossier du cas, ou nom avec espaces sans guillemets | `cd` dans le dossier du cas ; `cd "cas/exemples/1- 2D model"`, `CN-AeroModels "mon cas.yml"` |
| efforts nuls (0), ou qui changent beaucoup avec le nombre d'éléments | calcul en ligne portante non convergé (près du décrochage, ou trop d'éléments, souvent dès 30) | revenir à 10-20 éléments ; comparer 10 et 20 : s'ils diffèrent de plus de 1 %, ne pas retenir le point |
| `[ MANQUE ] aile elliptique : C_L = …` différent de 0,3655 | autre version de l'outil, ou fichier modifié | vérifier la version (v0.5.1) ; refaire `git checkout -- cas/` pour retrouver les fichiers d'origine |
| `ModuleNotFoundError: No module named 'yaml'` | module Python absent | `sudo apt install python3-yaml python3-matplotlib` |
| un résultat de l'outil vous semble faux, ou vous ne savez pas si l'outil marche | à établir | lancez `python3 scripts/test_valeurs_connues.py` depuis le dossier du dépôt et collez **toute** sa sortie dans votre message à l'enseignant |

## Pannes propres à ParaView (TD 1, manipulation 2 bis)

| Symptôme | Cause | Remède |
|---|---|---|
| ParaView pour Windows ne trouve pas les fichiers du TD (ni `C:\` ni « Documents ») | les fichiers sont dans WSL, que Windows voit par une adresse réseau | dans le terminal Ubuntu, depuis le dossier du cas : `wslpath -w .` ; coller l'adresse affichée (`\\wsl.localhost\Ubuntu\home\<nom>\…`, ou `\\wsl$\Ubuntu\home\<nom>\…`) dans le champ du nom de fichier |
| après *File > Load State*, seuls le titre, la barre de couleur et le repère x, y, z s'affichent (ni aile, ni mer, ni flèches), ou `Could not open file` dans *Output Messages* | ParaView cherche les données à un mauvais endroit, ou les `.vtk` n'ont pas été écrits | vérifier que `ls *.vtk` montre quatre fichiers dans le dossier du cas (sinon relancer `CN-AeroModels aile_caboteur.yml --vtk 1`) ; recharger l'état `aile_caboteur.pvsm` (dans le dossier du cas, à côté des `.vtk`) avec *Search files under specified directory* et le *Data Directory* **proposé** (il finit par `Cas-ENSM_aile-du-caboteur`), pas *Use File Names From State* |
| la vue s'est perdue (aile hors de l'écran, minuscule, ou la tête en bas) | rotation ou zoom à la souris, ou bouton ±X / ±Y | bouton *Reset Camera* pour recadrer ; *Set view direction to +Z* pour la vue de dessus ; pour la vue de départ, recharger l'état |
| `pvpython scripts/voir_aile_caboteur.py` : aucune fenêtre, ou erreur d'affichage (*display*, *Qt*) | affichage graphique de WSL absent (Windows 10 ancien, ou WSL non à jour) | dans PowerShell : `wsl --update`, puis rouvrir Ubuntu ; sinon ParaView pour Windows (pré-vol, étape ⑤) |

Chaque lancement **écrase** `results.csv` du dossier courant : le renommer avant de relancer s'il faut le garder.
Ne modifiez pas les fichiers de `cas/` : copiez-les d'abord (`cp aile_caboteur.yml essai.yml`) et travaillez sur la copie.
