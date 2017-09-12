$(function() {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    //var gatewaysock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/room1/&username="+name);
    var gatewaysock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + window.location.pathname);
    //var gatewaysock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + window.location.pathname);

    var global_data = null;
    console.log(ws_scheme + '://' + window.location.host + window.location.pathname)
    gatewaysock.onmessage = function(message) {
        // var data = JSON.parse(message.data);
        //var data = message.data;
        global_data = JSON.parse(message.data);
        //console.log(data);
        console.log(window.location.pathname.trim('/').split('/')[2]);
        // if(data["name"] != window.location.pathname.trim('/').split('/')[2]){
        //     return
        // }

        var gateway = $("#gateway");
        var ele = $('<tr></tr>');
        //console.log(message)
        //alert(data);
        ele.append(
            $("<td></td>").text(new Date().toLocaleTimeString()+':'+new Date().getMilliseconds())
        );
        ele.append(
            $("<td></td>")
        );
        ele.append(
            $("<td></td>").text(message.data)
        );

        gateway.append(ele);

        //gatewaysock.send("I got message!")
    };

    gatewaysock.onopen = function () {
        //$("#gateway").cleanData()
    };

    gatewaysock.onerror = function (err) {
        console.log(err.error);
        // gatewaysock.close();
        if(err.code == 403){
            gatewaysock.close();
        }
    };

    // gatewaysock.onclose = function (e) {
    //     console.log(e)
    // };

    //if (gatewaysock.readyState == WebSocket.OPEN) gatewaysock.onopen();

    $("#gatewayform").on("submit", "go", function(event) {
        var message = {
            // handle: $('#handle').val(),
            // message: $('#message').val(),
            'text': global_data
        }
        gatewaysock.send(JSON.stringify(message));
        $("#message").val('').focus();
        //return false;
    });

    $("#clear").click(function() {
        $("#gateway tbody").html("");
    });



    // $("#gateway").on("button", "clear", function(event) {
    //     $("#btn").click(function() {
    //     $("#gateway tbody").html("");
    // });
    //     return false;
    // });
});