<!doctype html>

<html lang="fi">
<head>
  <meta charset="utf-8">

  <title>Kuukausiraportit</title>

</head>

<body>
  <a href="../">[palaa]</a>
  <br>
  Tulosta kuukauden alkukulutus kuukaudelle:
  <form action="raportti.php" method="get">
   Vuosi: <input type="text" name="vuosi" value="<?php echo date("Y"); ?>">
   Kuukausi: <input type="text" name="kuukausi" value="<?php echo date("m"); ?>">
   <input type="submit" value="Kysely">
  </form>
</body>
</html>
