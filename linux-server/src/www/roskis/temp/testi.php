<?php
   class MyDB extends SQLite3 {
      function __construct() {
         $this->open('mydatabase.sqlite');
      }
   }
   
   $db = new MyDB();
/*
   if(!$db) {
      echo $db->lastErrorMsg();
   } else {
      echo "Opened database successfully<br>";
   }
*/
//SELECT * from ASIAKKAAT WHERE nimi="Raspi";

   $sql =<<<EOF
     SELECT * from ASIAKKAAT;

EOF;

   $ret = $db->query($sql);
   while($row = $ret->fetchArray(SQLITE3_ASSOC) ) {
      echo "ip = ". $row['ip'] . " --> ";
      echo "nimi = ". $row['nimi'] ."<br>";
   }
   echo "Operation done successfully<br>";
   $db->close();
?>
