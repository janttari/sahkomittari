<?php
$ip=$_GET["ip"];
echo "<a href='index.php'>[palaa]</a><br>";
echo "Historia asiakkaalle: ".$ip. "<br><br><pre>";
echo "<pre>";
echo "aikaleima;ip;kwh;pulssit;tuntikohtainen;lampo;kosteus;ulkolampo;ulkokosteus;\n";
        $db_kulutus = new SQLite3('/opt/sahkomittari-server/data/kulutus.db');
        $sql = "SELECT * from kulutus WHERE ip='".$ip."' ORDER BY aikaleima";
        $kys_kulutus = $db_kulutus->query($sql);
        while($ret_kulutus = $kys_kulutus->fetchArray(SQLITE3_ASSOC)) {
               echo $ret_kulutus['aikaleima'] . ";" . $ret_kulutus['ip'] . ";" . $ret_kulutus['kwh'] . ";" . $ret_kulutus['pulssit'] . ";" . $ret_kulutus['tuntikohtainen'] . ";" . $ret_kulutus['lampo'] . ";" . $ret_kulutus['kosteus'] . ";" . $ret_kulutus['ulkolampo'] . ";" . $ret_kulutus['ulkokosteus'] . ";<br>" ;
             }
            //$row_kulutus = $ret_kulutus->fetchArray(SQLITE3_ASSOC);
            //echo $row_kulutus;
            //$kwh=$row_kulutus['kwh'];
            //$pulssit=$row_kulutus['pulssit'];
            //$lampo=$row_kulutus['lampo'];
            //$kosteus=$row_kulutus['kosteus'];
            //echo $row['ip'] . ";" . $row['numero'] . ";" . $row['nimi'] . ";" .$kwh . ";<br>";
 //       }
        $db_kulutus->close();


echo "</pre>";
?>
