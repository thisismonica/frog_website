<?php
session_start();
if(!isset($_SESSION['curr_file']))
{
    $res['msg'] = "Error: Current filename not set";
    $res['success'] = false;
    $res = json_encode($res);
}else{
	// Run python script to extract functions
	#####################################################
	# extract_functions2.py
	# version 2.0: update RE for more funciton types
	# usage: python extract_function2.py [file name]
	# output: res['msg'] and res['success'], res['content']
	# file output: filename+function_id+".test.c"
	#####################################################

	$command = escapeshellcmd('python ../Frog/extract_functions2.py ');
	$result = shell_exec($command.$_SESSION['curr_file']);
	$res = $result;
}
echo $res;
?>
