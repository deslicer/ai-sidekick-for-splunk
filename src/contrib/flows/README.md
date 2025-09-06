# Test Basic Wf Workflow

A basic workflow template for test_basic_wf

## Overview

**Category:** Analysis  
**Complexity:** Beginner  
**Estimated Duration:** 2-3 minutes  
**Author:** community  
**Version:** 1.0.0

## Business Value

Provides basic analysis capabilities

## Use Cases

- Basic data analysis
- System monitoring

## Requirements

**Splunk Versions:** 8.0+, 9.0+  
**Required Permissions:** search

## Workflow Phases

### Main Analysis Phase

**basic_check:**
- Description: Basic data check
- SPL: `search earliest=-24h | head 10 | table _time, index, sourcetype`

## Usage

1. **Start AI Sidekick:** Ensure your AI Sidekick is running
2. **Select Agent:** Choose the FlowPilot agent from the dropdown
3. **Execute Workflow:** Use the command or describe your analysis needs
4. **Review Results:** Examine the comprehensive analysis and recommendations

## Success Metrics

- Successful completion of all workflow phases
- Actionable insights generated
- Clear recommendations provided

## Template Information

This workflow was generated from a YAML template on 2025-09-04.

**Template Version:** 1.0.0  
**Template Format:** 1.0  
**Generated JSON:** `test_basic_wf.json`

To modify this workflow, edit the `test_basic_wf.yaml` template file and regenerate.
