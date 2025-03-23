const socket = new WebSocket("wss://qxp1ga8zl7.execute-api.us-east-2.amazonaws.com/test/");

socket.onopen = function() {
    console.log("WebSocket connection opened.");
    // socket.send(JSON.stringify({ action: "sendMessage", message: "Hello from client!" }));
};

socket.onmessage = function(event) {
    console.log("Message from server:", event.data);
};

socket.onclose = function() {
    console.log("WebSocket connection closed.");
};

socket.onerror = function(error) {
    console.error("WebSocket error:", error);
};
