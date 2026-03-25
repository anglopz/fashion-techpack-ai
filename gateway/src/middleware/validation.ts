import { Request, Response, NextFunction } from "express";
import { ZodSchema, z } from "zod";

export function validate(schema: ZodSchema) {
  return (req: Request, res: Response, next: NextFunction): void => {
    const result = schema.safeParse(req.body);
    if (!result.success) {
      res.status(400).json({
        error: "Validation failed",
        details: result.error.issues,
      });
      return;
    }
    req.body = result.data;
    next();
  };
}

export const CreateTechPackSchema = z.object({
  description: z.string().min(1),
  garment_type: z.string().optional(),
  target_season: z.string().optional(),
  fabric_preferences: z.array(z.string()).default([]),
  color_palette: z.array(z.string()).default([]),
  style_references: z.array(z.string()).default([]),
  engine: z.enum(["langgraph", "crewai"]).default("langgraph"),
});

export const CreateFabricSchema = z.object({
  name: z.string().min(1),
  composition: z.string().min(1),
  weight_gsm: z.number().positive(),
  width_cm: z.number().positive(),
  color: z.string().min(1),
  care_instructions: z.array(z.string()),
});
