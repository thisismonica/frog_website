<?php
session_start();

$res = array();
$res['success'] = false;

// Check session
if(!isset($_SESSION['curr_test_file']))
{
    $res['msg'] = "Error: Current test filename not set. Check generate test case message.";

}elseif( !isset($_SESSION['test_num'])){
	$res['msg'] = "Error: Test cases number not set, check replay message."

}else{
	$num = $_SESSION['test_num'];
	$testfile = $_SESSION['curr_test_file'];
	$target = $testfile+"_passorfail.txt";

    // Open file to store pass/fail output
    $output = fopen($target, "w");
    if(!$output){
    	$res['msg'] = "Error: unable to store pass/fail info in file: ".$target;
    }else{

    	// Read Post data
    	for($x=0; $x<$num; $x++){
			$name = "testcase".$x;
			$passorfail = $_POST[$name];
			fwrite($output, $passorfail);
			fwrite($output, "\n");
		}
		fclose($output);
		$res['msg'] = "Store pass/fail info in file: ".$target;
	}

 }
echo json_encode($res);
?>