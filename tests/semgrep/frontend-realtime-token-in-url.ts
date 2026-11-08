// ruleid: frontend-realtime-token-in-url
const ws = new WebSocket("wss://x/ws?token=" + token);
// ok: frontend-realtime-token-in-url
const ws2 = new WebSocket("wss://x/ws");
