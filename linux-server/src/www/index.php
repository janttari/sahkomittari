<!DOCTYPE html> <head> <style>.red {background-color: coral;}</style> <script type="text/javascript" 
src="js/jquery-3.5.1.min.js"></script> </head> <script>

//var socketUrl = 'ws://'+location.hostname+(location.port ? ':'+location.port: '')+'/p7777'; //    ws://domain:portti/p7777
//var socketUrl = 'ws://localhost:8889';
var socketUrl = 'ws://'+location.hostname+":8889";

var ws = new  WebSocket(socketUrl);

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
                $(elem).addClass('red').delay(1000).queue(function(next){
                $(this).removeClass('red');
                next();
                });
                
            }
            else{
                console.log("elementtiä "+json.elementit[it].elementti+" ei ole!");    
            }
        }
}
</script>
<a href="hallinta.php">hallinta</a><br>
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

<table border=1><tr><td width="300">nähty</td><td width=100>ip</td><td width="100">numero</td><td width="100">nimi</td><td width="100">kwh</td><td width="100">pulssit</td></tr>
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
        echo "<tr><td id=nahty_".$row['ip'].">---</td</td---><td>". $row['ip'] . "</td><td>". $row['numero'] ."</td><td>". $row['nimi'] ."</td><td id=kwh_".$row['ip'].">---</td><td id=pulssit_".$row['ip'].">---</td></tr><br>";
    }
   
    $db->close();
?>

</table>
</body>
</html>
