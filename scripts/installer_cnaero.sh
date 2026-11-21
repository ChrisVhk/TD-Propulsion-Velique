#!/usr/bin/env bash
# installer_cnaero.sh — TD Propulsion vélique (EGN-S7, ENSM)
# ---------------------------------------------------------------------------
# Installe, DANS UBUNTU (WSL), ce qu'il faut pour le TD en plus de l'environnement
# du cours d'informatique appliquée S5 :
#   1. CN-AeroModels v0.5.1, binaire officiel Linux (linux-x64) du LHEEA, téléchargé
#      depuis la page Releases du dépôt de l'outil (aucune compilation) ;
#   2. le dossier du binaire ajouté au PATH (dans ~/.bashrc) ;
#   3. Python : les modules yaml et matplotlib (paquets Ubuntu).
#
# Usage, depuis le dossier du dépôt, dans le terminal Ubuntu :
#     bash scripts/installer_cnaero.sh
# puis fermer et rouvrir le terminal (ou : source ~/.bashrc), puis :
#     python3 scripts/verifie_mon_install.py
#
# Le script se relance sans risque : chaque étape vérifie d'abord si elle est déjà faite.
# Le mot de passe demandé à l'étape 3 est celui de votre compte Ubuntu (sudo).
set -euo pipefail

VERSION="v0.5.1"
ARCHIVE="CN-AeroModels-linux-x64-${VERSION}.tar.gz"
# Adresse de téléchargement de l'archive de la page Releases (API GitLab du dépôt lheea/CN-AeroModels),
# relevée dans la passation de Cowork du 01/11/2026 ; à revérifier sur la page Releases si elle change.
URL="https://gitlab.com/api/v4/projects/54731355/packages/generic/cn-aeromodels/${VERSION}/${ARCHIVE}"
PAGE="https://gitlab.com/lheea/CN-AeroModels/-/releases"
DEST="${HOME}/outils/CN-AeroModels"
BIN="${DEST}/bin/CN-AeroModels"

etape() { printf '\n==> %s\n' "$1"; }
ok()    { printf '  [ OK ] %s\n' "$1"; }
note()  { printf '  [ NOTE ] %s\n' "$1"; }

case "$(uname -s)" in
  Linux) ;;
  *) echo "Ce script se lance dans le terminal Ubuntu (WSL), pas dans PowerShell." >&2; exit 1 ;;
esac

# 1. Binaire ------------------------------------------------------------------
etape "CN-AeroModels ${VERSION} (binaire Linux du LHEEA)"
if [ -x "${BIN}" ]; then
  ok "déjà installé : ${BIN}"
else
  mkdir -p "${DEST}"
  tmp="$(mktemp -d)"
  echo "  téléchargement depuis la page Releases officielle (${PAGE}) ..."
  if command -v curl >/dev/null 2>&1; then
    curl -fL --retry 2 -o "${tmp}/${ARCHIVE}" "${URL}"
  else
    wget -O "${tmp}/${ARCHIVE}" "${URL}"
  fi
  echo "  empreinte SHA-256 de l'archive (à noter si on vous la demande) :"
  sha256sum "${tmp}/${ARCHIVE}" | sed 's/^/    /'
  tar xzf "${tmp}/${ARCHIVE}" -C "${DEST}"
  rm -rf "${tmp}"
  if [ -x "${BIN}" ]; then ok "installé : ${BIN}"; else
    echo "  [ MANQUE ] ${BIN} absent après décompression : voir docs/00b_CA_NA_PAS_MARCHE.md" >&2; exit 1; fi
fi

# 2. PATH -------------------------------------------------------------------
etape "PATH"
LIGNE='export PATH="$HOME/outils/CN-AeroModels/bin:$PATH"'
if grep -qxF "${LIGNE}" "${HOME}/.bashrc" 2>/dev/null; then
  ok "déjà dans ~/.bashrc"
else
  printf '\n# CN-AeroModels (TD Propulsion vélique, EGN-S7)\n%s\n' "${LIGNE}" >> "${HOME}/.bashrc"
  ok "ajouté à ~/.bashrc (fermez et rouvrez le terminal, ou : source ~/.bashrc)"
fi

# 3. Python -----------------------------------------------------------------
etape "Python : yaml et matplotlib"
if python3 -c "import yaml, matplotlib" 2>/dev/null; then
  ok "yaml et matplotlib déjà présents"
else
  note "installation des paquets python3-yaml et python3-matplotlib (mot de passe Ubuntu demandé)"
  sudo apt-get update -qq
  sudo apt-get install -y python3-yaml python3-matplotlib
  python3 -c "import yaml, matplotlib" && ok "yaml et matplotlib installés"
fi

etape "Fini"
echo "  Rouvrez le terminal, revenez dans le dossier du dépôt, puis lancez :"
echo "    python3 scripts/verifie_mon_install.py"
