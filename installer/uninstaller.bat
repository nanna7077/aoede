@echo off

echo "Uninstalling Aoede"
echo .
rmdir /s /q %UserProfile%\Docuemnts\aoede
del C:\ProgramData\Microsoft\Windows\Start Menu\Programs\aoede.lnk
echo .
echo "Successfully uninstalled Aoede"