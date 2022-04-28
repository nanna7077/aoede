#! /bin/bash

echo "Installing Aoede"
echo ""
cd /tmp
echo "Installing just_playback"
echo ""
rm -rf justplaybackWheels
rm wheels.zip
wget https://github.com/nanna7077/just_playback/releases/download/v0.1.6/wheels.zip
unzip wheels -d justplaybackWheels
cd justplaybackWheels
for f in *; do
    echo ""
    echo ""
    echo "Trying to install $f"
    echo ""
    echo ""
    pip install $f && break
done
echo ""
echo "Downloading Aoede"
echo ""
cd /tmp
rm -rf aoede-current
rm current.zip
wget https://github.com/nanna7077/aoede/archive/refs/heads/current.zip
unzip current.zip
cd aoede-current/src
echo ""
echo "Installing Aoede"
echo ""
mkdir /opt
rm -rf /opt/aoede
mkdir /opt/aoede
cp -r * /opt/aoede/
cp /tmp/aoede-current/installer/uninstaller.sh /opt/aoede
cp /tmp/aoede-current/installer/installer.sh /opt/aoede
mv /opt/aoede/installer.sh /opt/aoede/updater.sh
cd /opt/aoede
echo ""
echo "Installing requirements"
echo ""
pip install -r requirements.txt
echo ""
echo "Adding Desktop files"
echo ""
rm /usr/share/applications/aoede.desktop
cat > /usr/share/applications/aoede.desktop << EOL
[Desktop Entry]
Name=Aoede
Comment=Aoede is an easy-to-use and minimalstic music player.
GenericName=Music Player
Exec=python /opt/aoede/application.py
Icon=/opt/aoede/web/logo.png
Type=Application
Categories=Music;Playback;
Path=/opt/aoede
EOL