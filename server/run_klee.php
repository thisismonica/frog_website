 <?php
 // Define KLEE
 define('KLEE_EXECUTABLE', '/home/qirong/Frog/frog_test/tools/KLEE_SOURCE_2015/klee/Release+Asserts/bin/klee ');
 define('KLEE_OPTIONS',' --allow-external-sym-calls ');

session_start();

// Check session
if(!isset($_SESSION['curr_file']))
{
    $res['msg'] = "Error: Current filename not set";
    $res['success'] = false;
}else{

	// Test files names
    $target_path = $_SESSION['curr_file'].$_POST['function_id'].".test.c";
    $target_object = $_SESSION['curr_file'].$_POST['function_id'].".test.o";

    // Check test file generated
    if( !file_exists($target_path) ){
        $res['msg'] = "Error: Test file does not exist. NO valid functions found.";
        $res['success'] = false;
    }
    else{
    	// LLVM Compile
    	$command = escapeshellcmd('python ../Frog/compile.py ');
    	$llvm_result = shell_exec($command.$target_path);

        // If compile succeed, run KLEE
        if($llvm_result['success']){

            // Run KLEE
            $cmd .= KLEE_EXECUTABLE.KLEE_OPTIONS.escapeshellarg($target_object);
            exec($cmd,$msg,$ret);

            // if successfully run
            if($ret == 0){
                $res['success'] = true;
                $res['msg'] = $msg;
            }
            else{
                $res['success'] = false;
                $res['msg'] = $msg;
            }
        }
        else{
            $res['success'] = false;
            $res['msg'] = $llvm_result['msg'];
        }
     }   
}
$res = json_encode($res);
echo $res
?>
