import http from "http";
import WebSocket, { WebSocketServer } from "ws";
import { URL } from "url";

export function setupWebSocketHandler(
  server: http.Server,
  orchestratorWsUrl: string,
): void {
  const wss = new WebSocketServer({ noServer: true });

  server.on("upgrade", (request, socket, head) => {
    const pathname = new URL(request.url ?? "", "http://localhost").pathname;
    const match = pathname.match(
      /^\/api\/v1\/techpacks\/([^/]+)\/stream$/,
    );

    if (!match) {
      socket.destroy();
      return;
    }

    wss.handleUpgrade(request, socket, head, (ws) => {
      wss.emit("connection", ws, request, match[1]);
    });
  });

  wss.on("connection", (clientWs: WebSocket, _request: http.IncomingMessage, techpackId: string) => {
    const orchestratorPath = `/api/v1/techpacks/${techpackId}/stream`;
    const wsUrl = `${orchestratorWsUrl}${orchestratorPath}`;

    let orchestratorWs: WebSocket;
    try {
      orchestratorWs = new WebSocket(wsUrl);
    } catch (err) {
      clientWs.send(JSON.stringify({ error: "Failed to connect to orchestrator" }));
      clientWs.close();
      return;
    }

    orchestratorWs.on("open", () => {
      // Relay: orchestrator → client
      orchestratorWs.on("message", (data) => {
        if (clientWs.readyState === WebSocket.OPEN) {
          clientWs.send(data.toString());
        }
      });
    });

    orchestratorWs.on("close", () => {
      if (clientWs.readyState === WebSocket.OPEN) {
        clientWs.close();
      }
    });

    orchestratorWs.on("error", (err) => {
      if (clientWs.readyState === WebSocket.OPEN) {
        clientWs.send(
          JSON.stringify({ error: `Orchestrator connection failed: ${err.message}` }),
        );
        clientWs.close();
      }
    });

    // If client disconnects, close orchestrator connection
    clientWs.on("close", () => {
      if (orchestratorWs.readyState === WebSocket.OPEN) {
        orchestratorWs.close();
      }
    });
  });
}
