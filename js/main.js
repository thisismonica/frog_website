/*
 * Global variables
 * -------------------------------------------------
 */
var editor; // Code mirror object
var editChanged = false; // Flag indicating change of content in the code editor
var currentProj = ''; // Current project name
var isRunning = true; // Indicate if there is a program running

/*
 * Document ready
 * -------------------------------------------------
 */
$(document).ready(function() {

    // Initialize code window
    var helloWordCode = "#include <iostream>\n\nint main()\n{\n\tstd::cout << \"Hello World!\" << std::endl;\n\treturn 0;\n}";
    var codeWindow = document.getElementById("code");
    codeWindow.innerHTML = helloWordCode;

    // Code mirror
    editor = CodeMirror.fromTextArea(codeWindow, {
        lineNumbers: true,
        styleActiveLine: true,
        matchBrackets: true,
        theme: "elegant",
        mode: "text/x-csrc"
    });


    // TEST: marker function of code mirror
    /*
    markerBug = editor.doc.markText({line:0,ch:0},{line:1,ch:1},{className:"bug"});
    markerWarning = editor.doc.markText({line:4,ch:0},{line:5,ch:0},{className:"warning"});
    */
    
    // Fire when editor content changed
    editor.on("change",function(cm){
        editChanged = true;
    });

    // Get project list
    //getProjectList();

    // Tool tips on buttons
    //$('.btn').tooltip();
    
    // Idle timeout
    // start the idle timer plugin
    /*$.idleTimeout('#logout_popup_open', '#btn-continue-logout', {
        idleAfter: 300,
        //pollingInterval: 2,
        //keepAliveURL: 'keepalive.php',
        //serverResponseEquals: 'OK',
        warningLength: 60,
        onTimeout: function(){
            window.location = "php/signout.php";
        },
        onIdle: function(){
            $(this).trigger("click");
        }
    });*/

});

/*
 * Project operation
 * -------------------------------------------------
 */

function getProjectList()
/* 
 * Get a complete list of projects under user folder
 * Called when document is ready
 */
{
    // Open loading
    openBlock();

    $.ajax({
        url: "php/project.php",
        type: "POST",
        data: { action: "get" },
        success: function(msg)
        {
            // Translate JSON format
            var json="";
            eval('json='+msg+';');

            // Set current project to global variable
            currentProj = json['curr-proj'];

            // If successful
            if(json['res'])
            {
                var content = '';
                if(json['dir'].length <= 0)
                {
                    // If there is no project at all 
                    content = '<a href="#" class="list-group-item">None</a>'; 
                }
                else
                {
                    // Display in list group
                    for(var i=0;i<json['dir'].length;i++)
                    {
                        content += '<a href="#" id="'+md5(json['dir'][i]+'sidebar')+'" class="list-group-item" onClick="openProject(\''+json['dir'][i]+'\');" >'+json['dir'][i]+'</a>'; 
                    }
                }

                // Append to sidebar
                $('#sidebar-project-list').append(content);
            }
            else
            {
               // Display error message
                writeToResultWindow("Fail to get project list.");
                writeToResultWindow(json['msg'],"danger");
            }

            // Close loading
            closeBlock();
            
        },
        error: function(xhRequest, ErrorText, thrownError)
        {
            // Close loading
            closeBlock();

            alert(xhRequest.status+": "+thrownError);
        }
    });
}

function selectProject(param)
/* 
 * Show project list modal that contains a complete list of projects 
 * Called when user clicks on [Open Project] or [Delete project] from top menu bar
 */
{
    // Check for unsaved files 
    if(!checkForUnsaved()) return;

    // Open loading
    openBlock();
    
    $.ajax({
        url: "php/project.php",
        type: "POST",
        data: { action: "get" },
        success: function(msg)
        {
           // Translate JSON format
            var json="";
            eval('json='+msg+';');
            
            // If successful 
            if(json['res'])
            {
                if(json['dir'].length <= 0)
                {
                    // If there is no projects
                    writeToResultWindow("No project uploaded.","warning");
                }
                else
                {
                    // Display in list group
                    var content = '';
                    for(var i=0;i<json['dir'].length;i++)
                    {
                        if(param == 'open')
                            content += '<a href="#" id="'+md5(json['dir'][i]+'modal')+'" class="list-group-item" onClick="openProject(\''+json['dir'][i]+'\');">'+json['dir'][i]+'</a>'; 
                        else
                            content += '<a href="#" id="'+md5(json['dir'][i]+'modal')+'" class="list-group-item" onClick="deleteProject(\''+json['dir'][i]+'\');">'+json['dir'][i]+'</a>'; 
                    }

                    // Append to popup overlay div and trigger click function
                    $('#project-list').html(content);
                    $('#project_popup_open').click();
                }
            }
            else
            {
                // Display error message
                writeToResultWindow("Fail to open project.");
                writeToResultWindow(json['msg'],"danger");
            }

            // Close loading
            closeBlock();
            
        },
        error: function(xhRequest, ErrorText, thrownError)
        {
            // Close loading
            closeBlock();

            alert(xhRequest.status+": "+thrownError);
        }
    });
}

function openProject(projName)
/* 
 * Open a project 
 * Called when user clicks on the project list sidebar or from project list modal
 */
{
    // Check if there is already a project opened
    if(currentProj != '')
    {
        // Check if current project is the same one
        if(currentProj == projName)
            return;

        // Pop up confirmation
        if(!confirm("You have already opened a project. Do you want to close it and open a new one?"))
            return;
    }

    // Close popup
    $('#project_popup_close').click();

    // Open loading
    openBlock();

    $.ajax({
        url: "php/project.php",
        type: "POST",
        data: { action: "select", name : projName },
        success: function(msg)
        {
            // Translate JSON format
            var json="";
            eval('json='+msg+';');

            // If successful
            if(json['res'])
            {
                // Reload
                location.reload();
            }
            else
            {
                // Display error message
                writeToResultWindow("Fail to open project","danger");
                writeToResultWindow(json['msg'],"danger");
            }

            // Close loading
            closeBlock();
        },
        error: function(xhRequest, ErrorText, thrownError)
        {
            // Close loading
            closeBlock();

            alert(xhRequest.status+": "+thrownError);
        }
    });

}

function closeProject()
/* 
 * Close a project
 * Called when user clicks on the [Close Project] on the top menu bar
 */
{
    // Check for unsaved files
    if(!checkForUnsaved()) return;
    
    // Open loading
    openBlock();

    $.ajax({
        url: "php/project.php",
        type: "POST",
        data: { action: "close" },
        success: function(msg)
        {
            // Translate JSON format
            var json="";
            eval('json='+msg+';');

            // If successful
            if(json['res'])
            {
                // Reload page
                location.reload();
            }
            else
            {
                // Display error message
                writeToResultWindow("Fail to close project.");
                writeToResultWindow(json['msg'],"danger");
            }

            // Close loading
            closeBlock();
        },
        error: function(xhRequest, ErrorText, thrownError)
        {
            // Close loading
            closeBlock();

            alert(xhRequest.status+": "+thrownError);
        }
    });
}

function deleteProject(projName)
/* 
 * Delete a project
 * Called when user wants to delete a project from the project list modal 
 */
{
    // Open loading
    openBlock();

    // Close Popup Overlay
    $('#project_popup_close').click();

    $.ajax({
        url: "php/project.php",
        type: "POST",
        data: { action: "delete", name : projName },
        success: function(msg)
        {
            // Translate JSON format
            var json="";
            eval('json='+msg+';');

            // If successful
            if(json['res'])
            {
                // Reload page
                location.reload();
            }
            else
            {
                // Display error message
                writeToResultWindow("Fail to delete project");
                writeToResultWindow(json['msg'],"danger");
            }

            // Close loading
            closeBlock();
        },
        error: function(xhRequest, ErrorText, thrownError)
        {
            // Close loading
            closeBlock();

            alert(xhRequest.status+": "+thrownError);
        }
    });

}

function importProject()
/* 
 * Import a project from local destination 
 * Called when user clicks on [Import Project] in the top menu bar
 */
{
    // Check for unsaved tasks
    if(!checkForUnsaved()) return;
    
    // Pop up a local file window
    $("#import-project").click();
}

/*
 * File
 * -------------------------------------------------
 */

function readFile(filepath, filename)
/* 
 * Read a file
 * Called when user clicks on a file in the file tree structure
 */
{
    // Check for unsaved tasks
    if(!checkForUnsaved()) return;

    // Open loading
    openBlock();
    
    $.ajax({
        url: "php/file.php",
        type: "POST",
        data: { action: "read", filepath: filepath },
        success: function(msg)
        {
            // Translate JSON format
            var json="";
            eval('json='+msg+';');
            
            // If successful
            if(json['res'])
            {
                if(json['content'] == null)
                {
                    // Null content 
                    writeToResultWindow("Fail to read "+filename);
                    writeToResultWindow("Content encoding is invalid.","danger");
                }
                else
                {
                    // Display file content
                    editor.setValue(json['content']);
                    editChanged = false; // reset change flag

                    // Set file metadata
                    $('#file-detail').html(filename);
                    $('#file-detail').attr('rel',filepath);

                    // Show option for different types of files 
                    // First reset every button
                    $('#btn-extract').addClass("hide");
                    $('#btn-prepare').addClass("hide");
                    $('#btn-compile').addClass("hide");
                    $('#btn-include').addClass("hide");
                    $('#btn-link').addClass("hide");
                    $('#btn-run').addClass("hide");

                    var ext = getExt(filepath); // Get file extension
                    switch(ext)
                    {
                        case "c": // Display Prepare
                            $('#btn-prepare').removeClass("hide");
                            break;
                        case "cmp": // Display Compile & Include
                            $('#btn-compile').removeClass("hide");
                            $('#btn-include').removeClass("hide");
                            break;
                        case "blee": // Display Run
                            $('#btn-run').removeClass("hide");
                            $('#btn-link').removeClass("hide");
                            break;
                        case "ktest": // Display Extract
                            $('#btn-extract').removeClass("hide");
                            break;
                        default:
                            break;
                    }
                }
            }
            else
            {
                // Display error message
                writeToResultWindow("Fail to read "+filename);
                writeToResultWindow(json['msg'],"danger");
            }

            // Close loading
            closeBlock();

        },
        error: function(xhRequest, ErrorText, thrownError)
        {
            // Close loading
            closeBlock();

            alert(xhRequest.status+": "+thrownError);
        }
    });

}

function saveFile()
/*
 * Save a file
 * Called when user clicks on the [Save] from top menu bar or from the code editor
 */
{
    // Obtain file path, name and content
    var content = editor.getValue();
    var filepath = $('#file-detail').attr('rel');
    var filename = $('#file-detail').html();

    // Check if there is no open file in the editor
    if(filepath == "")
    {
        writeToResultWindow("No file selected.");
        writeToResultWindow("Click on the file in the right sidebar.","info");
        return;
    }

    // Open loading
    openBlock();

    $.ajax({
        url: "php/file.php",
        type: "POST",
        data: { action: "save", content: content, filepath: filepath },
        success: function(msg)
        {
            // Translate JSON format
            var json="";
            eval('json='+msg+';');
            
            // If successful
            if(json['res'])
            {
                // Tell user it's saved
                writeToResultWindow(filename+' saved.');

                // Reset flag
                editChanged = false;
            }
            else
            {
                // Display error message
                writeToResultWindow('Fail to save '+filename);
                writeToResultWindow(json['msg'],"danger");
            }

            // Close loading
            closeBlock();

        },
        error: function(xhRequest, ErrorText, thrownError)
        {
            // Close loading
            closeBlock();

            alert(xhRequest.status+": "+thrownError);
        }
    });
}

function deleteFile()
/*
 * Delete a file
 * Called when user clicks on the [Delete] from the code editor
 */
{
    // Obtain file path and name
    var filepath = $('#file-detail').attr('rel');
    var filename = $('#file-detail').html();

    // Check if there is an active file
    if(filepath == "")
    {
        writeToResultWindow("No file selected.");
        writeToResultWindow("Click on the file in the right sidebar.","info");
        return;
    }

    // Confirm before deleting the file
    if(!confirm("Are you sure to delete this file?")) return;

    // Open loading
    openBlock();

    $.ajax({
        url: "php/file.php",
        type: "POST",
        data: { action: "delete", filepath: filepath },
        success: function(msg)
        {
            // Translate JSON format
            var json="";
            eval('json='+msg+';');
            
            // If successful
            if(json['res'])
            {
                // Close file
                closeFile();

                // Recollapse
                recollapse(filepath);

                // Tell user it's deleted
                writeToResultWindow(filename+' deleted.');
            }
            else
            {
                // Display error message
                writeToResultWindow('Fail to delete '+filename);
                writeToResultWindow(json['msg'],"danger");
            }

            // Close loading
            closeBlock();
            
        },
        error: function(xhRequest, ErrorText, thrownError)
        {
            // Close loading
            closeBlock();

            alert(xhRequest.status+": "+thrownError);
        }
    });
}

function deleteDir()
/*
 * Delete a directory or file checked in the sidebar
 * Called when user click on [Delete] fro mthe top menu bar
 */
{
    // Obtain selected function list
    var n = $("li input:checkbox:checked").length; 
    var dir = $("li input:checkbox:checked").map(function(){return $(this).val();}).get(); 

    // Check if at least one directory or file is checked
    if(n <= 0)
    {
        alert("You have to select one directory or file in the file tree");
        return;
    }

    // Open loading
    openBlock();

    $.ajax({
        url: "php/file.php",
        type: "POST",
        data: { action: "deleteDir", dir: dir },
        success: function(msg)
        {
            // Translate JSON format
            var json="";
            eval('json='+msg+';');
            
            // If successful
            if(json['res'])
            {
                var filepath = $('#file-detail').attr('rel');
                for(var i=0;i<json['dir'].length;i++)
                {
                    // If current file is deleted, close it
                    if(json['dir'][i] == filepath)
                        closeFile();

                    // Tell user it's deleted
                    writeToResultWindow(json['dir'][i]+' deleted.');
                }

                // Recollapse root directory
                recollapse(currentProj+'/');
            }
            else
            {
                // Display error message
                writeToResultWindow('Fail to delete.');
                writeToResultWindow(json['msg'],"danger");
            }

            // Close loading
            closeBlock();
            
        },
        error: function(xhRequest, ErrorText, thrownError)
        {
            // Close loading
            closeBlock();

            alert(xhRequest.status+": "+thrownError);
        }
    });

}

function closeFile()
/*
 * Close a file by inserting hello world sample code
 * Called after user has deleted a file
 */
{
    // Hello world sample code
    var helloWordCode = "#include <iostream>\n\nint main()\n{\n\tstd::cout << \"Hello World!\" << std::endl;\n\treturn 0;\n}";

    // Update code editor
    editor.setValue(helloWordCode);
    editChanged = false;

    // Set file details
    $('#file-detail').html('');
    $('#file-detail').attr('rel','');

    // Hide all buttons
    $('#btn-extract').addClass("hide");
    $('#btn-prepare').addClass("hide");
    $('#btn-include').addClass("hide");
    $('#btn-link').addClass("hide");
    $('#btn-compile').addClass("hide");
    $('#btn-run').addClass("hide");
}
