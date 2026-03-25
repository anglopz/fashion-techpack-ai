import {
  CreateTechPackRequest,
  CreateTechPackResponse,
  CreateFabricRequest,
  FabricSearchResult,
  WSMessage,
  AuthPayload,
} from "../../src/types";

describe("types", () => {
  it("CreateTechPackRequest has required fields", () => {
    const req: CreateTechPackRequest = {
      description: "Organic cotton t-shirt",
    };
    expect(req.description).toBe("Organic cotton t-shirt");
    expect(req.engine).toBeUndefined();
  });

  it("CreateTechPackRequest accepts all optional fields", () => {
    const req: CreateTechPackRequest = {
      description: "test",
      garment_type: "top",
      target_season: "SS26",
      fabric_preferences: ["cotton"],
      color_palette: ["#000"],
      style_references: ["ref1"],
      engine: "langgraph",
    };
    expect(req.engine).toBe("langgraph");
  });

  it("CreateTechPackResponse has all fields", () => {
    const res: CreateTechPackResponse = {
      id: "tp_abc123",
      status: "processing",
      engine: "langgraph",
      ws_url: "/api/v1/techpacks/tp_abc123/stream",
    };
    expect(res.id).toBe("tp_abc123");
  });

  it("CreateFabricRequest has required fields", () => {
    const req: CreateFabricRequest = {
      name: "Organic Cotton Jersey",
      composition: "100% Organic Cotton",
      weight_gsm: 180,
      width_cm: 150,
      color: "Natural White",
      care_instructions: ["Machine wash 30°C"],
    };
    expect(req.name).toBe("Organic Cotton Jersey");
  });

  it("WSMessage represents agent progress", () => {
    const msg: WSMessage = {
      agent: "brief_analyzer",
      status: "running",
      message: "Parsing design brief...",
    };
    expect(msg.agent).toBe("brief_analyzer");
  });
});
