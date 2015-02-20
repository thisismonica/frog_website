 <?php
 // Define KLEE
define('COMPILE','/home/kuan/llvm-gcc4.2-2.9-x86_64-linux/bin/llvm-gcc --emit-llvm -c -g '); 
define('KLEE_INCLUDE','/home/qirong/Frog/frog_test/tools/KLEE_SOURCE_2015/klee/include/klee ');

session_start();

$res = array();

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
	// Delete old object
	if(file_exists($target_object)){
		unlink($target_object);
	}

    	// LLVM Compile
	$cmd =COMPILE.' -I'.KLEE_INCLUDE.' -o '.$target_object;
	$cmd = $cmd.' '.$target_path." 2>&1";
	escapeshellcmd($cmd);
	
	exec($cmd,$msg,$return);

	if($return==0){
		$res['success'] = true;
		$res['msg'] = "Compile succeed. \n".implode("; ",$msg);
	}
	else{
		$res['success'] = false;
		$res['msg'] = $cmd."Error: Compile failed. \n".implode("; ",$msg);
	}	
     }   
}

echo json_encode( $res );
?>
