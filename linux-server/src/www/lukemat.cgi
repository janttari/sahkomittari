#!/bin/bash

echo "Content-type: text/html"
echo ""

echo '<html>'
echo '<head>'
echo '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'
echo '<title>Mittarilukemat</title>'
echo '</head>'
echo '<body>'
echo '<table border="1"><tr><td>IP</td><td>kwh</td><td>kulutus</td><td>pulssit</td><td>päivät</td</tr>'

for filename in /dev/shm/sahkomittari/*; do
    ip=$(basename $filename)
    nimi=$(./ip_to_numeronimiip $ip)
    rivi=$(cat $filename)
    kwh=$(echo $rivi |cut -d ';' -f 1)
    ajankKulutus=$(echo $rivi |cut -d ';' -f 2)
    pulssit=$(echo $rivi |cut -d ';' -f 3)
    paivalinkki="paivat.py?$ip"
    echo "<tr><td>$ip $nimi</td><td>$kwh</td><td>$ajankKulutus</td><td>$pulssit</td><td><a href="$paivalinkki">päivät</td></tr>"
done
echo '</table>'
