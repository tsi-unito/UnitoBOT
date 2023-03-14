<?php
if(!defined('MAINSTART')) { die(); }


echo "Funzioni Funzionante". PHP_EOL;
date_default_timezone_set('Europe/Rome');

//CREAZIONE VARIABILI UPDATE
if(true) {

    if(isset($update['channel_post']))
        $update['message'] = $update['channel_post'];

    if(isset($update["callback_query"])) {
        $msg = strip_tags($update["callback_query"]["data"]);

        $cbid = $update["callback_query"]["id"];
        $cbmid = $update["callback_query"]["message"]["message_id"];
        $chatID = $update["callback_query"]["message"]["chat"]["id"];
        $userID = $update["callback_query"]["from"]["id"];

        $nome = strip_tags($update["callback_query"]["from"]["first_name"]);

        if(isset($update["callback_query"]["from"]["last_name"]))
            $cognome = strip_tags($update["callback_query"]["from"]["last_name"]);

        if(isset($update["callback_query"]["from"]["username"]))
            $username = strip_tags($update["callback_query"]["from"]["username"]);
    }
    else {
        if(isset($update["message"]["chat"]["id"]))
            $chatID = $update["message"]["chat"]["id"];

        if(isset($update["message"]["from"]["id"]))
            $userID = $update["message"]["from"]["id"];

        if(isset($update["message"]["from"]["first_name"]))
            $nome = strip_tags($update["message"]["from"]["first_name"]);

        if(isset($update["message"]["from"]["last_name"]))
            $cognome = strip_tags($update["message"]["from"]["last_name"]);

        if(isset($update["message"]["from"]["username"]))
            $username = $update["message"]["from"]["username"];

        if(isset($update["message"]["chat"]["title"]))
            $title = $update["message"]["chat"]["title"];
    }

    { //DEFINISCE IL TIPO DI MESSAGGIO

        //messaggi
        if(isset($update['message']['text'])) {
            $msg = $update["message"]["text"];
            $TIPO = "text";
        }

        //audio
        elseif(isset($update['message']["audio"]['file_id'])) {
            $audio = $update["message"]["audio"]['file_id'];
            $TIPO = "audio";
        }

        //animation
        elseif(isset($update['message']["animation"]['file_id'])) {
            $animation = $update["message"]["animation"]['file_id'];
            $TIPO = "animation";
        }

        //sticker
        elseif(isset($update['message']["sticker"]['file_id'])) {
            $sticker = $update["message"]["sticker"]['file_id'];
            $TIPO = "sticker";
        }

        //photo
        elseif(isset($update['message']["photo"][0]['file_id'])) {
            $photo = $update["message"]["photo"][0]['file_id'];
            $TIPO = "photo";
        }

        //video
        elseif(isset($update['message']["video"]['file_id'])) {
            $video = $update["message"]["video"]['file_id'];
            $TIPO = "video";
        }

        //voce
        elseif(isset($update['message']["voice"]['file_id'])) {
            $audio = $update["message"]["voice"]['file_id'];
            $TIPO = "voice";
        }

        //video_note
        elseif(isset($update['message']["video_note"]['file_id'])) {
            $video_note = $update["message"]["video_note"]['file_id'];
            $TIPO = "video_note";
        }

        //document
        elseif(isset($update['message']["document"]['file_id'])) {
            $document = $update["message"]["document"]['file_id'];
            $TIPO = "document";
        }

        if(isset($update['message']['forward_from_chat']))
            $forward = $update['message']['forward_from_chat'];
    }


    if(isset($update['message']['caption']))
        $caption = strip_tags($update['message']['caption']);


    if(isset($update["message"]["message_id"]))
        $msgid = $update["message"]["message_id"];


    if(isset($update['message']['entities']))
        $ent = $update['message']['entities'];

    if(isset($update['message']['caption_entities']))
        $ent = $update['message']['caption_entities'];

}


//messaggi
function sm($chatID, $text, $menu = false, $fm = "html", $link = false) {
    global $client;

    if(is_array($text))
        $text = implode("\n", $text);


    if(isset($menu) and $menu) {
        if($menu == "del") {
            $rm['remove_keyboard'] = true;
        }
        else {
            if(isset($menu[0][0]["text"])) {
                $rm = ['inline_keyboard' => $menu];
            }
            else {

                $rm = ['keyboard' => $menu, 'resize_keyboard' => true];
            }
            $rm['force_reply'] = false;
            $rm = json_encode($rm);
        }
    }


    $args = [
        'disable_web_page_preview' => $link,
        'chat_id' => $chatID,
        'text' => $text,
        'parse_mode' => $fm
    ];

    if($menu) $args["reply_markup"] = $rm;


    $response = $client->request('POST', 'sendmessage', ['json' => $args]);
    $rr = $response->getBody();

    $rr = json_decode($rr, true);


    if(isset($rr['result']['message_id']))
        return($rr['result']['message_id']);
    else {

        if($chatID == $admin_errors_ID)
            sm($chatID, "Errore1: ". $rr['description'], false, '');
        return 0;
    }
}

//messaggi con eliminazione
function smg($chatID, $text, $menu = false, $fm = "html", $link = false) {
    global $client;

    if(is_array($text))
        $text = implode("\n", $text);

    if(isset($menu) and $menu) {
        if($menu == "del") {
            $rm['remove_keyboard'] = true;
        }
        else {
            if(isset($menu[0][0]["text"])) {
                $rm = ['inline_keyboard' => $menu];
            }
            else {
                $rm = ['keyboard' => $menu, 'resize_keyboard' => true];
            }
            $rm['force_reply'] = false;
            $rm = json_encode($rm);
        }
    }


    $args = [
        'disable_web_page_preview' => $link,
        'chat_id' => $chatID,
        'text' => $text,
        'parse_mode' => $fm
    ];

    if($menu) $args["reply_markup"] = $rm;


    $response = $client->request('POST', 'sendmessage', ['json' => $args]);
    $rr = $response->getBody();
    $rr = json_decode($rr, true);

    if(isset($rr['result']['message_id'])) {

        global $us;
        if($us['last_id'] != 0)
            del($us['last_id']);

        secure("UPDATE utenti SET last_id = ". $rr['result']['message_id'] ." WHERE chat_id = $chatID");
        return ($rr['result']['message_id']);
    }
    else {

        if($chatID == $admin_errors_ID)
            sm($chatID, "Errore2: ". $rr['description'], false, '');
        return 0;
    }
}

//foto
function si($chatID, $photo, $caption = false, $menu = false) {
    global $client;


    if(isset($menu) and $menu) {
        if($menu == "del") {
            $rm['remove_keyboard'] = true;
        }
        else {
            if(isset($menu[0][0]["text"])) {
                $rm = ['inline_keyboard' => $menu];
            }
            else {
                $rm = ['keyboard' => $menu, 'resize_keyboard' => true];
            }
            $rm['force_reply'] = false;
            $rm = json_encode($rm);
        }
    }

    if(!(isset($caption)) or !$caption)
        $caption = '';

    if(is_array($caption))
        $caption = implode("\n", $caption);


    $args = [
        'chat_id' => $chatID,
        'photo' => $photo,
        'parse_mode' => 'html',
        'caption' => $caption
    ];

    if($menu) $args["reply_markup"] = $rm;

    $response = $client->request('POST', 'sendphoto', ['json' => $args]);
    $r = $response->getBody();

    $rr = json_decode($r, true);

    if(isset($rr['result']['message_id']))
        return($rr['result']['message_id']);
    else {

        if($chatID == $admin_errors_ID)
            sm($chatID, "Errore3: ". $rr['description'], false, '');
        return 0;
    }
}


//edit
function cb_reply($text = false, $menu = false, $cbmid = false, $fm = "html", $page = false, $cbid = false, $ntext = false, $ntype = false) {

    global $client;
    global $chatID;

    if(is_array($text))
        $text = implode("\n", $text);

    if(!(isset($cbmid)) or !$cbmid)
        if(isset($GLOBALS['cbmid'])) $cbmid = $GLOBALS['cbmid'];

    if(!(isset($cbid)) or !$cbid) global $cbid;
    if(isset($GLOBALS['cbid'])) $cbid = $GLOBALS['cbid'];

    if(isset($text) and $text) {

        $args = [
            'chat_id' => $chatID,
            'message_id' => $cbmid,
            'text' => $text,
            'parse_mode' => $fm,
            'disable_web_page_preview' => $page
        ];

        if(isset($menu) and $menu) {
            $rm = ['inline_keyboard' => $menu];
            $rm = json_encode($rm);
            $args["reply_markup"] = $rm;
        }


        $response = $client->request('POST', 'editMessageText', ['json' => $args]);
        $r = $response->getBody();
        $rr = json_decode($r, true);

        if(!(isset($rr['ok']) and $rr['ok']) and $chatID == $admin_errors_ID)
            sm($chatID, "Errore4: ". $rr['description'], false, '');

    }

    if(isset($cbid) and $cbid) {
        $args = ['callback_query_id' => $cbid];

        if(isset($ntext) and $ntext) //Notifica su schermo
        {
            $args['text'] = $ntext;
            $args['show_alert'] = $ntype;
        }

        $client->request('POST', 'answerCallbackQuery', ['json' => $args]);
    }

}

//elimina messaggio
function del($msgid = false, $chatID = false) {
    global $client;
    if(!$chatID) global $chatID;
    if(!$msgid) {
        global $us;
        $msgid = $us['last_id'];
    }

    $args = [
        'chat_id' => $chatID,
        'message_id' => $msgid
    ];

    $client->request('POST', 'deletemessage', ['json' => $args]);
}


//costruisci la varibile sql, DUBUG
function build($sql, $array) {
    foreach(array_keys($array) as $var) {
        $sql = str_replace(":". $var, '"'. $array[$var] .'"', $sql);
    }

    global $chatID;

    if($chatID === $admin_errors_ID)
        sm($chatID, "<b>BUILD ESEGUITO</b> \n\n<code>". $sql ."</code>\n\n<code>". $array ."</code>");
}


//controllo che sia un click di un bottone, non indispendabile
function cbid() {
    global $cbid;

    if(!(isset($cbid)))
        exit();
}


// Esegui una richiesta mediante il clinet, like request('getChannel', ['chat_id' => $chatID]);
function request($url, $args, $method='POST') {

    global $client;

    $response = $client->request($method, $url, ['json' => $args]);
    $rr = $response->getBody();
    return json_decode($rr, true);
}


// Invia il messaggio di errore e ferma l'esecuzione
function error($text, $chatID=False, $die=1) {

    if(!$chatID)
        global $chatID;

    sm($chatID, '❌ '. $text);

    if($die)
        die();
}

?>