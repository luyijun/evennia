/*

Evennia websocket webclient (javascript component)

The client is composed of two parts:
 src/server/portal/websocket_client.py - the portal-side component
 this file - the javascript component handling dynamic content

messages sent to the client is one of two modes:
  OOB("func1",args, "func2",args, ...)  - OOB command executions, this will
                                        call unique javascript functions
                                        func1(args), func2(args) etc.
  text - any other text is considered a normal text output in the main output window.

*/

// If on, allows client user to send OOB messages to server by
// prepending with ##OOB{}, for example ##OOB{"echo":[1,2,3,4]}
var OOB_debug = true

//
// Custom OOB functions
// functions defined here can be called by name by the server. For
// example input OOB{"echo":(args),{kwargs}} will trigger a function named
// echo(args, kwargs). The commands the server understands is set by
// settings.OOB_PLUGIN_MODULES

var CMD_NOINPUT = "__noinput_command"

function echo(args, kwargs) {
    // example echo function.
    doShow("out", "ECHO return: " + args) }

function list (args, kwargs) {
    // show in main window
    doShow("out", args) }

function send (args, kwargs) {
    // show in main window. SEND returns kwargs {name:value}.
    for (sendvalue in kwargs) {
        doShow("out", sendvalue + " = " + kwargs[sendvalue]);}
}

function report (args, kwargs) {
    // show in main window. REPORT returns kwargs
    // {attrfieldname:value}
    for (name in kwargs) {
        doShow("out", name + " = " + kwargs[name]) }
}

function repeat (args, kwargs) {
    // called by repeating oob funcs
    doShow("out", args) }

function err (args, kwargs) {
    // display error
    doShow("err", args) }


//
// Webclient code
//

function webclient_init(){
    // called when client is just initializing
    websocket = new WebSocket(wsurl);
    websocket.onopen = function(evt) { onOpen(evt) };
    websocket.onclose = function(evt) { onClose(evt) };
    websocket.onmessage = function(evt) { onMessage(evt) };
    websocket.onerror = function(evt) { onError(evt) };
}

function onOpen(evt) {
    // called when client is first connecting
    $("#connecting").remove(); // remove the "connecting ..." message
    $('#input_box').attr("style", "visibility: hidden;");
	$('#overlayer').attr("style", "visibility: hidden;");
    doShow("sys", "Using websockets - connected to " + wsurl + ".")

    setTimeout(function () {
        $("#numplayers").fadeOut('slow', doSetSizes);
    }, 10000);
}

function onClose(evt) {
    // called when client is closing
    CLIENT_HASH = 0;
    alert("Mud客户端的连接已经断开。");
}

function onMessage(evt) {
    // called when the Evennia is sending data to client
	try {
    	var msg = JSON.parse(evt.data);}
    catch(err) {
    	// not JSON packed - a normal text
        doShow('text', inmsg);
        return;
    }

    if (msg.oob) {
		for (var ind in msg.oob) {
			try {
				window[msg.oob[ind][0]](msg.oob[ind][1], msg.oob[ind][2]) }
			catch(err) {
				doShow("err", "Could not execute js OOB function '" + msg.oob[ind][0] + "(" + msg.oob[ind][1] + msg.oob[ind][2] + ")'") }
		}
    }
    
    if (msg.prompt) {
	    doPrompt("prompt", msg.prompt);
	}
	
	if (msg.clear_links) {
		doClearLinks();
	}

	if (msg.text) {
		if (!msg.type) {
			doShow("text", msg.text);
		}
		else {
			if (msg.type == "" || msg.type == "text") {
				doShow("text", msg.text);
			}
			//else if (msg.type == "input_link") {
			//	doInputLink("text", msg.text);
			//}
			else if (msg.type == "input_text") {
				doInputText("text", msg.text);
			}
			else if (msg.type == "input_password") {
				doInputText("password", msg.text);
			}
			else if (msg.type == "alert") {
				doAlert("text", msg.text);
			}
			else {
				doShow("text", msg.text);
			}
		}
	}

    /*
    var inmsg = evt.data;
    
    if (inmsg.length > 3 && inmsg.substr(0, 3) == "OOB") {
        // dynamically call oob methods, if available
        try {
            var oobarray = JSON.parse(inmsg.slice(3));} // everything after OOB }
        catch(err) {
            // not JSON packed - a normal text
            doShow('out', inmsg);
            return;
        }
        if (typeof oobarray != "undefined") {
            for (var ind in oobarray) {
                try {
                    window[oobarray[ind][0]](oobarray[ind][1], oobarray[ind][2]) }
                catch(err) {
                    doShow("err", "Could not execute js OOB function '" + oobarray[ind][0] + "(" + oobarray[ind][1] + oobarray[ind][2] + ")'") }
            }
        }
    }
    else if (inmsg.length >= 6 && inmsg.substr(0, 6) == "PROMPT") {
        // handle prompt
        var game_prompt = inmsg.slice(6);
        doPrompt("prompt", game_prompt);
    }
    else if (inmsg.length >= 5 && inmsg.substr(0, 5) == "TYPE[") {
    	// handle type
    	var end = inmsg.indexOf("]", 5);
    	if (end != -1) {
    		var type = inmsg.substr(5, end - 5);
    		var msg = inmsg.slice(end + 1);
    		doShow(type, msg);
    	}
    	else {
    		doShow('out', inmsg);
    	}
    }
    else {
        // normal message
        doShow('out', inmsg); }
    */
}

function onError(evt) {
    // called on a server error
    doShow('err', "Connection error trying to access websocket on " + wsurl + ". " + "Contact the admin and/or check settings.WEBSOCKET_CLIENT_URL.");
}

function doSend(){
    // relays data from client to Evennia.
    // If OOB_debug is set, allows OOB test data on the
    // form ##OOB{func:args}
    outmsg = $("#input_text").val();
    history_add(outmsg);
    HISTORY_POS = 0;
    $('#input_text').val("");                     // clear input field
    doCloseInput();

    if (OOB_debug && outmsg.length > 4 && outmsg.substr(0, 5) == "##OOB") {
        if (outmsg == "##OOBUNITTEST") {
           // unittest mode
           doShow("out", "OOB testing mode ...");
           doOOB(JSON.parse('{"ECHO":"Echo test"}'));
           doOOB(JSON.parse('{"LIST":"COMMANDS"}'));
           doOOB(JSON.parse('{"SEND":"CHARACTER_NAME"}'));
           doOOB(JSON.parse('{"REPORT":"TEST"}'));
           doOOB(JSON.parse('{"UNREPORT":"TEST"}'));
           doOOB(JSON.parse('{"REPEAT": 1}'));
           doOOB(JSON.parse('{"UNREPEAT": 1}'));
           doShow("out", "... OOB testing mode done.");
           return
        }
        // test OOB messaging
        try {
            doShow("out", "OOB input: " + outmsg.slice(5));
            if (outmsg.length == 5) {
                doShow("err", "OOB testing syntax: ##OOB{\"cmdname:args, ...}"); }
            else {
                doOOB(JSON.parse(outmsg.slice(5))); } }
        catch(err) {
            doShow("err", err) }
    }
    else {
        // normal output
        websocket.send(outmsg); }
}

function doOOB(oobdict){
    // Send OOB data from client to Evennia.
    // Takes input on form {funcname:[args], funcname: [args], ... }
    var oobmsg = JSON.stringify(oobdict);
    websocket.send("OOB" + oobmsg);
}

function doShow(type, msg){
    // Add msg to the main output window.
    // type gives the class of div to use.
    // The default types are
    // "out" (normal output) or "err" (red error message)
    $('#messagewindow').stop(true);
    $('#messagewindow').scrollTop($('#messagewindow')[0].scrollHeight);
    
    $("#messagewindow").append(
        "<div class='msg "+ type +"'>"+ msg +"</div>");    
    var max = 40;
    while ($("#messagewindow div").size() > max) {
    	$("#messagewindow div:first").remove();
    }
    // scroll message window to bottom
    //$('#messagewindow').scrollTop($('#messagewindow')[0].scrollHeight);
    $('#messagewindow').animate({scrollTop: $('#messagewindow')[0].scrollHeight});
}

function doClearLinks() {
	$('#messagewindow div a').contents().unwrap();
}

function doPrompt(type, msg) {
    // Display prompt
    $('#prompt').replaceWith(
            "<div id='prompt' class='msg "+ type +"'>" + msg + "</div>");
}

function doCancel() {
	websocket.send(CMD_NOINPUT);
	doCloseInput();
}

function doInputText(type, msg) {
    createInputTextDlg();
	$('#input_prompt').html(msg);
	var input = '<div><input type="' + type + '" id="input_text" value="" autocomplete="off"/></div>';
	var button = '<div>\
                    <input type="button" id="button_left" value="取  消" class="btn" onClick="doCancel()"/>\
                    <input type="button" id="button_right" value="确  定" class="btn btn-primary" onClick="doSend()"/>\
              	  </div>'
	$('#input_additional').html(input + button);
    $('#input_text').focus();
    doSetSizes();
}

function doInputCmd(type, msg) {
    createInputCmdDlg();
	$('#input_prompt').html(msg);
	var input = '<div><input type="' + type + '" id="input_text" value="" autocomplete="off"/></div>';
	var button = '<div>\
                    <input type="button" id="button_left" value="取  消" class="btn" onClick="doCloseInput()"/>\
                    <input type="button" id="button_right" value="确  定" class="btn btn-primary" onClick="doSend()"/>\
              	  </div>'
	$('#input_additional').html(input + button);
    $('#input_text').focus();
    doSetSizes();
}

function doInputLink(type, msg) {
    createInputTextDlg();
	$('#input_prompt').html(msg);
	$('#input_additional').html('<p/>');
	doSetSizes();
}

function doAlert(type, msg) {
    createInputTextDlg();
	$('#input_prompt').html(msg);
	var button = '<div><br></div>\
                  <div>\
                    <center>\
                      <input type="button" id="button_center" value="确  定" class="btn btn-primary" onClick="doCloseInput()"/>\
                    </center>\
              	  </div>'
	$('#input_additional').html(button);
	doSetSizes();
}

function doCloseInput() {
    $('#input_box').remove();
	$('#overlayer').remove();
	doSetSizes();
}

function doSetSizes() {
    // Sets the size of the message window
    var win_h = $(window).innerHeight();
    var win_w = $(window).innerWidth();
    var close_h = $('#close_button').outerHeight(true);
    var prom_h = $('#input_prompt').outerHeight(true);
    var add_h = $('#input_additional').outerHeight(true);
    $('#input_box').height(close_h + prom_h + add_h);
    
    var inp_h = $('#input_box').outerHeight(true);
    var inp_w = $('#input_box').outerWidth(true);
    //$("#wrapper").css({'height': win_h - inp_h - 1});
    $('#input_box').css({'left': (win_w - inp_w) / 2, 'top': (win_h - inp_h) / 2});

    if (win_h > 480) {
   	 	var head_h = $('#site-title').outerHeight(true);
   	 	$('#header_bar').show();
    	$('#wrapper').height(win_h - head_h - 6);
    }
    else {
    	$('#header_bar').hide();
    	$('#wrapper').height(win_h - 6);
    }
    
    var middle_h = $('#middlewindow').outerHeight(true);
    var bottom_h = $('#bottomwindow').outerHeight(true);
    $('#messagewindow').height(middle_h - bottom_h - 2);
    
    if (win_w > 960) {
      	$('#middlewindow').width(960);
      	$('#bottomwindow').width(960);
    }
    else {
    	$('#middlewindow').width(win_w);
      	$('#bottomwindow').width(win_w);
    }
}

function createInputTextDlg() {
	var dlg = '<div id="input_box">\
	<div id="close_button" class="clearfix">\
	<input type="image" id="button_close" class="close" src="/static/webclient/img/button_close.png" alt="close" onclick="doCancel()"/>\
	</div>\
	<div id="input_prompt">\
	</div>\
    <div id="input_additional">\
    </div>\
	</div>';
	
	var overlayer = '<div class="overlayer" id="overlayer"></div>';
	
	$("body").prepend(dlg + overlayer);
}

function createInputCmdDlg() {
	var dlg = '<div id="input_box">\
	<div id="close_button" class="clearfix">\
	<input type="image" id="button_close" class="close" src="/static/webclient/img/button_close.png" alt="close" onclick="doCloseInput()"/>\
	</div>\
	<div id="input_prompt">\
	</div>\
    <div id="input_additional">\
    </div>\
	</div>';
	
	var overlayer = '<div class="overlayer" id="overlayer"></div>';
	
	$("body").prepend(dlg + overlayer);
}

//
// Input code
//

// Input history

var HISTORY_MAX_LENGTH = 21
var HISTORY = new Array();
HISTORY[0] = '';
var HISTORY_POS = 0;

function history_step_back() {
    // step backwards in history stack
    HISTORY_POS = Math.min(++HISTORY_POS, HISTORY.length-1);
    return HISTORY[HISTORY.length-1 - HISTORY_POS];
}
function history_step_fwd() {
    // step forward in history stack
    HISTORY_POS = Math.max(--HISTORY_POS, 0);
    return HISTORY[HISTORY.length-1 - HISTORY_POS];
}
function history_add(input) {
    // add an entry to history
    if (input != HISTORY[HISTORY.length-1]) {
        if (HISTORY.length >= HISTORY_MAX_LENGTH) {
            HISTORY.shift(); // kill oldest history entry
        }
        HISTORY[HISTORY.length-1] = input;
        HISTORY[HISTORY.length] = '';
    }
}

// Catching keyboard shortcuts

$.fn.appendCaret = function() {
    /* jQuery extension that will forward the caret to the end of the input, and
       won't harm other elements (although calling this on multiple inputs might
       not have the expected consequences).

       Thanks to
       http://stackoverflow.com/questions/499126/jquery-set-cursor-position-in-text-area
       for the good starting point.  */
    return this.each(function() {
        var range,
            // Index at where to place the caret.
            end,
            self = this;

        if (self.setSelectionRange) {
            // other browsers
            end = self.value.length;
            self.focus();
            // NOTE: Need to delay the caret movement until after the callstack.
            setTimeout(function() {
                self.setSelectionRange(end, end);
            }, 0);
        }
        else if (self.createTextRange) {
            // IE
            end = self.value.length - 1;
            range = self.createTextRange();
            range.collapse(true);
            range.moveEnd('character', end);
            range.moveStart('character', end);
            // NOTE: I haven't tested to see if IE has the same problem as
            // W3C browsers seem to have in this context (needing to fire
            // select after callstack).
            range.select();
        }
    });
};
$.fn.appendCaret = function() {
    /* jQuery extension that will forward the caret to the end of the input, and
       won't harm other elements (although calling this on multiple inputs might
       not have the expected consequences).

       Thanks to
       http://stackoverflow.com/questions/499126/jquery-set-cursor-position-in-text-area
       for the good starting point.  */
    return this.each(function() {
        var range,
            // Index at where to place the caret.
            end,
            self = this;

        if (self.setSelectionRange) {
            // other browsers
            end = self.value.length;
            self.focus();
            // NOTE: Need to delay the caret movement until after the callstack.
            setTimeout(function() {
                self.setSelectionRange(end, end);
            }, 0);
        }
        else if (self.createTextRange) {
            // IE
            end = self.value.length - 1;
            range = self.createTextRange();
            range.collapse(true);
            range.moveEnd('character', end);
            range.moveStart('character', end);
            // NOTE: I haven't tested to see if IE has the same problem as
            // W3C browsers seem to have in this context (needing to fire
            // select after callstack).
            range.select();
        }
    });
};

// Input jQuery callbacks

$(document).keydown( function(event) {
    // Get the pressed key (normalized by jQuery)
    var code = event.which,
        inputField = $("#input_text");

    // always focus input field no matter which key is pressed
    inputField.focus();

    // Special keys recognized by client

    //doShow("out", "key code pressed: " + code); // debug

    if (code == 13) { // Enter Key
        doSend();
        event.preventDefault();
    }
    else {
        if (code == 38) { // arrow up 38
            inputField.val(history_step_back()).appendCaret();
        }
        else if (code == 40) { // arrow down 40
            inputField.val(history_step_fwd()).appendCaret();
        }
    }
});

// handler to avoid double-clicks until the ajax request finishes
//$("#inputsend").one("click", webclient_input)

// Callback function - called when the browser window resizes
$(window).resize(doSetSizes);

// Callback function - called when page is closed or moved away from.
//$(window).bind("beforeunload", webclient_close);
//
// Callback function - called when page has finished loading (kicks the client into gear)
$(document).ready(function(){
    // remove the "no javascript" warning, since we obviously have javascript
    $('#noscript').remove();
    // set sizes of elements and reposition them
    doSetSizes();
    // a small timeout to stop 'loading' indicator in Chrome
    setTimeout(function () {
        webclient_init();
    }, 500);
    // set an idle timer to avoid proxy servers to time out on us (every 3 minutes)
    setInterval(function() {
        websocket.send("idle");
    }, 60000*3);
});
