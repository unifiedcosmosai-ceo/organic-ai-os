#!/bin/bash
# Push zu GitHub - Anleitung

# 1. Erstelle leeres Repo auf GitHub: https://github.com/new
#    Name: organic-ai-os (oder dein Wunschname)
#    NICHT mit README initialisieren

# 2. Dann hier ausführen (ersetze USERNAME):

read -p "GitHub Username: " USERNAME
read -p "Repo Name [organic-ai-os]: " REPO
REPO=${REPO:-organic-ai-os}

echo "Verbinde mit https://github.com/$USERNAME/$REPO.git"

git remote remove origin 2>/dev/null
git remote add origin https://github.com/$USERNAME/$REPO.git
git branch -M main
git push -u origin main

echo ""
echo "✅ Gepusht! Repo: https://github.com/$USERNAME/$REPO"

# Für SSH (falls du SSH Key hast):
# git remote add origin git@github.com:$USERNAME/$REPO.git
