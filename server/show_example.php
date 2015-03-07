<?php
/*
 * Load example source code to user folder
 * Set $_SESSION['curr_file']
 ****************************************
 */

session_start();

// Directory name for example code
$dirname = "examples/";	

// Check session starts
if(!isset( $_SESSION['username'] ) ){
	$ret['msg'] = "Error: User not login.";
	$ret['success'] = false;
}else{
	$filename = $_POST['filename'];
	$src= $dirname.$filename;
	
	// Check example file exist
	if( !file_exists($src) ){
		$ret['msg'] = 'Example file not exist '.$src;	
		$ret['success'] = false;
	}else{
		 // Create new directory with 744 permissions if it does not exist yet
		$target_path = "uploads_".$_SESSION['username']."/";
		if ( !file_exists($target_path) ) {
		  mkdir ($target_path, 0744);
		}
		else{
			// Clear old data
			$clear = "rm -r ".$target_path."/* 2>/dev/null";
			exec($clear);
		}

		// Move example file to user folder
		$target = $target_path . $filename;
		$cp_cmd = "cp ".$src." ".$target;
		exec($cp_cmd, $msg, $return);
		if($return==0){
			$ret['success'] = true;
			$ret['msg'] = "Load example file succeed.";
			
			// Set curr_file
			$_SESSION['curr_file'] = $target;
			
		}else{
			$ret['success'] = false;
			$ret['msg'] = "Error: Unable to load example file.";
		}
	}
}
echo json_encode($ret);
?>
