<?php
if(!defined('MAINSTART')) { die(); }


try {
	// Esegui connesione al database
	$db = new PDO("mysql:host=127.0.0.1;dbname=#######;charset=utf8mb4", "admin", "######");


	$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
	echo "Errore: " . $e->getMessage() . PHP_EOL;
	die();
}


// Funzione per eseguire le richieste al database in maniera sicura.
// $me = secure("SELECT * FROM utenti WHERE chat_id = :id AND nome = :nome", ['id' => $chatID, 'nome' => $nome], 1);
// Per usare parametri aggiungere :parametro e poi aggiungere il parametro nell'array. Il terzo parametro è la tipologia di return.
// 0 = nessun return, 1 = return di una riga, 2 = return del numero di righe, 3 return di tutte le righe.
// secure("UPDATE utenti SET nome = :nome WHERE chat_id = :id", ['nome' => "Jacopo", 'chat_id' => 158472703]);		// modifica il nome di un utente senza return
// $utenti = secure("SELECT * FROM utenti", 0, 1); // Ritorna il primo utente
// $utenti = secure("SELECT * FROM utenti", 0, 2); // Ritorna il numero di utenti
// $utenti = secure("SELECT * FROM utenti", 0, 3); // Ritorna tutti gli utenti
function secure ($sql, $par = 0, $fc = 0, $if = 1) {
	global $db;

	try {
		$sc = $db->prepare($sql);
		if(isset($par) and $par)
			$sc->execute($par);
		else
			$sc->execute();
	} catch (PDOException $e) {
		die();
	}

	if(isset($fc) and $fc) {
		if($fc == 1)		return $sc->fetch(PDO::FETCH_ASSOC); //fetch primo risultato
		elseif($fc == 2)	return $sc->rowCount(); //fetch numero risultati
		elseif($fc == 3)	return $sc->fetchAll(); //fetch di tutti risultati
	}
}


?>
