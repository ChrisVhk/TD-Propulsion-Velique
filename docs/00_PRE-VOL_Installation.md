# Pré-vol — installer son environnement AVANT le TD 1

> **Public : élèves de S7.** Vous n'avez pas suivi le cours d'informatique appliquée de S5, qui installe le même
> environnement : ce pré-vol vous y renvoie et vous dit quoi lancer. Comptez 30 à 60 min selon le réseau et l'état
> du poste. **Pendant le TD 1**, l'installation se fait de 0:00 à 0:40, pendant que le binôme avance les premiers
> exercices à la main. En cas de blocage : [`00b_CA_NA_PAS_MARCHE.md`](00b_CA_NA_PAS_MARCHE.md).

On installe **quatre choses**, dans cet ordre. Tout le TD se fait dans le **terminal Ubuntu** (WSL), jamais dans
PowerShell, sauf l'étape ①.

## ① L'environnement : WSL + Ubuntu (par le dépôt du cours S5)

WSL est un Linux (Ubuntu) qui tourne à l'intérieur de Windows. Il s'installe par le script du cours d'informatique
appliquée S5, dans son dépôt public :

- dépôt : <https://github.com/ChrisVhk/Informatique-Appliquee-S5> ;
- guide pas à pas : `docs/00_PRE-VOL_Installation.md` de ce dépôt ;
- script : `scripts/installer_poste.ps1` de ce dépôt.

**Ce que vous lancez.** Téléchargez `installer_poste.ps1` depuis ce dépôt, puis, dans **PowerShell** (si possible en
administrateur la première fois), dans le dossier du fichier :

```powershell
powershell -ExecutionPolicy Bypass -File installer_poste.ps1
```

**Ce qu'il fait.** Il installe WSL et Ubuntu, VS Code et son extension WSL, Python avec numpy, matplotlib et pandas,
clone le dépôt du cours S5 (sans gêne pour ce TD) et lance sa vérification. Il se relance sans risque. **Après
l'installation de WSL, un redémarrage est obligatoire** : le script s'arrête avec une consigne claire ; relancez
exactement la même commande après le redémarrage.

Ubuntu est déjà installé sur votre poste ? Passez à l'étape ②.

## ② Le dépôt du TD

Dans le **terminal Ubuntu** :

```bash
cd ~
git clone https://github.com/ChrisVhk/TD-Propulsion-Velique.git
cd TD-Propulsion-Velique
```

## ③ CN-AeroModels et les modules Python du TD

```bash
bash scripts/installer_cnaero.sh
source ~/.bashrc
```

Le script télécharge le binaire **Linux** v0.5.1 de CN-AeroModels sur la page *Releases* officielle du LHEEA
(<https://gitlab.com/lheea/CN-AeroModels/-/releases>), le décompresse dans `~/outils/CN-AeroModels`, ajoute son
dossier au `PATH` (dans `~/.bashrc`) et installe les modules Python `yaml` et `matplotlib` (mot de passe Ubuntu
demandé). Il se relance sans risque.

## ④ VÉRIFIER — la seule chose à renvoyer

Depuis le dossier du dépôt (`~/TD-Propulsion-Velique`) :

```bash
python3 scripts/verifie_mon_install.py
```

Le script vérifie Python, WSL, les modules, trouve CN-AeroModels, le lance sur l'aile elliptique
(`cas/exemples/2- nonlinear lifting line/elliptic.yml`) et compare le résultat à la valeur de référence, C_L = 0,3655 (sortie de l'outil v0.5.1 pour cette aile, accord avec la
théorie de Prandtl).
Il affiche un bilan en clair (`[ OK ]` / `[ MANQUE ]` / `[ NOTE ]`) puis un **bloc encadré** à copier et à renvoyer à
l'enseignant.

- Que des `[ OK ]` → rien d'autre à faire.
- Un `[ MANQUE ]` → [`00b_CA_NA_PAS_MARCHE.md`](00b_CA_NA_PAS_MARCHE.md), puis renvoyez quand même le bloc.

## En binôme : une machine qui marche suffit

Si l'un des deux postes fonctionne, le binôme travaille dessus et l'autre répare à côté. Les exercices se font de
toute façon à la main ; l'outil sert à vérifier et à aller plus loin.
