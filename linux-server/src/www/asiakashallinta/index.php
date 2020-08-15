<!-- php sqlite3 esimerkki https://github.com/sinha2773/crud_sqlitedb -->

<?php session_start();

spl_autoload_register('autoloader');

function autoloader($class){
	include("$class.php");
}

$db = new Db('/opt/sahkomittari-server/data/asiakkaat.db');

//inserting data
if( isset($_POST['ADD_ASIAKAS']) ){
        $ip = $_POST['ip'];
	$nimi = $_POST['nimi'];
	$numero = $_POST['numero'];
	if( $db->insert($ip, $nimi, $numero) ){
		$msg = array('1', "Asiakas lisätty.");
	}else{
		$msg = array('0', "Asiakkaan lisääminen epäonnistui.");
	}
	$_SESSION['msg'] = $msg;
}

//geting edit items
if( isset($_REQUEST['edit']) ){
	$id = $_GET['id'];
	$data = $db->getById($id)->fetchArray();
}

//updateing data
if( isset($_POST['UPDATE_ASIAKAS']) ){
	$id = $_POST['id'];
        $ip = $_POST['ip'];
	$nimi = $_POST['nimi'];
	$numero = $_POST['numero'];
	if( $db->update($id, $ip, $nimi, $numero) ){
		$msg = array('1', "Asiakas päivitetty.");
	}else{
		$msg = array('0', "Asiakkaan päivittäminen epäonnistui.");
	}
	$_SESSION['msg'] = $msg;
	header("Location: /asiakashallinta");
	exit;
}

//deleting data
if( isset($_REQUEST['delete']) ){
	$id = $_GET['id'];
	if( $db->delete($id) ){
		$msg = array('1', "Asiakkaan poistaminen onnitui.");
	}else{
		$msg = array('0', "Asiakkaan poistaminen epäonnistui.");
	}
	$_SESSION['msg'] = $msg;

	header("Location: /asiakashallinta");
	exit;
}


// to show updating form
$isEdit = isset($_REQUEST['edit']) ? true : false;

?>

<!DOCTYPE html>
<html>
<head>
	<title>Asiakashallinta</title>
	<style type="text/css">
		.red { color: red; }
		.green { color: green; }
	</style>
</head>
<body>
<a href="../">[Palaa]</a>
<a href="varmuuskopioi.php">[Lataa varmuuskopio]</a>
<br><br>
	<div style="margin: 0 auto; width: 800px;">
		<div>
			<form style="display:<?php echo $isEdit ? 'none':'block'; ?>" action="" method="post">
                                <input type="text" name='ip' placeholder="Anna IP" required="">
				<input type="text" name='nimi' placeholder="Anna kontin nimi" required="">
				<input type="text" name='numero' placeholder="Anna kontin numero" required="">
				<input type="submit" name="ADD_ASIAKAS" value="Lisää">
			</form>

			<form style="display:<?php echo $isEdit ? 'block':'none'; ?>" action="" method="post">
				<input type="hidden" name="id" value="<?php echo isset($data) ? $data['rowid'] : ''; ?>">
                                <input type="text" name='ip' value="<?php echo isset($data) ? $data['ip'] : ''; ?>" placeholder="Anna IP">
				<input type="text" name='nimi' value="<?php echo isset($data) ? $data['nimi'] : ''; ?>" placeholder="Anna nimi">
				<input type="text" name='numero' value="<?php echo isset($data) ? $data['numero'] : ''; ?>" placeholder="Anna numero" required="">
				<input type="submit" name="UPDATE_ASIAKAS" value="Tallenna">
			</form>

			<?php if( isset($_SESSION['msg']) && !empty($_SESSION['msg']) ){ ?>
			<p class="<?php echo $_SESSION['msg'][0]==0 ? 'red' : 'green';?>"><?php echo $_SESSION['msg'][1];?></p>
			<?php } ?>
		</div>
		<table cellpadding="5" border="1" width="100%">
			<tr>
				<td>ID</td>
				<td>IP</td>
                                <td>Nimi</td>
				<td>Numero</td>
				<td>Toiminto</td>
			</tr>
			<?php 
			$result = $db->getAll();
			//echo "<pre>"; print_r($result->fetchArray());
			//$allData = 
			while($row = $result->fetchArray()) {?>
				
			<tr>
				<td><?php echo $row['rowid'];?></td>
				<td><?php echo $row['ip'];?></td>
                                <td><?php echo $row['nimi'];?></td>
				<td><?php echo $row['numero'];?></td>
				<td>
					<a href="?edit=true&id=<?php echo $row['rowid']; ?>">Muuta</a> | 
					<a href="?delete=true&id=<?php echo $row['rowid']; ?>" onclick="return confirm('Are you sure?');">Poista</a>
				</td>
			</tr>
			<?php } ?>

		</table>
	</div>
<?php $_SESSION['msg'] = array(); ?>
</body>	
</html>
