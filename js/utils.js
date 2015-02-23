/*
 * Output to Console
 */
function writeToConsole(msg, type)
{
  
    type = typeof type !== 'undefined' ? type : "normal";
    var resWin1 = $('#console1');
    var resWin2 = $('#console2');
    var resWin3 = $('#console3');

    if(type == "normal")
    {
        // Current time stamp
        var now = new Date();
        var timestamp = now.getHours()+":"+now.getMinutes()+":"+now.getSeconds()+":"+now.getMilliseconds();

        resWin1.append("<p class=\"normal\">["+timestamp+"]\t"+msg+"</p>");
        resWin2.append("<p class=\"normal\">["+timestamp+"]\t"+msg+"</p>");
        resWin3.append("<p class=\"normal\">["+timestamp+"]\t"+msg+"</p>");
    }
    else
    {
        if(msg instanceof Array)
        {
            for(var i=0;i<msg.length;i++)
            {
                if(msg[i].trim().length > 0)
                    resWin1.append("<p class=\"text-"+type+" bold\">"+msg[i]+"</p>");
                    resWin2.append("<p class=\"text-"+type+" bold\">"+msg[i]+"</p>");
                    resWin3.append("<p class=\"text-"+type+" bold\">"+msg[i]+"</p>");
            }
        }
        else
        {
            resWin1.append("<p class=\"text-"+type+" bold\">"+msg+"</p>");
            resWin2.append("<p class=\"text-"+type+" bold\">"+msg+"</p>");
            resWin3.append("<p class=\"text-"+type+" bold\">"+msg+"</p>");
        }
    }
    resWin1.scrollTop(resWin1[0].scrollHeight);
    resWin2.scrollTop(resWin2[0].scrollHeight);
    resWin3.scrollTop(resWin3[0].scrollHeight);
}

/* 
 * Function to move console to position number
 */
function showConsole(console_id){
    switch(console_id){
        case 1:
            $('#console-div1').show();
	    $('#console1').height(330);
            $('#console-div2').hide();
            $('#console-div3').hide();
        break;
        case 2:
            $('#console-div1').hide();
            $('#console-div2').show();
	    $('#console2').height(100);
            $('#console-div3').hide();
        break;
        case 3:
            $('#console-div1').hide();
            $('#console-div2').hide();
            $('#console-div3').show();
	    $('#console3').height(300);
        break;
        default:
    }
}
