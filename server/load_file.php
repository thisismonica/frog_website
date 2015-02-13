<?php
session_start();
$res = array();
if(!isset($_SESSION['curr_file']))
{
    $res['msg'] = "not uploaded."; 
    $res['success'] = false;
    $res['unset'] = true;
    
}else{
    $res['unset'] = false;
    // Source code files name
    $target_path = $_SESSION['curr_file'];

    // Test file not generated
    if( !file_exists($target_path) ){
        $res['msg'] = "Error: Source code file does not exist.";
        $res['success'] = false;
    }

    // Test file found
    else{
        $res['success'] = true;
        $res['msg'] = "Load source code file succeed.";
        $file_content = file_get_contents($target_path);
        $res['content'] = $file_content;
    }
}
echo json_encode($res);
?>
