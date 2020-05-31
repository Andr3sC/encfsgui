OLDPWD=$PWD
cd $(dirname $(readlink -f $0))
rm -r source
mkdir source
rm -r target
mkdir target
mkdir -p source/usr/share/encfgui
mkdir -p source/usr/share/encfsgui/conf
cp ../encfsgui.py source/usr/share/encfsgui/
chmod 755 source/usr/share/encfsgui/encfsgui.py
cp -r ../conf/*  source/usr/share/encfsgui/conf
find source -type f -name "*~" -exec rm {} \;
find source -type f -name "*po" -execdir msgfmt {} \;
find source -type f -name "*po" -exec rm {} \;
echo $PWD
find . -type f -print
cd $OLDPWD
echo "done"

