<!DOCTYPE html>
<head>
<link rel="stylesheet" type="text/css" href="style.css?ver=1a">
</head>
<script src="js/reconnecting-websocket.js"></script>
<script>

//var socketUrl = 'ws://'+location.hostname+(location.port ? ':'+location.port: '')+'/p7777'; //    ws://domain:portti/p7777
var socketUrl = 'ws://localhost:8888';
var ws = new  ReconnectingWebSocket(socketUrl);


function ruudulle(kentta, sanoma) { //tulosta kenttä:arvo
    document.getElementById(kentta).innerHTML = sanoma + '\n';
}




ws.onopen = function() {
    socketOK=true;
    ruudulle("yhteys","<font color='green'>YHDISTETTY");
};



ws.onclose = function() {
    socketOK
    ruudulle("yhteys","<font color='red'>KATKAISTU</font>");
    setTimeout(function () {
		console.log("reconn");
        reconn();
    }, 2000);
    
};

ws.onmessage = function(event) {
    var json = JSON.parse(event.data);
        for (it in json.elementit){
            console.log(json.elementit[it]);
            if (document.getElementById(json.elementit[it].elementti)){
                document.getElementById(json.elementit[it].elementti).innerHTML = json.elementit[it].arvo;
            }
            else{
                console.log("elementtiä "+json.elementit[it].elementti+" ei ole!");    
            }
        }
};

</script>
<table><tr><td>
<div id="yhteys"><font size="-5" color="brown">ei_tiedossa</font>
</td><td>
<div id="muu">asdfas</div>
</td></tr></table>
<br>

<table border=1><tr><td width="100">nähty</td><td width=100>ip</td><td width="100">numero</td><td width="100">nimi</td><td width="100">kwh</td></tr>
<?php
   class MyDB extends SQLite3 {
      function __construct() {
         $this->open('/yandex/työnalla/sahkomittari/linux-server/src/opt/sahkomittari-server/raspisahkomittari.db');
      }
   }
   
   $db = new MyDB();



//SELECT * from ASIAKKAAT WHERE nimi="Raspi";

   $sql =<<<EOF
     SELECT * from asiakkaat;

EOF;

   $ret = $db->query($sql);
   while($row = $ret->fetchArray(SQLITE3_ASSOC) ) {
      echo "<tr><td id=".$row['ip']."_nahty>---</td</td---><td>". $row['ip'] . "</td><td>". $row['numero'] ."</td><td>". $row['nimi'] ."</td><td id=".$row['ip']."_kwh>---</td></tr><br>";
   }
   
   $db->close();
?>
</table>