@echo off
setlocal

:: Dossier Python
set PYTHON=C:\Python313\python.exe
set PIP=C:\Python313\python.exe -m pip
set STREAMLIT=C:\Python313\Scripts\streamlit.exe

:: Vérifier si pip est installé
%PYTHON% -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] pip non trouvé. Téléchargement de get-pip.py...
    curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    echo [INFO] Installation de pip...
    %PYTHON% get-pip.py
)

:: Installer les dépendances nécessaires
echo [INFO] Installation des dépendances...
%PIP% install --upgrade pip
%PIP% install streamlit pandas openpyxl matplotlib

:: Lancer l'application
echo [INFO] Lancement de l'application...
%STREAMLIT% run app.py

pause
