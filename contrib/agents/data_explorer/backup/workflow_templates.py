"""
Workflow Templates for Structured Data Explorer Agent.

Provides consistent output templates and structured data management
for reliable business intelligence generation.
"""

from datetime import datetime
from typing import Any, TypedDict


class PhaseResult(TypedDict):
    """Type definition for phase execution results."""
    phase_number: int
    phase_name: str
    status: str
    data_collected: dict[str, Any]
    insights: list[str]
    timestamp: str


class BusinessInsight(TypedDict):
    """Type definition for structured business insights."""
    insight_number: int
    title: str
    executive_summary: str
    data_foundation: str
    business_impact: dict[str, str]
    implementation_plan: dict[str, Any]
    success_metrics: list[dict[str, str]]
    next_steps: list[str]


class WorkflowState:
    """
    Manages the state and templates for the structured data exploration workflow.

    Provides consistent output formatting and progress tracking across
    the 5-phase analysis process.
    """

    def __init__(self, index_name: str) -> None:
        """
        Initialize workflow state for a specific index analysis.

        Args:
            index_name: Name of the Splunk index being analyzed
        """
        self.index_name = index_name
        self.phases: list[PhaseResult] = []
        self.current_phase = 0
        self.start_time = datetime.now().isoformat()

    def get_phase_template(self, phase_number: int) -> str:
        """
        Get the output template for a specific phase.

        Args:
            phase_number: Phase number (1-5)

        Returns:
            Formatted template string for the phase
        """
        templates = {
            1: """🔍 **PHASE 1: Index Baseline Analysis**
Index: {index_name}
Total Events: {total_events}
Size: {size_mb} MB
Time Range: {earliest} to {latest}
Status: ✅ Index validated""",

            2: """📊 **PHASE 2: Data Composition Analysis**
Top Sourcetypes:
{sourcetype_list}

Top Hosts:
{host_list}

Key Findings:
- Primary data source: {dominant_sourcetype} ({percentage}% of data)
- Host diversity: {host_count} unique hosts
- Data concentration: {distribution_insights}""",

            3: """⏰ **PHASE 3: Temporal Pattern Analysis**
Weekly Volume Trend:
{daily_volume_analysis}

Hourly Usage Pattern:
{hourly_pattern_analysis}

Operational Insights:
- Peak usage: {peak_time_and_volume}
- Baseline traffic: {baseline_volume}
- Usage pattern: {business_hours_pattern}""",

            4: """🔍 **PHASE 4: Data Quality Assessment**
Sample Events Analysis:
{sample_events_analysis}

Field Completeness:
{field_completeness_list}

Data Quality Score: {quality_score}/10
Key Issues:
{quality_issues_list}""",

            5: """💼 **PHASE 5: Business Intelligence Generation**
Generated {insight_count} actionable business insights based on real data analysis.
Each insight includes specific SPL queries, dashboard recommendations, and measurable success metrics."""
        }

        return templates.get(phase_number, "Unknown phase template")

    def get_insight_template(self) -> str:
        """
        Get the template for business insights.

        Returns:
            Formatted template string for business insights
        """
        return """💡 **BUSINESS INSIGHT #{insight_number}: {title}**

**Executive Summary**: {executive_summary}

**Data Foundation**:
{data_foundation}

**Business Impact**:
- Cost Impact: {cost_impact}
- Operational Impact: {operational_impact}
- Risk Impact: {risk_impact}

**Implementation Plan**:
1. **Immediate Action**: {immediate_action}
   ```spl
   {immediate_spl}
   ```

2. **Dashboard Creation**: {dashboard_recommendation}
   - Panel 1: {panel_1_description}
   - Panel 2: {panel_2_description}

3. **Alert Configuration**: {alert_recommendation}
   ```spl
   {alert_spl}
   ```

**Success Metrics**:
- {metric_1_name}: {metric_1_target}
- {metric_2_name}: {metric_2_target}

**Next Steps**: {next_steps}

---"""

    def get_phase_spl_queries(self, phase_number: int) -> list[str]:
        """
        Get the required SPL queries for a specific phase.

        Args:
            phase_number: Phase number (1-5)

        Returns:
            List of SPL query strings for the phase
        """
        query_templates = {
            1: [
                f"| rest /services/data/indexes | search title={self.index_name} | table title, currentDBSizeMB, totalEventCount, maxTime, minTime"
            ],
            2: [
                f"index={self.index_name} | stats count by sourcetype | sort -count | head 10",
                f"index={self.index_name} | stats count by host | sort -count | head 10"
            ],
            3: [
                f"index={self.index_name} earliest=-7d | timechart span=1d count",
                f"index={self.index_name} earliest=-24h | timechart span=1h count"
            ],
            4: [
                f"index={self.index_name} | head 20 | table _time, host, source, sourcetype, _raw",
                f"index={self.index_name} | fieldsummary | sort -count | head 15"
            ],
            5: []  # Phase 5 is analysis, not data collection
        }

        return query_templates.get(phase_number, [])

    def record_phase_completion(self, phase_number: int, data: dict[str, Any]) -> None:
        """
        Record the completion of a workflow phase.

        Args:
            phase_number: Completed phase number
            data: Data collected during the phase
        """
        phase_names = {
            1: "Index Discovery & Baseline Analysis",
            2: "Data Composition Analysis",
            3: "Temporal Patterns & Usage Analysis",
            4: "Data Quality & Structure Assessment",
            5: "Business Intelligence Generation"
        }

        phase_result: PhaseResult = {
            "phase_number": phase_number,
            "phase_name": phase_names.get(phase_number, f"Phase {phase_number}"),
            "status": "completed",
            "data_collected": data,
            "insights": [],
            "timestamp": datetime.now().isoformat()
        }

        self.phases.append(phase_result)
        self.current_phase = phase_number

    def get_workflow_summary(self) -> str:
        """
        Generate a summary of the completed workflow.

        Returns:
            Formatted workflow summary string
        """
        completed_phases = len(self.phases)
        return f"""
🎯 **DATA EXPLORATION WORKFLOW SUMMARY**
Index Analyzed: {self.index_name}
Phases Completed: {completed_phases}/5
Analysis Duration: {self.start_time}
Status: {"✅ Complete" if completed_phases == 5 else f"⏳ In Progress (Phase {completed_phases + 1})"}

Ready for: Dashboard creation, Alert configuration, Data optimization
"""


def create_sample_insights() -> list[BusinessInsight]:
    """
    Create sample business insight templates for demonstration.

    Returns:
        List of sample business insights with proper structure
    """
    return [
        {
            "insight_number": 1,
            "title": "Cost Optimization through Data Lifecycle Management",
            "executive_summary": "Reduce indexing costs by implementing intelligent data retention policies based on usage patterns",
            "data_foundation": "Analysis of temporal patterns and sourcetype volumes",
            "business_impact": {
                "cost_impact": "15-25% reduction in storage costs",
                "operational_impact": "Automated data lifecycle management",
                "risk_impact": "Maintained compliance with reduced overhead"
            },
            "implementation_plan": {
                "immediate_action": "Analyze data age and access patterns",
                "dashboard_recommendation": "Data retention monitoring dashboard",
                "alert_recommendation": "Storage threshold alerts"
            },
            "success_metrics": [
                {"name": "Storage cost reduction", "target": "20%"},
                {"name": "Query performance improvement", "target": "15%"}
            ],
            "next_steps": ["Configure retention policies", "Set up monitoring"]
        }
    ]
