<?php
session_start();
$res = array();
if(!isset($_SESSION['curr_file']))
{
    $res['msg'] = "Error: Test file does not exist. Please extract functions first.";
    $res['success'] = false;
    
}else{
    // Test files names
    $target_path = $_SESSION['curr_file'].$_POST['function_id'].".test.c";
    $_SESSION['curr_test_file'] = $target_path;

    // Test file not generated
    if( !file_exists($target_path) ){
        $res['msg'] = "Error: Test file does not exist. NO valid functions found.";
        $res['success'] = false;
    }
    // Test file found
    else{
        $res['success'] = true;
        $res['msg'] = "Instrumented test file generated.";
        $file_content = file_get_contents($target_path);
        $res['content'] = $file_content;
    }
}
echo json_encode($res);
?>
