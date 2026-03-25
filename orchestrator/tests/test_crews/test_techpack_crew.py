"""Tests for CrewAI tech pack crew configuration."""

from crewai import Process

from app.crews.techpack_crew import (
    create_design_analyst,
    create_fabric_specialist,
    create_production_planner,
    create_technical_writer,
    create_techpack_crew,
    create_analyze_task,
    create_fabric_match_task,
    create_bom_task,
    create_assemble_task,
)


class TestAgentConfiguration:
    """Test that agents are configured correctly per PLAN.md section 5."""

    def test_design_analyst_role(self):
        agent = create_design_analyst()
        assert agent.role == "Design Analyst"
        assert "design brief" in agent.goal.lower()
        assert "senior fashion designer" in agent.backstory.lower()
        assert len(agent.tools) == 1  # brief_parser_tool

    def test_fabric_specialist_role(self):
        agent = create_fabric_specialist()
        assert agent.role == "Fabric Specialist"
        assert "fabric" in agent.goal.lower()
        assert "textile expert" in agent.backstory.lower()
        assert len(agent.tools) == 2  # fabric_search_tool, embedding_tool

    def test_production_planner_role(self):
        agent = create_production_planner()
        assert agent.role == "Production Planner"
        assert "bill of materials" in agent.goal.lower()
        assert "production manager" in agent.backstory.lower()
        assert len(agent.tools) == 0

    def test_technical_writer_role(self):
        agent = create_technical_writer()
        assert agent.role == "Technical Writer"
        assert "tech pack" in agent.goal.lower()
        assert "documentation specialist" in agent.backstory.lower()
        assert len(agent.tools) == 0


class TestTaskConfiguration:
    """Test that tasks are defined correctly."""

    def test_analyze_task_has_brief_placeholder(self):
        agent = create_design_analyst()
        task = create_analyze_task(agent)
        assert "{brief}" in task.description
        assert task.agent == agent

    def test_fabric_match_task(self):
        agent = create_fabric_specialist()
        task = create_fabric_match_task(agent)
        assert "fabric catalog" in task.description.lower()
        assert task.agent == agent

    def test_bom_task(self):
        agent = create_production_planner()
        task = create_bom_task(agent)
        assert "bill of materials" in task.description.lower()
        assert task.agent == agent

    def test_assemble_task(self):
        agent = create_technical_writer()
        task = create_assemble_task(agent)
        assert "tech pack" in task.description.lower()
        assert "tech pack" in task.expected_output.lower()
        assert task.agent == agent


class TestCrewConfiguration:
    """Test the full crew setup."""

    def test_crew_has_four_agents(self):
        crew = create_techpack_crew()
        assert len(crew.agents) == 4

    def test_crew_has_four_tasks(self):
        crew = create_techpack_crew()
        assert len(crew.tasks) == 4

    def test_crew_uses_sequential_process(self):
        crew = create_techpack_crew()
        assert crew.process == Process.sequential

    def test_crew_agent_order(self):
        crew = create_techpack_crew()
        roles = [a.role for a in crew.agents]
        assert roles == [
            "Design Analyst",
            "Fabric Specialist",
            "Production Planner",
            "Technical Writer",
        ]

    def test_crew_task_agent_alignment(self):
        """Each task should be assigned to the correct agent."""
        crew = create_techpack_crew()
        assert crew.tasks[0].agent.role == "Design Analyst"
        assert crew.tasks[1].agent.role == "Fabric Specialist"
        assert crew.tasks[2].agent.role == "Production Planner"
        assert crew.tasks[3].agent.role == "Technical Writer"
