<?php

const br = "\n</br>" . PHP_EOL;

echo "Inizio processo". br;

$api = "bot";
$api .= "822833797:AAGhZvgBkFw0t_-rCtkZrQB7h_cXpt9yPlg";	//TEST (token non funzionante)

$webhook = "https://test.jackswork.it/bot/index.php?api=$api";  // Dominio che punta al file index.php del bot dove arrivano le richieste di telegram


echo "Elimino webhook...";
$req = file_get_contents("https://api.telegram.org/$api/deletewebhook");

echo "OK". br ."Elimino updates... ";
$req = file_get_contents("https://api.telegram.org/$api/getupdates?offset=-1");

echo "OK". br ."Risetto webhook... ";
$req = file_get_contents("https://api.telegram.org/$api/setwebhook?url=$webhook&&max_connections=100");

echo "OK". br;

?>