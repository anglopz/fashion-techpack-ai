"""CrewAI prototype for tech pack generation with 4 specialized agents."""

from __future__ import annotations

import os

from crewai import Agent, Crew, LLM, Process, Task

from app.crews.tools import brief_parser_tool, embedding_tool, fabric_search_tool


def _get_llm(model_path: str) -> LLM:
    """Create an OpenRouter-backed LLM instance."""
    return LLM(
        model=f"openrouter/{model_path}",
        api_key=os.getenv("OPENROUTER_API_KEY", ""),
    )


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

def create_design_analyst() -> Agent:
    """Agent 1: Parse unstructured design briefs into structured data."""
    return Agent(
        role="Design Analyst",
        goal="Parse unstructured design briefs into structured garment specifications",
        backstory=(
            "You are a senior fashion designer with 15 years of experience "
            "reading design briefs from creative directors. You excel at "
            "extracting precise specifications from vague creative language."
        ),
        tools=[brief_parser_tool],
        llm=_get_llm("openai/gpt-4o-mini"),
        verbose=True,
    )


def create_fabric_specialist() -> Agent:
    """Agent 2: Find best fabric matches from catalog via RAG."""
    return Agent(
        role="Fabric Specialist",
        goal="Find the best fabric matches from the catalog for the given design",
        backstory=(
            "You are a textile expert specializing in sustainable fabrics "
            "with deep knowledge of fabric properties, sourcing, and seasonal "
            "appropriateness. You can match fabric requirements to catalog "
            "entries with precision."
        ),
        tools=[fabric_search_tool, embedding_tool],
        llm=_get_llm("openai/gpt-4o-mini"),
        verbose=True,
    )


def create_production_planner() -> Agent:
    """Agent 3: Generate complete bill of materials."""
    return Agent(
        role="Production Planner",
        goal="Generate a complete bill of materials for garment production",
        backstory=(
            "You are a production manager with expertise in garment "
            "manufacturing, costing, and bill of materials generation. "
            "You know exactly what materials, trims, and hardware are "
            "needed for any garment type."
        ),
        tools=[],
        llm=_get_llm("openai/gpt-4o-mini"),
        verbose=True,
    )


def create_technical_writer() -> Agent:
    """Agent 4: Assemble all outputs into final tech pack."""
    return Agent(
        role="Technical Writer",
        goal="Assemble all agent outputs into a comprehensive fashion tech pack",
        backstory=(
            "You are a technical documentation specialist who assembles "
            "comprehensive fashion tech packs from structured data. You "
            "ensure consistency, completeness, and professional formatting."
        ),
        tools=[],
        llm=_get_llm("anthropic/claude-sonnet-4"),
        verbose=True,
    )


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def create_analyze_task(agent: Agent) -> Task:
    """Task 1: Analyze the design brief."""
    return Task(
        description=(
            "Analyze the following design brief and extract structured "
            "information including garment type, fabric preferences, color "
            "palette, and key design requirements.\n\n"
            "Design brief: {brief}"
        ),
        expected_output=(
            "A JSON object with: garment_type, fabric_keywords (list), "
            "color_palette (list), fit_type, target_season, and any "
            "special construction requirements."
        ),
        agent=agent,
    )


def create_fabric_match_task(agent: Agent) -> Task:
    """Task 2: Find matching fabrics from the catalog."""
    return Task(
        description=(
            "Based on the design analysis, search the fabric catalog to "
            "find the best matching fabrics. Consider the garment type, "
            "season, and fabric preferences. Return the top 3 matches "
            "with similarity scores."
        ),
        expected_output=(
            "A JSON array of fabric specifications, each with: name, "
            "composition, weight_gsm, width_cm, color, supplier, "
            "price_per_meter, care_instructions, and similarity_score."
        ),
        agent=agent,
    )


def create_bom_task(agent: Agent) -> Task:
    """Task 3: Generate bill of materials."""
    return Task(
        description=(
            "Using the garment type, selected fabrics, and design "
            "requirements, generate a complete bill of materials. Include "
            "all fabric quantities, trims (buttons, zippers, labels), "
            "thread, and hardware needed for production."
        ),
        expected_output=(
            "A JSON array of BOM items, each with: category (fabric, "
            "trim, hardware, thread, label), description, quantity, unit, "
            "color, and supplier."
        ),
        agent=agent,
    )


def create_assemble_task(agent: Agent) -> Task:
    """Task 4: Assemble the final tech pack."""
    return Task(
        description=(
            "Compile all previous outputs into a complete fashion tech "
            "pack. Include measurements with size grading (XS-XL), "
            "construction details with stitch types and seam allowances, "
            "and organize everything into the standard tech pack format. "
            "The output MUST be valid JSON matching the TechPack schema."
        ),
        expected_output=(
            "A complete JSON tech pack with: id, brief, measurements "
            "(with key_measurements per size), primary_fabric, "
            "secondary_fabrics, bom (list of items), construction "
            "(list of steps with stitch_type and seam_allowance), "
            "colorways, status, created_at, and version."
        ),
        agent=agent,
    )


# ---------------------------------------------------------------------------
# Crew
# ---------------------------------------------------------------------------

def create_techpack_crew() -> Crew:
    """Build the full TechPack crew with 4 agents and sequential process."""
    design_analyst = create_design_analyst()
    fabric_specialist = create_fabric_specialist()
    production_planner = create_production_planner()
    technical_writer = create_technical_writer()

    analyze_task = create_analyze_task(design_analyst)
    match_task = create_fabric_match_task(fabric_specialist)
    bom_task = create_bom_task(production_planner)
    assemble_task = create_assemble_task(technical_writer)

    return Crew(
        agents=[
            design_analyst,
            fabric_specialist,
            production_planner,
            technical_writer,
        ],
        tasks=[analyze_task, match_task, bom_task, assemble_task],
        process=Process.sequential,
        verbose=True,
    )
