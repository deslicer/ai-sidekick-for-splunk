# IndexAnalyzer Agent

Demo agent for the AI Sidekick for Splunk Lab demonstrating systematic index analysis.

## Overview

This agent performs a 5-phase systematic analysis of Splunk indexes:

1. **Data Types Discovery** - Identifies sourcetypes and data patterns
2. **Field Analysis** - Analyzes field distributions and patterns
3. **Sample Data Collection** - Gathers representative data samples
4. **Volume Assessment** - Evaluates index size and event counts
5. **Business Insights Generation** - Creates persona-based use cases

## Features

- ✅ **Real Data Integration** - Uses SplunkMCP_agent for actual Splunk searches
- ✅ **Systematic Workflow** - 5-phase approach ensures comprehensive analysis
- ✅ **Business Intelligence** - Generates actionable insights with SPL queries
- ✅ **Auto-Discovery** - Follows standard agent discovery pattern

## Usage

```
"Use index_analyzer to analyze index=pas"
"IndexAnalyzer analyze index=_internal"
"Help me analyze index=_audit with index_analyzer"
```

## Implementation

This agent demonstrates:
- LlmAgent pattern for simple, effective implementation
- BaseAgent inheritance with proper metadata
- Auto-discovery factory functions
- Structured logging and error handling
- Integration with the multi-agent orchestrator system

## Workshop Learning Objectives

- Understand agent structure and auto-discovery
- Learn the DataExplorer systematic approach
- Practice real data integration patterns
- Generate business intelligence from Splunk data
