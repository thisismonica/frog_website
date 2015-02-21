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
                    showConsole(1);
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
   
    // Load code editor from saved user data
    loadCodeEditor();

    // Fire when editor content changed
    editor.on("change",function(cm){
        editChanged = true;
    });

    // Show console at the top
    showConsole(1);

    // TEST: marker function of code mirror
    /*
    markerBug = editor.doc.markText({line:0,ch:0},{line:1,ch:1},{className:"bug"});
    markerWarning = editor.doc.markText({line:4,ch:0},{line:5,ch:0},{className:"warning"});
    */
    
});

/*
 * Called when button 'extract funciton' clicked. 
 * Save & Extract functions from source code
 * Call clearKLEEData() if succeed
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

	        // Clear old KLEE data
	        clearKLEEData();

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
 * Clear old KLEE data
 * Called after extract funtion succeed.
 * -------------------------------------------------
 */
function clearKLEEData(){
    $.ajax({
        url: 'server/clearKLEEData.php',
        type: "POST",
        success: function(msg){
            var json="";
            eval('json='+msg+';');
            if(json['success']){
		//writeToConsole(json['msg']);
                //writeToConsole('Old KLEE Data Cleared','normal');
            }else{
	        writeToConsole(json['msg'],'warning');
                writeToConsole('Unable to clear KLEE Data','warning');
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
 * Called after source code saved
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
                // Move console and page position
                showConsole(2); 
                window.location.href = "#step3"; 
                      
                clearTable();
                drawTable(json['content']);                      
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
 * To load source code
 * called onDocumentReady()
 * ---------------------------------------------------------
 */
function loadCodeEditor(){
    // Request for source code saved
    $.ajax({
        url: 'server/load_file.php',
        type: "POST", 
        success: function(msg){
            // Format JSON data from server
            var json="";
            eval('json='+msg+';');

            // Display code if upload success
            if(json['success']){
                if(json['content'] == null)
                {
                    // Null content 
                    writeToConsole("Fail to read source code file ", "warning");
                }
                else
                { 
                    // Display file content
                    editor.setValue(json['content']);
                    editChanged = false;
                }
            }
            else{
		if(!json['unset']){

			// Display error message
			writeToConsole("Fail to read test file ");
			writeToConsole(json['msg'],"danger");
		    }
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
 * Called by extract functions
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
 * Called when button 'generate test suite' clicked
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
                    writeToConsole("Displayed instrumented test file", "normal");

                    // Display file content
                    editor.setValue(json['content']);
		    editChanged = false;

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

/*
 * Function to compile test file based on selected function
 * run KLEE if compile succeed
 * ---------------------------------------------------------
 */
function compile(id){
    var fun_id = id;
    $.ajax({
        url: 'server/compile.php',
        type: "POST", 
        data: {function_id: fun_id},
        success: function(msg){
            // Format JSON data from server
            var json="";
            eval('json='+msg+';');

            if(json['success']){
                writeToConsole(json['msg']);
		writeToConsole("Running KLEE...");
		runKLEE(fun_id);
                //replayTestCases();
            }
            else{
                // Display error message
                writeToConsole(json['msg'],"danger");
            }
        },
        error: function(xhRequest, ErrorText, thrownError)
        {   
            writeToConsole(xhRequest.status+": "+thrownError, 'danger');
        }   
    });
}

/*
 * Function to run KLEE based on selected function
 * called after compile succeed
 * ---------------------------------------------------------
 */
function runKLEE(id){
    var fun_id = id;
    $.ajax({
        url: 'server/run_klee.php',
        type: "POST", 
        data: {function_id: fun_id},
        success: function(msg){
		var json="";
		eval('json='+msg+';');

		if(json['success']){
			writeToConsole(json['msg']);
			writeToConsole("Replaying test cases...");
			replayTestCases(id);			
		}else{
			writeToConsole(json['msg'],"danger");
		}
        },
        error: function(xhRequest, ErrorText, thrownError)
        {   
            writeToConsole(xhRequest.status+": "+thrownError, 'danger');
        }   
    });
}

/* 
 * Function to replay test cases, called when run KLEE succeed
 * ---------------------------------------------------------
 */
function replayTestCases(id){
    var fun_id = id;
    $.ajax({
        url: 'server/replay.php',
        type: "POST", 
        data: {function_id: fun_id},
        success: function(msg){

		var json="";
		eval('json='+msg+';');

		if(json['success']){
		    writeToConsole(json['msg']);

		    clearTestSuiteTable();
		    drawTestSuiteTable( json['test_output']);

		     // Show result and move console
                    if( $('#test-suite').is(":visible") ){
                        $('#test-suite').hide("slow");
                        $('#test-suite').show("slow");          
                    }else{
                        $('#test-suite').show("slow");    
                    }
                    showConsole(3);

		}else{
			writeToConsole(json['msg'],"danger");
		}
		$('#generate-test-button').button('reset');
        },

        error: function(xhRequest, ErrorText, thrownError)
        {   
            writeToConsole(xhRequest.status+": "+thrownError, 'danger');
	        $('#generate-test-button').button('reset');
        }   
    });
}

/*
 * Function to draw/clear test suit table
 * called after repaly succeed
 * -------------------------------------------------
 */
function clearTestSuiteTable(){
     $("#test-suite-table tbody tr").remove();
}

function drawTestSuiteTable(data) {
    var rows = [];

    for (var i = 0; i < data.length; i++) {
        rows.push(drawTestSuiteRow(data[i], i));
    }

    $("#test-suite-table").append(rows);
}

function drawTestSuiteRow(rowData, rowid) {
    var id = rowid.toString();
    var test_str = "testcase";
    id = test_str.concat(id);
    
    var row = $("<tr />");
    var checked = "";
    row.append($("<td>" + rowData.arg+ "</td>"));
    row.append($("<td>"+rowData.output+"</td>"));

row.append($(
"<td class=\"col-md-3\"><div class=\"btn-group\" data-toggle=\"buttons\"><label class=\"btn btn-primary active\"><input type=\"radio\" name="+id+ " value=\"True\" checked>Pass</label><label class=\"btn btn-primary\"><input type= \"radio\" name="+id+" value=\"False\">Fail</lable></div></td>"));
	
    return row;
}
