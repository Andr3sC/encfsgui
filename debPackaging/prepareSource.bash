OLDPWD=$PWD
cd $(dirname $(readlink -f $0))
rm -r source
mkdir source
rm -r target
mkdir target
mkdir -p source/usr/share/encfsgui/conf
mkdir -p source/usr/share/encfsgui/widgetHandlers
cp ../encfsgui.py source/usr/share/encfsgui/
cp ../widgetHandlers/* source/usr/share/encfsgui/widgetHandlers
chmod 755 source/usr/share/encfsgui/encfsgui.py
cp -r ../conf/*  source/usr/share/encfsgui/conf
find source -type f -name "*~" -exec rm {} \;
find source -type f -name "*po" -execdir msgfmt {} \;
find source -type f -name "*po" -exec rm {} \;
mkdir -p source/usr/bin
echo '/usr/share/encfsgui/encfsgui.py $@' > source/usr/bin/encfsgui
chmod 755 source/usr/bin/encfsgui
echo $PWD
find . -type f -print
cd $OLDPWD
echo "done"

