<!doctype html>

<html lang="fi">
<head>
  <meta charset="utf-8">

  <title>Raportti</title>
</head>

<body>
    <a href="../">[palaa]</a><br><br>
    <?php
        $vuosi=$_GET["vuosi"];
        $kuukausi=$_GET["kuukausi"];
        date_default_timezone_set('Europe/Helsinki');
        $skkalku = $vuosi."-".$kuukausi."-"."01";
        $ukkalku = mktime(0, 0, 0, $kuukausi, 1, $vuosi ); //kuukauden ensimmäinen ajankohta unix-aikana
        $skkviimpv= date("t", strtotime($skkalku)); //kyseisen kuukauden viimeinen päivä numero
        $ukkloppu = mktime(23, 59, 59, $kuukausi, $skkviimpv, $vuosi); //kuukauden viimeinen ajankohta unix-aikana
        //echo $ukkalku . "-". $ukkloppu;
        $db_asiakkaat = new SQLite3('/opt/sahkomittari-server/data/asiakkaat.db');
        $db_kulutus = new SQLite3('/opt/sahkomittari-server/data/kulutus.db');
        $sql = "SELECT * from asiakkaat";
        $ret_asiakkaat = $db_asiakkaat->query($sql);
        echo "<pre>";
        while($row = $ret_asiakkaat->fetchArray(SQLITE3_ASSOC) ) {
            //Kysellään kuukauden ensimmäinen kulutuslukema, koska siinä on edellisen kuukauden loppulukema
            $sql = "SELECT * from kulutus WHERE IP='".$row['ip']."' AND aikaleima BETWEEN ".$ukkalku." AND ".$ukkloppu." ORDER BY aikaleima LIMIT 1";
            $ret_kulutus = $db_kulutus->query($sql);
            $row_kulutus = $ret_kulutus->fetchArray(SQLITE3_ASSOC);
            $kwh=$row_kulutus['kwh'];
            $pulssit=$row_kulutus['pulssit'];
            $lampo=$row_kulutus['lampo'];
            $kosteus=$row_kulutus['kosteus'];
            echo $row['ip'] . ";" . $row['numero'] . ";" . $row['nimi'] . ";" .$kwh . ";<br>";
        }
        echo "</pre>";
        $db_asiakkaat->close();
        $db_kulutus->close();

    ?>
</body>
</html>
