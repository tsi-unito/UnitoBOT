<?php
if(!defined('MAINSTART')) { die("<b>The sender's IP has not been recognised.</br>All the actions were stopped</b>"); }

if(isset($_SERVER['REMOTE_ADDR'])) {

    if (isset($_SERVER["HTTP_CF_CONNECTING_IP"])) {
        $_SERVER['REMOTE_ADDR'] = $_SERVER["HTTP_CF_CONNECTING_IP"];
        $_SERVER['HTTP_CLIENT_IP'] = $_SERVER["HTTP_CF_CONNECTING_IP"];
    }
    $client  = @$_SERVER['HTTP_CLIENT_IP'];
    $forward = @$_SERVER['HTTP_X_FORWARDED_FOR'];
    $remote  = $_SERVER['REMOTE_ADDR'];

    if(filter_var($client, FILTER_VALIDATE_IP)) { $ip = $client; }
    elseif(filter_var($forward, FILTER_VALIDATE_IP)) { $ip = $forward; }
    else { $ip = $remote; }
}

if(isset($ip) and !(strpos($ip, "145.239")===0)) {
    if(! in_array( substr( $_SERVER['HTTP_X_FORWARDED_FOR'], 0, 11), ['149.154.167','149.154.160']) and !strpos(' '.$_SERVER['HTTP_X_FORWARDED_FOR'],'91.108.6')) {
        die("<b>The sender's IP has not been recognised.</br>All the actions were stopped</b>");
    }
}