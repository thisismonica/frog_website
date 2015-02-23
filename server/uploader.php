<?php
session_start();

// Check session starts
if(!isset( $_SESSION['username'] ) ){
	$ret['error'] = "Not login.";
	$ret['success'] = false;
}else{

	$target_path = "uploads_".$_SESSION['username']."/";
	//$target_path = "uploads/";

	 // Create new directory with 744 permissions if it does not exist yet
	if ( !file_exists($target_path) ) {
	  mkdir ($target_path, 0744);
	}

	 // Upload files
	if(isset($_FILES["source_code"]))
	{
		
		// Clear previous data
		$clear = "rm -r ".$target_path."/* 2>/dev/null";
		exec($clear);

		$ret = array();

		$error =$_FILES["source_code"]["error"];
		$ret['error'] = $error;
		$ret['success'] = false;

		// Upload single file
		if(!is_array($_FILES["source_code"]["name"])) //single file
		{
			$file_name = $_FILES["source_code"]["name"];
			$target_path = $target_path . basename( $file_name);

			// Store file in server
			if(move_uploaded_file($_FILES["source_code"]["tmp_name"], $target_path) ){

				//TODO: file name for specific user
				$_SESSION['curr_file'] = $target_path;
				$ret['file_name']= $file_name;
				$ret['success'] = true;
			}

			// Read file content
			$file_content = file_get_contents($target_path);
			$ret['content'] = $file_content;
		}
	}
}
echo json_encode($ret);
?>
