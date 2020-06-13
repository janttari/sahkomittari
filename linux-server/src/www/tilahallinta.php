<?php
if($_POST['Submit']){
$open = fopen("/opt/sahkomittari-server/asiakastiedot_tilat/tilat","w+");
$text = $_POST['update'];
fwrite($open, $text);
fclose($open);
echo "Tiedosto tallennettu!<br />"; 
echo "<meta http-equiv='refresh' content='2;url=index.html'>";
}else{
$file = file("/opt/sahkomittari-server/asiakastiedot_tilat/tilat");
echo "<form action=\"".$PHP_SELF."\" method=\"post\">";
echo "<textarea Name=\"update\" cols=\"100\" rows=\"20\">";
foreach($file as $text) {
echo $text;
} 
echo "</textarea>";
echo "<br><input name=\"Submit\" type=\"submit\" value=\"Tallenna\" />\n
</form>";
}
?>
