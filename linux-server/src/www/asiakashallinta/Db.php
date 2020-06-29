<?php
class Db {

	public $db;

	public function __construct($db){
		$this->db = new SQLite3($db);
		$this->init();
	}

	private function init(){
		//$this->dropStudentTable();
		$this->createStudentTable();
	}


	public function createStudentTable(){
		return $this->db->exec('CREATE TABLE IF NOT EXISTS asiakkaat (ip TEXT, nimi TEXT, numero TEXT)');
	}

	public function dropStudentTable(){
		return $this->db->exec('DROP TABLE asiakkaat');
	}

	public function insert($ip, $nimi, $numero){
		return $this->db->exec("INSERT INTO asiakkaat (ip, nimi, numero) VALUES ('$ip', '$nimi', '$numero')");
	}

	public function update($id, $ip, $nimi, $numero){
		return $this->db->query("UPDATE asiakkaat set ip='$ip', nimi='$nimi', numero='$numero' WHERE rowid=$id");
	}

	public function delete($id){
		return $this->db->query("DELETE FROM asiakkaat WHERE rowid=$id");
	}

	public function getAll(){
		return $this->db->query("SELECT rowid, * FROM asiakkaat");
	}

	public function getById($id){
		return $this->db->query("SELECT rowid, * FROM asiakkaat WHERE rowid=$id");
	}
}

?>
