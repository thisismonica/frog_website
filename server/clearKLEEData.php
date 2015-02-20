<?php
session_start();
$res = array();
if(!isset($_SESSION['curr_file']))
{
    $res['msg'] = "Session not Login."; 
    $res['success'] = false;
    
}else{

    // Source code files name
    $target_path = $_SESSION['curr_file'];
    
    // Directory name
    $target_dir = dirname( $target_path );

    // KLEE file name
    $klee_files = $target_dir."/klee-*";
    
    // Check file exist
    $lscmd = "ls ".$klee_files." 2>/dev/null";
    exec($lscmd, $lsmsg, $lsreturn);

    if($lsreturn == 0){
	    
            // Remove file if file exist
	    $cmd = "rm -r ".$klee_files." 2>/dev/null ";
	    exec($cmd, $msg, $return);
	    if($return == 0){
		$res['msg'] = "Old KLEE data cleared.";
		$res['success'] = true;           
	    }else{
                $res['msg'] = "Error: Unable to remove KLEE data."; 
	        $res['success'] = false;
            } 
     }else{
	   $res['msg'] = "KLEE data already cleared.";
           $res['success'] = true;
     }    
}
echo json_encode($res);
?>
