 <?php
session_start();
if(!isset($_SESSION['curr_file']))
{
    $res['msg'] = "Error: Current filename not set";
    $res['success'] = false;
    $res = json_encode($res);
}else{
	// Test files names
    $target_path = $_SESSION['curr_file'].$_POST['function_id'].".test.c";

    // Test file not generated
    if( !file_exists($target_path) ){
        $res['msg'] = "Error: Test file does not exist. NO valid functions found.";
        $res['success'] = false;
    }
    else{
	// Run python script to Compile and run KLEE
	$command = escapeshellcmd('python ../Frog/run_klee.py ');
	$result = shell_exec($command.$target_path);
	$res = $result;
	}
}
echo $res;
?>
