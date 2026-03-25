import http from "http";
import express from "express";
import WebSocket, { WebSocketServer } from "ws";
import { setupWebSocketHandler } from "../../src/ws/techpackStream";

// Helper: create a mock orchestrator WS server
function createMockOrchestrator(
  port: number,
  messages: object[],
): Promise<http.Server> {
  return new Promise((resolve) => {
    const server = http.createServer();
    const wss = new WebSocketServer({ server });
    wss.on("connection", (ws) => {
      for (const msg of messages) {
        ws.send(JSON.stringify(msg));
      }
      ws.send(JSON.stringify({ event: "done", status: "completed" }));
      ws.close();
    });
    server.listen(port, () => resolve(server));
  });
}

function waitForMessages(ws: WebSocket, count: number): Promise<object[]> {
  return new Promise((resolve) => {
    const received: object[] = [];
    ws.on("message", (data) => {
      received.push(JSON.parse(data.toString()));
      if (received.length >= count) resolve(received);
    });
  });
}

describe("WebSocket techpack stream relay", () => {
  let gatewayServer: http.Server;
  let orchestratorServer: http.Server;
  let gatewayPort: number;
  const orchestratorPort = 19876;

  afterEach((done) => {
    const servers = [gatewayServer, orchestratorServer].filter(Boolean);
    let closed = 0;
    if (servers.length === 0) return done();
    servers.forEach((s) =>
      s.close(() => {
        closed++;
        if (closed === servers.length) done();
      }),
    );
  });

  it("relays messages from orchestrator to client", async () => {
    const agentMessages = [
      { agent: "brief_analyzer", status: "running", message: "Parsing..." },
      { agent: "brief_analyzer", status: "completed", data: { garment_type: "top" } },
    ];

    orchestratorServer = await createMockOrchestrator(
      orchestratorPort,
      agentMessages,
    );

    const app = express();
    gatewayServer = http.createServer(app);
    setupWebSocketHandler(gatewayServer, `ws://localhost:${orchestratorPort}`);

    await new Promise<void>((resolve) =>
      gatewayServer.listen(0, () => resolve()),
    );
    gatewayPort = (gatewayServer.address() as any).port;

    const client = new WebSocket(
      `ws://localhost:${gatewayPort}/api/v1/techpacks/tp_test/stream`,
    );

    await new Promise<void>((resolve) => client.on("open", () => resolve()));

    // Expect 2 agent messages + 1 done message = 3
    const messages = await waitForMessages(client, 3);
    expect(messages[0]).toMatchObject({ agent: "brief_analyzer", status: "running" });
    expect(messages[1]).toMatchObject({ agent: "brief_analyzer", status: "completed" });
    expect(messages[2]).toMatchObject({ event: "done", status: "completed" });

    client.close();
  });

  it("sends error when orchestrator is unreachable", async () => {
    const app = express();
    gatewayServer = http.createServer(app);
    // Point to a port where nothing is listening
    setupWebSocketHandler(gatewayServer, "ws://localhost:19999");

    await new Promise<void>((resolve) =>
      gatewayServer.listen(0, () => resolve()),
    );
    gatewayPort = (gatewayServer.address() as any).port;

    const client = new WebSocket(
      `ws://localhost:${gatewayPort}/api/v1/techpacks/tp_test/stream`,
    );

    await new Promise<void>((resolve) => client.on("open", () => resolve()));

    const messages = await waitForMessages(client, 1);
    expect(messages[0]).toMatchObject({ error: expect.any(String) });

    client.close();
  });
});
