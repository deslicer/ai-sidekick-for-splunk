# Data quality check

This workflow checks the data quality issues in splunk

## Overview

**Category:** Data_Quality  
**Complexity:** Beginner  
**Estimated Duration:** 5-10 minutes  
**Author:** community  
**Version:** 1.0.0

## Business Value

helps detect data quality issue during data onboarding process

## Use Cases

- detect data quality issues
- Improve search and overall system performance

## Requirements

**Splunk Versions:** 8.0+, 9.0+  
**Required Permissions:** search, _internal index, all indexes

## Workflow Phases

### Main Analysis Phase

**dq_ingestion_latency:**
- Description: Median and p95 of index-time minus event time (seconds); large gaps suggest clock skew or delayed delivery.
- SPL: `index=* _time=* 
| eval latency=_indextime - _time
| where latency>=0 AND latency<86400
| stats median(latency) as p50, perc95(latency) as p95 by sourcetype
| sort - p95`

**dq_timestamp_parse_warnings:**
- Description: Scans splunkd logs for DateParser/strptime warnings that indicate TIME_FORMAT/TIME_PREFIX issues.
- SPL: `index=_internal source=*splunkd.log* 
("DateParserVerbose" OR "could not use strptime" OR "Failed to parse timestamp")
| rex field=_raw max_match=1 "(?i)sourcetype=(?<sourcetype>[^ ]+)"
| timechart span=15m count by sourcetype limit=15`

**dq_line_breaking_risk:**
- Description: Flags unusually large events that could indicate bad line breaking or TRUNCATE behavior.
- SPL: `index=* 
| eval ev_len=len(_raw)
| where ev_len >= 10000
| stats count as large_events, max(ev_len) as max_event_len by sourcetype
| sort - large_events`

**dq_duplicate_events_hash:**
- Description: Detects potential duplicates by hashing _raw per sourcetype/source in window; tune window to avoid false positives.
- SPL: `index=* 
| eval sig=md5(_raw)
| stats count as cnt by sourcetype, source, sig
| where cnt>1
| stats sum(cnt) as duplicate_events, dc(sig) as duplicate_signatures by sourcetype, source
| sort - duplicate_events`
- Time Range: -6h@h to now

**dq_missing_time_or_future_past:**
- Description: Finds events with _time in the future/past beyond a threshold, a common sign of bad timestamp parsing or TZ.
- SPL: `index=* 
| eval now=now(), skew=_time-now
| eval time_issue=case(skew>3600,"future_gt_1h", skew<-31536000,"past_gt_1y", true(),null())
| where isnotnull(time_issue)
| stats count by time_issue, sourcetype
| sort - count`

**dq_field_coverage_summary:**
- Description: Summarizes field presence/null rates to spot broken extractions after ingestion changes.
- SPL: `index=* 
| head 5000
| fieldsummary
| eval null_pct=round(100*(isnull)/count,2)
| table field, distinct_values, null_pct, maxlen, avglen
| sort - null_pct`
- Time Range: -2h@h to now

**dq_source_host_coverage:**
- Description: Distinct hosts and sources per sourcetype; useful to catch missing senders or misrouted data.
- SPL: `index=* 
| stats dc(host) as hosts, dc(source) as sources by sourcetype
| sort - hosts`

**dq_event_rate_stability:**
- Description: Compares last hour vs prior day same hour average to flag big drops/spikes in volume.
- SPL: `| tstats count WHERE index=* by _time, sourcetype span=1h
| eval hour=strftime(_time,"%H")
| eventstats avg(count) as prior_avg by sourcetype, hour
| eval delta=count-prior_avg, pct=round(100*delta/prior_avg,2)
| where abs(pct)>=50 AND prior_avg>0
| table _time, sourcetype, count, prior_avg, pct
| sort - _time`
- Time Range: -25h@h to now

**dq_nullqueue_suspect_queue_pressure:**
- Description: Queue fill % as a proxy for parsing pressure that can lead to data loss or delays.
- SPL: `index=_internal source=*metrics.log group=queue
| stats avg(current_size_kb) as size_kb, avg(max_size_kb) as max_kb by name
| eval fill_pct=round(100*size_kb/max_kb,2)
| sort - fill_pct`
- Time Range: -1h@h to now

**dq_index_storage_headroom:**
- Description: Checks total index size vs configured max to spot near-capacity indexes (can cause data aging/truncation).
- SPL: `| rest /services/data/indexes
| eval current_size_gb=round(currentDBSizeMB/1024,2)
| eval max_gb=case(isnotnull(maxTotalDataSizeMB), round(maxTotalDataSizeMB/1024,2), true(), null())
| eval pct_of_max=if(isnotnull(max_gb) AND max_gb>0, round(100*current_size_gb/max_gb,2), null())
| table title, totalEventCount, current_size_gb, max_gb, pct_of_max, frozenTimePeriodInSecs
| sort - pct_of_max`

**dq_line_breaking_candidates_xml_json:**
- Description: Heuristic: XML/JSON sources with very large lines often need explicit LINE_BREAKER/SHOULD_LINEMERGE configs.
- SPL: `index=* (sourcetype=*xml* OR sourcetype=*json* OR source="*.xml" OR source="*.json")
| eval ev_len=len(_raw)
| where ev_len>=10000
| stats count as large_events, max(ev_len) as max_event_len by sourcetype, source
| sort - large_events`

## Usage

1. **Start AI Sidekick:** Ensure your AI Sidekick is running
2. **Select Agent:** Choose the FlowPilot agent from the dropdown
3. **Execute Workflow:** Use the command or describe your analysis needs
4. **Review Results:** Examine the comprehensive analysis and recommendations

## Success Metrics

- no line breaking, time stamp parsing or truncation errors
- performant indexing pipelines queues

## Template Information

This workflow was generated from a YAML template on 2025-09-04.

**Template Version:** 1.0.0  
**Template Format:** 1.0  
**Generated JSON:** `dq_check_flow_fixed.json`

To modify this workflow, edit the `dq_check_flow_fixed.yaml` template file and regenerate.
