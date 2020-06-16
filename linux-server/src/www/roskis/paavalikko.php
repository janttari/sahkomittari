<!DOCTYPE html>
<head>
<link rel="stylesheet" type="text/css" href="style.css?ver=1a">
</head>
<script>

//var socketUrl = 'ws://'+location.hostname+(location.port ? ':'+location.port: '')+'/p7777'; //    ws://domain:portti/p7777
var socketUrl = 'ws://localhost:8889';
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
                if ((json.elementit[it].elementti).startsWith("nahty_")){
					//json.elementit[it].style.backgroundColor = "PaleGreen"; 
					document.getElementById(json.elementit[it].elementti).style.backgroundColor = "PaleGreen"; 
				   console.log("NAHTY", json.elementit[it].elementti);	
				}
            }
            else{
                console.log("elementtiä "+json.elementit[it].elementti+" ei ole!");    
            }
        }
};
setInterval(function(){ 
    console.log("timer"); //tässä käydään nähty-sarake läpi ja värjätään punaiseksi jos yli nn sek edellisestä lähetyksestä
    var slides = document.getElementsByClassName("nahty");
        for (var i = 0; i < slides.length; i++) {
            console.log(slides.item(i));
            ero=Date.now()-Date.parse(slides[i].innerHTML);
            if (ero>60000){
			    slides[i].style.backgroundColor = "LightPink"; 	//laitetta ei ole minuuttiin nähty, laitetaan tausta punaiseksi
		    }
        }
}, 5000);

</script>
<table><tr><td>
<div id="yhteys"><font size="-5" color="brown">ei_tiedossa</font>
</td><td>
<div id="muu">asdfas</div>
</td></tr></table>
<br>

<table border=1><tr><td width="300">nähty</td><td width=100>ip</td><td width="100">numero</td><td width="100">nimi</td><td width="100">kwh</td></tr>
<?php 
    class MyDB extends SQLite3 {
        function __construct() {
            $this->open('/yandex/työnalla/sahkomittari/linux-server/src/opt/sahkomittari-server/raspisahkomittari.db');
        }
    }
    $db = new MyDB();
    $sql =<<<EOF
    SELECT * from asiakkaat;
    EOF;

    $ret = $db->query($sql);
    while($row = $ret->fetchArray(SQLITE3_ASSOC) ) {
        echo "<tr><td class=nahty id=nahty_".$row['ip'].">---</td</td---><td>". $row['ip'] . "</td><td>". $row['numero'] ."</td><td>". $row['nimi'] ."</td><td id=kwh_".$row['ip'].">---</td></tr><br>";
    }
   
    $db->close();
?>

</table>
</body>
</html>
