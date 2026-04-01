@echo off
echo =========================================
echo  Demarrage du systeme global
echo =========================================

echo 1. Activation de l'environnement virtuel...
call env\Scripts\activate.bat

echo 2. Execution du pipeline...
python main.py

echo.
pause
