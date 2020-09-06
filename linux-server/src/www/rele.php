<!DOCTYPE html> <head> <style>.korostus {background-color: Coral;} .alive {background-color: Gainsboro;} </style> <script type="text/javascript" 
src="js/jquery-3.5.1.min.js"></script> </head> <script>

//var socketUrl = 'ws://'+location.hostname+(location.port ? ':'+location.port: '')+'/p7777'; //    ws://domain:portti/p7777
//var socketUrl = 'ws://localhost:8889';
var socketUrl = 'ws://'+location.hostname+":8889";

var ws = new  WebSocket(socketUrl);

function lahetatavu(){ //lähetetään tavu releelle
    let ip=document.getElementById("ip").value;
    let tavu=document.getElementById("tavu").value;
    let etakomento='{"komento": {"laite": "'+ip+'", "tavu": "'+tavu+'"}}';
    console.log("Lähettää: "+etakomento);
    ws.send(etakomento);

}

function ruudulle(kentta, sanoma) { //tulosta kenttä:arvo
    document.getElementById(kentta).innerHTML = sanoma + '\n';
}

ws.onopen = function() {
    ruudulle("yhteys","<font color='green'>YHDISTETTY");
};

ws.onclose = function() {
    ruudulle("yhteys","<font color='red'>KATKAISTU</font>");
    setTimeout(function () {
		console.log("reconn");
        location.reload();
    }, 5000);
};

ws.onmessage = function(event) {
	aika=new Date().toLocaleTimeString('en-US', { hour12: false, hour: "numeric", minute: "numeric", second: "numeric"});
    ruudulle("yhteys","<font color='green'>"+aika+"</font>");

    var json = JSON.parse(event.data);
        for (it in json.elementit){
            console.log(json.elementit[it]);
            if (document.getElementById(json.elementit[it].elementti)){
                document.getElementById(json.elementit[it].elementti).innerHTML = json.elementit[it].arvo;
                elem=document.getElementById(json.elementit[it].elementti);
                if (!( event.data.includes("alive"))){
                    vari='korostus';
                }
                else{
                    vari='alive';
                }
                    $(elem).addClass(vari).delay(1000).queue(function(next){
                    $(this).removeClass(vari);
                    next();
                    });
            }
            else{
                console.log("elementtiä "+json.elementit[it].elementti+" ei ole!");    
            }
        }
}
</script>
<!--
<a href="asiakashallinta/">[Asiakashallinta]</a> 
<a href="kuukausiraportit/">[Kuukausiraportit]</a>
-->
<br><br>
<form>
    ip:<input type="text" id="ip"><br>
    tavu:<input type="text" id="tavu"><br>
   <input type="button" value="Lähetä" onclick="lahetatavu()">
</form>
<br>
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
<table border=1><tr><td width="300">nähty</td><td width="100">ip</td><td width="100">numero</td><td width="100">nimi</td><td width="100">kwh</td><td width="100">reaaliaik</td><td width="100">pulssit</td><td width="100">info</td><td width="100">lampo</td><td width="100">kosteus</td><td width="100">historia</td></tr>
<?php 
    $db_asiakkaat = new SQLite3('/opt/sahkomittari-server/data/asiakkaat.db');
    $db_kulutus = new SQLite3('/opt/sahkomittari-server/data/kulutus.db');
    $sql = "SELECT * from asiakkaat";
    $ret_asiakkaat = $db_asiakkaat->query($sql);
    while($row = $ret_asiakkaat->fetchArray(SQLITE3_ASSOC) ) {
        $sql = "SELECT * from kulutus WHERE IP='".$row['ip']."' ORDER BY aikaleima DESC LIMIT 1";
        $ret_kulutus = $db_kulutus->query($sql);
        $row_kulutus = $ret_kulutus->fetchArray(SQLITE3_ASSOC);
        $kwh=$row_kulutus['kwh'];
        $pulssit=$row_kulutus['pulssit'];
        $lampo=$row_kulutus['lampo'];
        $kosteus=$row_kulutus['kosteus'];
        echo "<tr><td id=nahty_".$row['ip'].">---</td></td---><td>". $row['ip'] . "</td><td>". $row['numero'] ."</td><td>". $row['nimi'] ."</td><td id=kwh_".$row['ip'].">".$kwh."</td><td id=reaali_".$row['ip'].">---</td><td id=pulssit_".$row['ip'].">".$pulssit."</td></td><td id=info_".$row['ip'].">REC</td><td id=lampo_".$row['ip'].">...</td><td id=kosteus_".$row['ip'].">...</td><td><a href=\"historia.php?ip=".$row['ip']."\">historia</a></td></tr><br>";
    }
   
    $db_asiakkaat->close();
    $db_kulutus->close();
?>

</table>
</body>
</html>
