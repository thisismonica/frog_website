<?php
session_start();
if(!isset($_SESSION['curr_file']))
{
    $res['msg'] = "Error: Current filename not set";
    $res['success'] = false;
    $res = json_encode($res);
}else{
	// Run python script to extract functions
	$command = escapeshellcmd('python ../Frog/extract_functions2.py ');
	$result = shell_exec($command.$_SESSION['curr_file']);
	$res = $result;
}
echo $res;
?>