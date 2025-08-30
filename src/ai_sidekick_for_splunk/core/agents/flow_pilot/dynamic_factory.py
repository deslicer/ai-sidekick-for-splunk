"""
Dynamic FlowPilot Agent Factory

This module creates FlowPilot agents dynamically based on discovered workflows.
It integrates the workflow discovery system with the agent discovery system to ensure
that all discovered workflows are available as agents in ADK Web and the orchestrator.

"""

import logging

from ...flows_engine.workflow_discovery import WorkflowInfo, WorkflowSource, discover_all_workflows
from .agent import FlowPilot, create_flow_pilot

logger = logging.getLogger(__name__)


class DynamicFlowPilotFactory:
    """
    Factory for creating FlowPilot agents dynamically based on discovered workflows.

    This factory scans for workflow definitions and creates corresponding FlowPilot
    agents, making them available for discovery by the orchestrator and ADK Web.

    """

    def __init__(self):
        self._discovered_workflows: dict[str, WorkflowInfo] = {}
        self._created_agents: dict[str, FlowPilot] = {}
        self._agent_instances: dict[str, FlowPilot] = {}

    def discover_and_create_agents(self, orchestrator=None) -> dict[str, FlowPilot]:
        """
        Discover all workflows and create corresponding FlowPilot agents.

        Args:
            orchestrator: The orchestrator instance to inject into agents

        Returns:
            Dictionary of agent_name -> FlowPilot instance
        """
        logger.info("🔍 Discovering workflows and creating FlowPilot agents...")

        # Discover all workflows
        try:
            workflows = discover_all_workflows(force_refresh=True)
            self._discovered_workflows = workflows
            logger.info(f"✅ Discovered {len(workflows)} workflows")
        except Exception as e:
            logger.error(f"❌ Failed to discover workflows: {e}")
            return {}

        # Create agents for each workflow
        created_count = 0
        for workflow_id, workflow_info in workflows.items():
            try:
                agent_name = self._generate_agent_name(workflow_info)

                # Skip if already created
                if agent_name in self._created_agents:
                    continue

                # Create FlowPilot agent
                agent = create_flow_pilot(
                    template_path=str(workflow_info.file_path), orchestrator=orchestrator
                )

                self._created_agents[agent_name] = agent
                self._agent_instances[agent_name] = agent

                logger.info(f"✅ Created FlowPilot agent: {agent_name}")
                created_count += 1

            except Exception as e:
                logger.error(f"❌ Failed to create agent for workflow {workflow_id}: {e}")
                continue

        logger.info(f"🎉 Created {created_count} FlowPilot agents from discovered workflows")
        return self._agent_instances.copy()

    def _generate_agent_name(self, workflow_info: WorkflowInfo) -> str:
        """
        Generate a consistent agent name from workflow info.

        Args:
            workflow_info: The workflow information

        Returns:
            Agent name suitable for discovery
        """
        # Use the workflow name directly, cleaned up for agent naming
        base_name = workflow_info.workflow_name

        # Clean up the name for agent discovery
        # Remove common suffixes and prefixes
        clean_name = base_name.replace(" Flow", "").replace("Flow ", "")
        clean_name = clean_name.replace(" Workflow", "").replace("Workflow ", "")

        # Convert to a valid identifier-like name
        agent_name = clean_name.replace(" ", "_").replace("-", "_")

        # Add source prefix for contrib workflows to avoid conflicts
        if workflow_info.source == WorkflowSource.CONTRIB:
            agent_name = f"Contrib_{agent_name}"

        return agent_name

    def get_agent_by_workflow_id(self, workflow_id: str) -> FlowPilot:
        """
        Get an agent by its workflow ID.

        Args:
            workflow_id: The workflow ID (e.g., 'contrib.helloworld')

        Returns:
            FlowPilot agent instance or None if not found
        """
        if workflow_id not in self._discovered_workflows:
            return None

        workflow_info = self._discovered_workflows[workflow_id]
        agent_name = self._generate_agent_name(workflow_info)

        return self._agent_instances.get(agent_name)

    def get_all_agents(self) -> dict[str, FlowPilot]:
        """Get all created FlowPilot agents."""
        return self._agent_instances.copy()

    def get_workflow_info(self, agent_name: str) -> WorkflowInfo:
        """
        Get workflow info for a given agent name.

        Args:
            agent_name: The agent name

        Returns:
            WorkflowInfo instance or None if not found
        """
        # Find the workflow that corresponds to this agent name
        for workflow_info in self._discovered_workflows.values():
            if self._generate_agent_name(workflow_info) == agent_name:
                return workflow_info
        return None

    def refresh_agents(self, orchestrator=None) -> dict[str, FlowPilot]:
        """
        Refresh the agent list by re-discovering workflows.

        Args:
            orchestrator: The orchestrator instance

        Returns:
            Updated dictionary of agents
        """
        logger.info("🔄 Refreshing FlowPilot agents...")
        self._created_agents.clear()
        self._agent_instances.clear()
        return self.discover_and_create_agents(orchestrator)


# Global factory instance
_factory_instance = None


def get_dynamic_factory() -> DynamicFlowPilotFactory:
    """Get the global dynamic factory instance."""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = DynamicFlowPilotFactory()
    return _factory_instance


def create_dynamic_flowpilot_agents(orchestrator=None) -> dict[str, FlowPilot]:
    """
    Convenience function to create all dynamic FlowPilot agents.

    Args:
        orchestrator: The orchestrator instance

    Returns:
        Dictionary of agent_name -> FlowPilot instance
    """
    factory = get_dynamic_factory()
    return factory.discover_and_create_agents(orchestrator)


def get_all_dynamic_agents() -> dict[str, FlowPilot]:
    """Get all dynamically created FlowPilot agents."""
    factory = get_dynamic_factory()
    return factory.get_all_agents()
