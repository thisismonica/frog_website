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