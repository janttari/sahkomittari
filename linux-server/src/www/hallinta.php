<!DOCTYPE html> <head> </head>

<body>
hallinta<br>
<table>
	<tr>
		<td>
            <div id="muu">Viim data: </div>
        </td>
		<td>
            <div id="yhteys"><font size="-5" color="brown">ei_tiedossa</font>
        </td>
    </tr>
</table>
<br>

<table border=1><tr><td width=100>ip</td><td width="100">numero</td><td width="100">nimi</td><td width="100">kwh</td></tr>

<?php 
    class MyDB extends SQLite3 {
        function __construct() {
            $this->open('/opt/sahkomittari-server/raspisahkomittari.db');
        }
    }
    $db = new MyDB();
    $sql =<<<EOF
    SELECT * from asiakkaat;
    EOF;

    $ret = $db->query($sql);
    while($row = $ret->fetchArray(SQLITE3_ASSOC) ) {
        echo $row;
        //echo "<tr><td id=nahty_".$row['ip'].">---</td</td---><td>". $row['ip'] . "</td><td>". $row['numero'] ."</td><td>". $row['nimi'] ."</td><td id=kwh_".$row['ip'].">---</td><td id=pulssit_".$row['ip'].">---</td></tr><br>";
    }
   
    $db->close();
?>

</table>
</body>
</html>
