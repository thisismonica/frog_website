<?php
session_start();
if(!isset($_SESSION['curr_file']))
{
    $res['msg'] = "Error: Current filename not set";
    $res['success'] = false;
    $res = json_encode($res);
}else{
        $target_path = $_SESSION['curr_file'].$_POST['function_id'].".test.c";

	// Run python script to extract functions

############################################################################
# replay.py 
# version 1.0: replay test cases then run tarantula 
# usage: python replay.py [test file] (e.g. mid.c0.test.c)
# output: res['msg'] and res['success']
# output: res['test_output'] test case dictionary array - ['arg'] argument string, ['return'] output string
# output file: [test file name]_matrix.txt
###########################################################################

	$command = escapeshellcmd('python ../Frog/replay.py ');
	$result = shell_exec($command.$target_path);
	$res = $result;

	// Get test cases number
	$json = json_decode($res,true);
	if($json['success'])
		$_SESSION['test_num'] = $json['test_num'];
}
echo $res;
?>
