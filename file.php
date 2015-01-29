<?php

//include "session.php";
//include "constant.php";

// Check login status
session_start();

if(!isset($_SESSION['curr_file']))
{
    $arr['msg'] = "Error: Current filename not set";
    $arr['res'] = false;
}
else
{
    $action = $_POST['action'];

    // Get file path
    //$filepath = USER_DIR.$_SESSION['username'].'/'.$_SESSION['curr-proj'].'/'.$_POST['filepath']; 
    $filepath = $_SESSION['curr_file'];

    if($action == "read")
    {
        /*
         * Read a file
         */
        // Check if file exists
        if(file_exists($filepath))
        {
            // Check for read permission
            if(is_readable($filepath))
            {
                // Read file content
                $fileContent = file_get_contents($filepath);

                // Convert file encoding from utf-8 to gb2312
                $fileContent = iconv("gb2312","utf-8//IGNORE",$fileContent);

                $arr['content'] = $fileContent;
                $arr['res'] = true;
            }
            else
            {
                // No permission to read
                $arr['msg'] = "You do not have read permission.";
                $arr['res'] = false;
            }
        }
        else
        {
            // File does not exist
            $arr['msg'] = 'File does not exist.';
            $arr['res'] = false;
        }
    }
    else if($action == "save")
    {
        /*
         * Save a file
         */

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

                $arr['res'] = true;
            }
            else
            {
                // No permission to write
                $arr['msg'] = "You do not have write permission.";
                $arr['res'] = false;
            }
        }
        else
        {
            // File does not exist
            $arr['msg'] = 'File does not exist.';
            $arr['res'] = false;
        }
    }
    else if($action == "delete")
    {
        /*
         * Delete a file
         */

        // Check if file exists
        if(file_exists($filepath))
        {
           // Check for write permission
           if(is_writeable($filepath))
           {
               // Unlink the file
               if(unlink($filepath))
               {
                   // Unset session for certain files
                   $tmpMd5 = md5($filepath);
                   if(isset($_SESSION[$tmpMd5]))
                      unset($_SESSION[$tmpMd5]);

                   $arr['res'] = true;
               } 
               else
               {
                   // Fail to unlink
                   $arr['msg'] = "Cannot delete this file.";
                   $arr['res'] = false;
               }
           }
           else
           {
               // No permission to write
               $arr['msg'] = "You do not have the permission to delete this file.";
               $arr['res'] = false;
           }
        }
        else
        {
            // File does not exist
            $arr['msg'] = "File does not exist.";
            $arr['res'] = false;
        }
    }
    else if($action == "deleteDir")
    {
        /*
         * Delete a directory
         */

        $dir = $_POST['dir'];

        // Obtain full path 
        $url = USER_DIR.$_SESSION['username'].'/'.$_SESSION['curr-proj'].'/';
        
        // Deletion command
        $cmd = "rm -r ";
        for($i=0;$i<count($dir);$i++)
        {
            $cmd .= escapeshellarg($url.$dir[$i])." ";

            // Unset session for certain files
            $tmpMd5 = md5($url.$dir[$i]);
            if(isset($_SESSION[$tmpMd5]))
                unset($_SESSION[$tmpMd5]);
        }
        $cmd .= "2>&1";
        exec($cmd,$msg,$ret);

        // For debugging purposes
        $arr['cmd'] = $cmd;
        $arr['msg'] = $msg;
        $arr['ret'] = $ret;

        // If operation is successful
        if($ret == 0)
        {
            $arr['dir'] = $dir;
            $arr['res'] = true;
        }
        else
        {
            // Failed to make new directory
            $arr['msg'] = $msg;
            $arr['res'] = false;
        }
    }
    else
    {
        // Project folder does not exist
        $arr['msg'] = "Project does not exist.";
        $arr['res'] = false;
    }
}

echo json_encode($arr);

?>
