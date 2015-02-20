 <?php
 // Define KLEE
 define('KLEE_EXECUTABLE', "/home/qirong/Frog/frog_test/tools/KLEE_SOURCE_2015/klee/Release+Asserts/bin/klee "); 
 define('KLEE_OPTIONS' , "--allow-external-sym-calls "); 

session_start();
$res = array();
$res['success'] = false;

// Check session
if(!isset($_SESSION['curr_file']))
{
  $res['msg'] = "Error: Session timeout. Current filename not set";
}else{

    // Test files names
    $target_object = $_SESSION['curr_file'].$_POST['function_id'].".test.o";

    // Check test file generated
    if( !file_exists($target_object) ){
        $res['msg'] = "Error: Test object file does not exist. Compiling Error.";
    }
    else{
            // Run KLEE
            $cmd = KLEE_EXECUTABLE.KLEE_OPTIONS.escapeshellarg($target_object)." 2>&1";
            exec($cmd,$msg,$ret);
	    if($ret==0){
		$res['success'] = true;
		$res['msg'] = "Run KLEE Succeed. ".json_encode($msg);	
	    }
	    else{
	    	$res['msg'] = "Error: run klee failed. ".json_encode($msg);
            }
		
    }
}
echo json_encode($res);
?>
