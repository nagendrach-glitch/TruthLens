"""
crew.py
Defines the TruthLens CrewAI crew: agents, tasks, and their wiring.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from .tools import YouTubeTranscriptTool, WebScrapingTool, FileReaderTool

# ── Optional: Serper web search ──────────────────────────────────────────────
try:
    from crewai_tools import SerperDevTool
    SERPER_AVAILABLE = True
except ImportError:
    SERPER_AVAILABLE = False
    print("[TruthLens] SerperDevTool not available — web search will be limited.")


def _build_tools(include_file: bool = False, include_serper: bool = False) -> list:
    """Instantiate tools on demand to avoid import-time failures."""
    tools = [WebScrapingTool(), YouTubeTranscriptTool()]
    if include_file:
        tools.append(FileReaderTool())
    if include_serper and SERPER_AVAILABLE:
        tools.append(SerperDevTool())
    return tools


@CrewBase
class FactChecker:
    """TruthLens fact-checking crew."""

    agents_config = "config/agents.yaml"
    tasks_config  = "config/tasks.yaml"

    # ── Agents ────────────────────────────────────────────────────────────────

    @agent
    def fact_researcher(self) -> Agent:
        """Gathers raw content from all input sources."""
        return Agent(
            config=self.agents_config["fact_researcher"],
            tools=_build_tools(include_file=True, include_serper=True),
            verbose=True,
        )

    @agent
    def content_analyzer(self) -> Agent:
        """Parses raw content into discrete, verifiable claims."""
        return Agent(
            config=self.agents_config["content_analyzer"],
            tools=_build_tools(include_file=False, include_serper=False),
            verbose=True,
        )

    @agent
    def fact_verifier(self) -> Agent:
        """Cross-references claims against authoritative sources."""
        return Agent(
            config=self.agents_config["fact_verifier"],
            tools=_build_tools(include_file=False, include_serper=True),
            verbose=True,
        )

    # ── Tasks ─────────────────────────────────────────────────────────────────

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],
            agent=self.fact_researcher(),
        )

    @task
    def content_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["content_analysis_task"],
            agent=self.content_analyzer(),
            context=[self.research_task()],
        )

    @task
    def verification_task(self) -> Task:
        return Task(
            config=self.tasks_config["verification_task"],
            agent=self.fact_verifier(),
            context=[self.research_task(), self.content_analysis_task()],
        )

    # ── Crew ──────────────────────────────────────────────────────────────────

    @crew
    def crew(self) -> Crew:
        """Assembles and returns the TruthLens fact-checking crew."""
        return Crew(
            agents=[
                self.fact_researcher(),
                self.content_analyzer(),
                self.fact_verifier(),
            ],
            tasks=[
                self.research_task(),
                self.content_analysis_task(),
                self.verification_task(),
            ],
            process=Process.sequential,
            verbose=True,
        )