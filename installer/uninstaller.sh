#! /bin/bash

echo "Uninstalling Aoede"
echo ""
pip uninstall -y -r /opt/aoede/requirements.txt
rm -rf /opt/aoede
rm /usr/share/applications/aoede.desktop
echo ""
echo "Successfully uninstalled Aoede"