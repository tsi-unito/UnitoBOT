<?php
if (!defined('MAINSTART')) { die(); }

echo "Comandi funzionante <br/>\n";


/* NOTAZIONI

    - la funzione smg invia un messaggio normalmente come la funzione sm. Inoltre però in automatico salva nella riga "last_id"
    del database della tabella "utenti" relativa all'utente in corso, ID del messaggio che è appena stato inviato.
    Quando viene ripetuto un smg (tipo se fai due volte /start ed hai smg come output principale) il vecchio messaggio viene eliminato, ne viene mandato uno nuovo, viene aggiornato ID in database.
    Questo è utile per evitare che il bot invii messaggi doppi e di avere mille menù cliccabili. Se vai su multiforwardbot e fai /start due volte, vedrai cosa intendo

    - per modificare un messaggio usa la funzione cb_reply

*/

//CREAZIONE VARIABILI
if (true) {

    //Amministratori
    $adm = [];
    $adm[] = 158472703;

    //Se l'utente è nell'array adm, è admin. adm prende quindi valore dell'utente attuale. Serve per limitare i comandi admin
    $adm = in_array($userID, $adm) ? $userID : 158472703;

    //Username del bot
    $ub = "TestJackBot";

    // Utili da usare nei testi e nei bottoni, emp sarebbe il carattere invisibile
    $bc = "Indietro 🔙";
    $st = "Indietro 🔚";
    $bin = "🗑";
    $emp = "ㅤ";


    //Se collegarsi o meno al database, false = non collegarti
    $database = false;


    { //Qualcosa di sicurezza

        if (!(isset($chatID))) //test da pc
            exit();

        // Blocca gruppi e canali
        if ($chatID < 0) {
            exit();
        }

    }


    //Connessione effettiva al database
    if ($database) {

        require 'public/database.php';
        function temp($val = 0, $userID = 0) {  //Modifica il valore della colonna "temp" nel database, temp(); per mettere vuoto. default usa userID dell'utente attuale

            if (!$userID) global $userID;
            if (!$val) $val = '';

            secure("UPDATE utenti SET temp = :temp WHERE chat_id = $userID", ["temp" => $val]);
        }


        //STRUTTURA BASE DEL DATABASE:
        // Tabella utenti: ID (autoincrement); chat_id (bigint, index); last_id (int, max 10 cifre per sicurezza, default NULL); temp (varchar 200, default NULL);
        $us = secure("SELECT * FROM utenti WHERE chat_id = :id", ['id' => $userID], 1);
        if (!(isset($us['chat_id']))) {
            secure("INSERT INTO utenti(chat_id) VALUE (:id)", ['id' => $userID]);
            $us = secure("SELECT * FROM utenti WHERE chat_id = :id", ['id' => $userID], 1);
        }
    }
}



//Gestione dei messaggi normali
if (isset($msg)) {

    //SEZIONE DEI COMANDI
    if (strpos($msg, '/')===0) {

        //Comando iniziala, start
        if ($msg == "/start") {

            $cbmid = sm($chatID, "Request");
            cb_reply("Edit... 1");
            cb_reply("Edit... 2");
            cb_reply("Edit... 3");
            cb_reply("Edit... 4");
            cb_reply("Edit... 5");
            cb_reply("Edit... 6");
            cb_reply("Edit... 7");
            cb_reply("Edit... 8");
            cb_reply("Edit... 9");
            cb_reply("Edit... 10");
        }


        //Sezione Amministratori
        elseif ($userID == $adm) {

            die();
        }

    }


    //SEZIONE DEGLI INPUT di testo
    elseif (isset($us['temp']) and $us['temp']) {


        //Sezione Amministratori
        if ($userID == $adm) {

            die();
        }

        die();
    }

}


//Gestione dei media
else {

    die();
}



?>