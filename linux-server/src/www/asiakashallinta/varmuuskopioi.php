<?php
$zip = new ZipArchive;
$zip->open('varmuuskopio.zip', ZipArchive::CREATE);
$files = glob("/opt/sahkomittari-server/data/*");
foreach($files as $tiedosto){
    $btiedosto=basename($tiedosto);
    $zip->addFile($tiedosto, $btiedosto);
    echo $tiedosto. " -> ".  $btiedosto. "\n";
}
$zip->close();
header("Location: ./varmuuskopio.zip");
?>
