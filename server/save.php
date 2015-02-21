<?php
// Check session
session_start();
$FILE_NAME = "user_file";

/* 
 * User has not uploaded any file, create new file to save content
*/
if(!isset( $_SESSION['curr_file'] ) || !file_exists($_SESSION['curr_file']))
{
    // Create directory
    $target_path = "uploads/";
    if ( !file_exists($target_path) ) {
        mkdir ($target_path, 0744);
    }

    // Create file
    $file_name = $FILE_NAME;
    $target_path = $target_path . basename( $file_name);
    $myfile = fopen($target_path, "w") or die("Unable to open file!");
    fclose($myfile);
    $_SESSION['curr_file'] = $target_path;
}

/* 
 * Write content to file
*/
$filepath = $_SESSION['curr_file'];
$arr = array();

// Check if file exists
if(file_exists($filepath))
{
    // Check for write permission
    if(is_writeable($filepath))
    {   
        // Obtain content
        $content = $_POST['content'];

        // Convert encoding
        $content = iconv("utf-8","gb2312",$content);  

        // Write to file
        file_put_contents($filepath, $content);

        $arr['success'] = true;
    }
    else
    {
        // No permission to write
        $arr['msg'] = "You do not have write permission.";
        $arr['success'] = false;
    }
}
else
{
    // File does not exist
    $arr['msg'] = 'File does not exist.';
    $arr['success'] = false;
}
echo json_encode($arr);

?>
