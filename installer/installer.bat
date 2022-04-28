@echo off

cd %TEMP%
echo "Installing Aoede"
echo .

goto :DOES_PYTHON_EXIST

:DOES_PYTHON_EXIST
echo .
echo "Checking for Python"
python -V | find /v "Python" >NUL 2>NUL && (goto :PYTHON_DOES_NOT_EXIST)
python -V | find "Python"    >NUL 2>NUL && (goto :PYTHON_DOES_EXIST)
goto :EOF

:PYTHON_DOES_NOT_EXIST
echo .
echo "Python not found."
echo "Install Python or add it to path if already installed to continue..."
goto :EOF

:PYTHON_DOES_EXIST
echo .
echo "Trying to install just_playback"
echo .
rmdir /s /q justplaybackWheels
del wheels.zip
curl -L "https://github.com/nanna7077/just_playback/releases/download/v0.1.6/wheels.zip" --output wheels.zip
powershell Expand-Archive "wheels.zip" -DestinationPath "%TEMP%\justplaybackWheels"
cd justplaybackWheels
for /f %%f in ('dir /b %TEMP%\justplaybackWheels') do (
    echo .
    echo "Trying to install %%f"
    echo .
    python -m pip install %%f && break
)
cd ..
echo .
echo "Downloading Aoede"
echo .
del current.zip
rmdir /s /q aoede-current
curl -L "https://github.com/nanna7077/aoede/archive/refs/heads/current.zip" --output current.zip
powershell Expand-Archive "current.zip" -DestinationPath "%TEMP%\aoede-current"
echo .
echo "Installing Aoede"
echo .
rmdir /s /q %UserProfile%\Documents\aoede
mkdir %UserProfile%\Documents\aoede
xcopy /e /v "%TEMP%\aoede-current\aoede-current\src\" "%UserProfile%\Documents\aoede\"
copy "%TEMP%\aoede-current\installer\uninstaller.bat" "%UserProfile%\Documents\aoede\"
copy "%TEMP%\aoede-current\installer\installer.bat" "%UserProfile%\Documents\aoede\"
cd %UserProfile%\Documents\aoede
rename installer.bat updater.bat
echo .
echo "Installing Requirements"
echo .
python -m pip install -r requirements.txt
echo .
echo "Creating Start Menu Entry"
echo .
%TEMP%\aoede-current\aoede-current\installer\shortcut.bat -linkfile "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\aoede.lnk" -target "pythonw.exe" -linkarguments "%UserProfile%\Documents\aoede\application.py" -description "An easy-to-use and minimalstic music player." -iconlocation "%UserProfile%\Documents\aoede\web\logo.png" -iconstyle 7 -workingdirectory "%UserProfile%\Documents\aoede"
echo "Aoede installed successfully!"
goto :EOF

:EOF
pause