<?php
const MAINSTART = true;


echo "Index Funzionante creato da @JackChevalley ". PHP_EOL;

// ID AMMINISTRATORE PER NOTIFICA DI BUG E PROBLEMI VARI
$admin_errors_ID = 158472703;


$content = file_get_contents("php://input");
$update = json_decode($content, true);

//Chiudo connessione con telegram
if(isset($_SERVER['REMOTE_ADDR'])) {
	$ip = $_SERVER['REMOTE_ADDR'];
	require 'public/access.php';	// Verifica che la richiesta web arrivi da telegram stesso

	set_time_limit(300);
	ignore_user_abort(true);

	$out =  json_encode([
		'method'=>'sendMessage',
		'chat_id'=>0,
		'text'=> "Bot developed by <a href='https://t.me/JackChevalley'>@JackChevalley</a>"
	]);

	header('Connection: close');
	header('Content-Length: '.strlen($out));
	header("Content-type:application/json");

	echo $out;
	flush();

	// Termina la richiesta di telegram prima di processare di modo da velocizzare il processo
	if (function_exists('fastcgi_finish_request')) {
		fastcgi_finish_request();
	}
}


// Crea la connessione con la lib delle richieste
require 'public/request/vendor/autoload.php';
use GuzzleHttp\Client;


// token del bot telegram, like "botTOKEN"
if(isset($_GET["api"]))
	$api = $_GET["api"];
else
	die('NO_API_PROVIDED');


// Crea il client delle richieste
$client = new Client([
	'base_uri' => 'https://api.telegram.org/'. $api .'/',
	'timeout'  => 0
]);

// Crea le funzioni e le variabili
require 'public/functions.php';


if(isset($userID) and !(is_numeric($userID) or $userID < 0)) //Sicurezza
	exit();

if(isset($chatID) and !is_numeric($chatID)) //Sicurezza
	exit();

// Sezione princiaple dei comandi
require 'comandi.php';
?>
