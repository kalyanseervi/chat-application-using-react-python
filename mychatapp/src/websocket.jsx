export const createWebSocketConnection = (userId, roomId, token) => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${userId}/${roomId}?token=${token}`);
  
    ws.onopen = () => console.log("Connected to WebSocket");
    ws.onclose = () => console.log("Disconnected from WebSocket");
    ws.onerror = (err) => console.error("WebSocket Error", err);
  
    return ws;
  };
  