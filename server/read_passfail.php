<?php
session_start();

$res = array();
$res['success'] = false;
$res['msg'] = "";

// Check session
if(!isset($_SESSION['curr_test_file']))
{
    $res['msg'] = "Error: Current test filename not set. Check generate test case message.";

}elseif( !isset($_SESSION['test_num'])){
	$res['msg'] = "Error: Test cases number not set, check replay message.";

}else{
	$num = intval($_SESSION['test_num']);
	$testfile = $_SESSION['curr_test_file'];
	$target = $testfile."_passorfail.txt";

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
		$res['msg'] = "Pass or Fail data saved.";

		// Run tarantula
		$cmd = "python ../Frog/tarantula.py ".$testfile;
		$msg = shell_exec( $cmd );
		$msg_json = json_decode( $msg , true);

		if($msg_json['success']){ 
			$res['msg'] = $res['msg']." Run Tanrantula succeed.";
			$res['success'] = true;
			$res['suspiciousness'] = $msg_json['suspiciousness'];
		}else{
			$res['msg'] = $res['msg'].$msg_json['msg'];			
		}
	}

 }
echo json_encode($res);
?>
