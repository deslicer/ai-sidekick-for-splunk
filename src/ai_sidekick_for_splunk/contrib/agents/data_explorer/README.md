# Structured Data Explorer Agent

A systematic, multi-phase approach to Splunk data analysis that provides consistent, actionable business intelligence with real data integration.

## 🎯 Key Improvements

### Problems Solved
- ❌ **Generic Insights**: Previous version generated vague, non-specific recommendations
- ❌ **Inconsistent Experience**: Pure LLM approach led to variable response quality
- ❌ **Missing SPL Implementation**: No concrete queries or actionable next steps
- ❌ **Fake Data Risk**: Potential for fabricated statistics and metrics

### Solution: Structured 5-Phase Workflow
- ✅ **Mandatory Phase Execution**: Consistent workflow every time
- ✅ **Real Data Integration**: All insights based on actual Splunk search results
- ✅ **Actionable SPL Queries**: Every insight includes ready-to-execute searches
- ✅ **Template-Driven Output**: Consistent formatting and comprehensive details

## 📋 Workflow Phases

### Phase 1: Index Discovery & Baseline Analysis
**Objective**: Validate index existence and establish baseline metrics

**Required Searches**:
```spl
| rest /services/data/indexes | search title={index_name} | table title, currentDBSizeMB, totalEventCount, maxTime, minTime
```

**Output**: Index validation, size metrics, time range coverage

### Phase 2: Data Composition Analysis
**Objective**: Understand data types and volume distribution

**Required Searches**:
```spl
index={index_name} | stats count by sourcetype | sort -count
index={index_name} | stats count by host | sort -count
index={index_name} | stats count by source | sort -count
```

**Output**: Sourcetype distribution, host and source diversity analysis

### Phase 3: Temporal Patterns & Usage Analysis
**Objective**: Identify usage patterns and operational insights

**Required Searches**:
```spl
index={index_name} earliest=-7d | timechart span=1d count
index={index_name} earliest=-24h | timechart span=1h count
```

**Output**: Volume trends, peak usage times, operational patterns

### Phase 4: Data Quality & Structure Assessment
**Objective**: Evaluate data completeness and field richness

**Required Searches**:
```spl
index={index_name} | head 5000 | table _time, host, source, sourcetype, _raw
index={index_name} | fieldsummary | sort -count | head 15
```

**Output**: Sample events, field completeness, data quality score

### Phase 5: Business Intelligence Generation
**Objective**: Generate exactly 5 actionable business insights

**Output**: Structured insights with:
- Executive summary
- Data foundation (specific findings)
- Quantified business impact
- Implementation plan with SPL queries
- Dashboard recommendations
- Alert configurations
- Success metrics
- Next steps

## 🎯 Business Insight Template

Each insight follows this mandatory structure:

```markdown
💡 **BUSINESS INSIGHT #N: {Title}**

**Executive Summary**: {One-sentence value proposition}

**Data Foundation**:
{Specific findings from real search results}

**Business Impact**:
- Cost Impact: {Quantified savings/cost}
- Operational Impact: {Efficiency gains}
- Risk Impact: {Risk reduction/compliance benefit}

**Implementation Plan**:
1. **Immediate Action**: {First step with SPL}
   ```spl
   {Ready-to-execute SPL query}
   ```

2. **Dashboard Creation**: {Dashboard recommendation}
   - Panel 1: {Description with SPL}
   - Panel 2: {Description with SPL}

3. **Alert Configuration**: {Alert recommendation}
   ```spl
   {Alert SPL query}
   ```

**Success Metrics**:
- {Metric 1}: {Target value}
- {Metric 2}: {Target value}

**Next Steps**: {Specific actionable items}
```

## 🔧 Technical Architecture

### Agent Structure
- **Base**: `LlmAgent` with structured prompt instructions
- **Workflow Management**: Phase-by-phase execution templates
- **Data Integration**: Mandatory delegation to SplunkMCP for real data
- **Output Templates**: Consistent formatting for all phases

### Quality Assurance
- **Real Data Mandate**: Never generate fake statistics
- **Template Compliance**: All outputs follow structured templates
- **SPL Validation**: All queries are syntactically correct
- **Business Focus**: Every insight addresses specific business value

### Files Structure
```
data_explorer/
├── agent.py                 # Main DataExplorer agent implementation
├── prompt.py                # Agent instructions and workflow
├── __init__.py              # Module exports and imports
├── README.md                # This documentation
```

## 🚀 Usage Example

### Input
```
analyze index=pas
```

### Expected Output Flow
1. **Phase 1**: Index validation and baseline metrics
2. **Phase 2**: Sourcetype and host distribution analysis
3. **Phase 3**: Temporal pattern identification
4. **Phase 4**: Data quality assessment
5. **Phase 5**: 5 structured business insights with:
   - Specific SPL queries for implementation
   - Dashboard panel recommendations
   - Alert configuration templates
   - Quantified success metrics

### Sample Insight Output
```markdown
💡 **BUSINESS INSIGHT #1: Cost Optimization through Data Lifecycle Management**

**Executive Summary**: Reduce indexing costs by 20% through intelligent data retention policies based on actual usage patterns.

**Data Foundation**:
Analysis shows pas:application represents 40% of index volume but only 15% is accessed after 90 days.

**Business Impact**:
- Cost Impact: $50K annual savings on storage costs
- Operational Impact: 25% faster search performance
- Risk Impact: Maintained compliance with reduced overhead

**Implementation Plan**:
1. **Immediate Action**: Analyze data access patterns by sourcetype
   ```spl
   index=pas | eval age=floor((now()-_time)/86400) | stats count by sourcetype, age | where age>90
   ```

2. **Dashboard Creation**: Data retention monitoring dashboard
   - Panel 1: Volume by sourcetype and age (timechart)
   - Panel 2: Access frequency heatmap by data age

3. **Alert Configuration**: Storage threshold monitoring
   ```spl
   | rest /services/data/indexes | where currentDBSizeMB>threshold | table title, currentDBSizeMB
   ```

**Success Metrics**:
- Storage cost reduction: 20%
- Search performance improvement: 25%

**Next Steps**: Configure retention policies, implement monitoring alerts
```

## 🎯 Benefits

### For Users
- **Predictable Experience**: Same structured output every time
- **Actionable Results**: Ready-to-implement SPL queries and configurations
- **Business Focused**: Clear ROI and value propositions
- **Implementation Ready**: Dashboard and alert templates included

### For Workshops
- **Demonstrable Value**: Concrete results participants can immediately use
- **Learning Framework**: Systematic approach participants can replicate
- **Best Practices**: Templates and patterns for consistent analysis
- **Scalable Process**: Workflow applicable to any Splunk index

This structured approach ensures the Data Explorer agent provides consistent, valuable, and immediately actionable business intelligence for every user request.
