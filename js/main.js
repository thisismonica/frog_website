/*
 * Global variables
 * -------------------------------------------------
 */
var editor; // Code mirror object
var editChanged = false; // Flag indicating change of content in the code editor
var currentProj = ''; // Current project name
var isRunning = true; // Indicate if there is a program running
var allowedSourceCode = "c,cpp"; //Allowed source code type for testing

/*
 * Document ready
 * -------------------------------------------------
 */
$(document).ready(function() {

    // Initialize file uploader
    $("#file-uploader").uploadFile({
        url:"server/uploader.php",
        allowedTypes: allowedSourceCode,
        fileName: "source_code",
        multiple: false,
        //uploadButtonClass:"ajax-file-upload-green",
        uploadButtonClass:"btn btn-success",
        dragDrop: false,
        showStatusAfterSuccess: false,
        showProgress: false,
        showAbort: false,
        maxFileSize: 1024000,
        onSuccess: function(files,data,xhr){
            // Format JSON data from server
            var json="";
            eval('json='+data+';');

            // Display code when upload success
            if(json['success']){
                if(json['content'] == null)
                {
                    // Null content 
                    writeToConsole("Fail to read ", "warning");
                    writeToConsole("Content encoding is invalid.","danger");
                }
                else
                { 
                    $("#code-area").hide("slow"); 
                    $("#code-area").show("clip"); 
                    writeToConsole("Upload file: "+files, "normal");

                    // Display file content
                    editor.setValue(json['content']);
                    editChanged = false; // reset change flag

                    // Show step2 options
                    $("#extract-functions").show("slow");
                    window.location.href = "#step2";
                }
            }
            else{
                // Display error message
                writeToConsole("Fail to read ");
                writeToConsole(json['error'],"danger");
            }
        }
    });

    // Initialize code window
    var helloWordCode = "#include <iostream>\n\nint main()\n{\n\tstd::cout << \"Hello Frog!\";\n}";
    var codeWindow = document.getElementById("code");
    codeWindow.innerHTML = helloWordCode;
    editor = CodeMirror.fromTextArea(codeWindow, {
        lineNumbers: true,
        styleActiveLine: true,
        matchBrackets: true,
        theme: "elegant",
        mode: "text/x-csrc"
    });

    // Fire when editor content changed
    editor.on("change",function(cm){
        editChanged = true;
    });


    // TEST: marker function of code mirror
    /*
    markerBug = editor.doc.markText({line:0,ch:0},{line:1,ch:1},{className:"bug"});
    markerWarning = editor.doc.markText({line:4,ch:0},{line:5,ch:0},{className:"warning"});
    */
    
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
 * Save & Extract functions from source code
 * -------------------------------------------------
 */
function extractFunctions(){
    // Save file from editor
    var source_code = editor.getValue();

    $.ajax({
        url: 'server/save.php',
        type: "POST",
        data: {content: source_code},
        success: function(msg){
            var json="";
            eval('json='+msg+';');
            if(json['success']){
                writeToConsole('Source code saved','normal');
                call_extract_function_script();
            }else{
                writeToConsole('Unable to save source code','warning');
            }
        },
        error: function(xhRequest, ErrorText, thrownError)
        {   
            writeToConsole(xhRequest.status+": "+thrownError, 'danger');
        }   
    });
}

/*
 * Call Python Script to extract functions
 * -------------------------------------------------
 */
function call_extract_function_script(){
     $.ajax({
        url: 'server/extract_functions.php',
        type: "POST", 
        success: function(msg){

            // Parsing json data from server
            var json="";
            eval('json='+msg+';');

            if(json['success']){
                if( $('#function-list').is(":visible")){
                    $('#function-list').hide("slow");
                    $('#function-list').show("slow");        
                }else{
                    $('#function-list').show("slow");    
                }
                        
                clearTable();
                drawTable(json['content']);
                window.location.href = "#step3";              
            }else{
                writeToConsole(json['msg'], 'danger');
            }
        },
        error: function(xhRequest, ErrorText, thrownError)
        {   
            writeToConsole(xhRequest.status+": "+thrownError, 'danger');
        }   
    });
}

/*
 * Function to draw/clear function list table
 * -------------------------------------------------
 */
function clearTable(){
     $("#function-list-table tbody tr").remove();
}
function drawTable(data) {
    var rows = [];

    for (var i = 0; i < data.length; i++) {
        rows.push(drawRow(data[i]));
    }

    $("#function-list-table").append(rows);
}
function drawRow(rowData) {
    var row = $("<tr />");
    var checked = "";
    //row.append($("<td>" + rowData.id + "</td>"));
    row.append($("<td>" + rowData.function + "</td>"));
    if(rowData.id == 0){
        checked = " checked ";
    }
    row.append($("<td><input type=\"radio\" name=\"function_id\" value="+rowData.id+" aria-label=\"...\""+checked+"> </td>") ); 
    return row;
}
/*
 * Function to create test file based on selected function
 * ---------------------------------------------------------
 */
function createTestFile(id){
    var fun_id = id;
    $.ajax({
        url: 'server/create_test_file.php',
        type: "POST", 
        data: {function_id: fun_id},
        success: function(msg){
            // Format JSON data from server
            var json="";
            eval('json='+msg+';');
            // Display code when upload success
            if(json['success']){
                if(json['content'] == null)
                {
                    // Null content 
                    writeToConsole("Fail to read instrumented test file ", "warning");
                }
                else
                { 
                    $("#code-area").hide("slow");  
                    $("#code-area").show("clip");
                    writeToConsole("Displayed instrumented test file", "normal");

                    // Display file content
                    editor.setValue(json['content']);
                    editChanged = false; // reset change flag
                }
            }
            else{
                // Display error message
                writeToConsole("Fail to read test file ");
                writeToConsole(json['msg'],"danger");
            }
        },
        error: function(xhRequest, ErrorText, thrownError)
        {   
            writeToConsole(xhRequest.status+": "+thrownError, 'danger');
        }   
    });
}
