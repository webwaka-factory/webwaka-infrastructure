# ADR-003: Cost-Aware Architecture for Observability

**Status:** ✅ Accepted  
**Date:** February 1, 2026  
**Decision Makers:** WebWaka Infrastructure Team  
**Consulted:** Platform Foundation Team, Finance Team

## Context

The WebWaka platform is designed with a Nigeria-first approach, where cost-effectiveness is a critical requirement. Observability infrastructure can be expensive due to high data volumes (logs, metrics, traces) and storage requirements. The platform must implement cost-aware strategies to minimize infrastructure costs while maintaining operational excellence.

### Cost Challenges

Observability systems generate large volumes of data that must be collected, transmitted, stored, and queried. Without careful design, observability costs can exceed application infrastructure costs.

**Typical Cost Drivers:**
- **Log ingestion:** High-volume logs can generate terabytes of data per month
- **Metrics storage:** Time-series databases require significant storage and compute
- **Trace storage:** Distributed traces can be very large (MB per trace)
- **Network bandwidth:** Transmitting telemetry data consumes bandwidth
- **Storage retention:** Long-term storage of telemetry data is expensive

**Nigeria-First Constraints:**
- **Limited bandwidth:** Internet bandwidth in Nigeria is expensive and often limited
- **Cost-sensitive market:** Customers expect low-cost solutions
- **Infrastructure costs:** Cloud infrastructure costs are higher in Nigeria than in developed markets

## Decision Drivers

1. **Cost Minimization:** Reduce observability costs to the absolute minimum while maintaining operational visibility
2. **Bandwidth Efficiency:** Minimize network bandwidth consumption for telemetry transmission
3. **Storage Efficiency:** Optimize storage usage through compression, sampling, and retention policies
4. **Operational Visibility:** Maintain sufficient visibility to detect and diagnose issues
5. **Scalability:** Cost-aware strategies must scale as the platform grows

## Decision

We will implement a **multi-layered cost-aware architecture** that combines sampling, compression, tiered retention, and intelligent data management to minimize costs while maintaining operational excellence.

## Cost-Aware Strategies

### 1. Intelligent Sampling

Sampling reduces data volume by collecting only a subset of telemetry data. Different sampling strategies are applied based on data type and criticality.

#### Trace Sampling

Distributed traces are the most expensive telemetry data type due to their size. We implement adaptive sampling to balance cost and visibility.

**Sampling Strategy:**
- **Error traces:** 100% sampling (all errors are captured)
- **Slow traces (> 1 second):** 100% sampling (performance issues are captured)
- **Normal traces:** 10% sampling (representative sample for baseline visibility)
- **Health check traces:** 1% sampling (minimal sampling for routine checks)

**Implementation:** OpenTelemetry SDK with head-based sampling configured per service.

**Cost Impact:** Reduces trace storage by 90% while maintaining full visibility into errors and performance issues.

#### Log Sampling

Logs are sampled based on log level to reduce storage costs while preserving critical information.

**Sampling Strategy:**
- **ERROR and FATAL:** 100% sampling (all errors are captured)
- **WARN:** 100% sampling (all warnings are captured)
- **INFO:** 100% sampling (important application events)
- **DEBUG:** 1% sampling (detailed debugging information, sampled)
- **TRACE:** 0.1% sampling (very detailed information, minimal sampling)

**Implementation:** Logger configuration with level-based sampling in all services.

**Cost Impact:** Reduces log storage by 50-70% depending on log level distribution.

#### Metrics Sampling

Metrics are less expensive than logs and traces but still require optimization.

**Sampling Strategy:**
- **Critical metrics (error rate, response time):** 15-second scrape interval
- **Standard metrics (request count, resource usage):** 30-second scrape interval
- **Low-priority metrics (cache hit rate, queue depth):** 60-second scrape interval

**Implementation:** Prometheus scrape configuration with per-job intervals.

**Cost Impact:** Reduces metrics storage by 30-50% compared to uniform 10-second scraping.

### 2. Tiered Retention Policies

Telemetry data is stored in tiered storage based on age and access frequency. Older data is moved to cheaper storage tiers or deleted.

#### Hot Storage (0-7 days)

Recent data is stored in fast, expensive storage (SSD) for real-time querying and alerting.

**Storage Type:** SSD-backed block storage  
**Access Pattern:** Frequent (real-time dashboards, alerts)  
**Cost:** High ($0.10-0.20/GB/month)

#### Warm Storage (7-30 days)

Older data is moved to slower, cheaper storage (HDD) for historical analysis.

**Storage Type:** HDD-backed block storage  
**Access Pattern:** Occasional (historical analysis, incident investigation)  
**Cost:** Medium ($0.03-0.05/GB/month)

#### Cold Storage (30-90 days)

Very old data is moved to object storage for long-term archival.

**Storage Type:** Object storage (S3, Azure Blob, GCS)  
**Access Pattern:** Rare (compliance, audits)  
**Cost:** Low ($0.01-0.02/GB/month)

#### Deletion (> 90 days)

Data older than 90 days is deleted unless required for compliance.

**Retention Policy:**
- **Logs:** 90 days (hot: 7, warm: 30, cold: 53)
- **Metrics:** 90 days (hot: 7, warm: 30, cold: 53)
- **Traces:** 30 days (hot: 7, warm: 23, cold: 0)

**Cost Impact:** Reduces storage costs by 60-80% compared to uniform hot storage.

### 3. Compression

All telemetry data is compressed before transmission and storage to reduce bandwidth and storage costs.

#### Log Compression

Logs are compressed using gzip before transmission and storage.

**Compression Ratio:** 5:1 to 10:1 (depending on log structure)  
**Implementation:** Promtail with gzip compression enabled  
**Cost Impact:** Reduces log storage and bandwidth by 80-90%

#### Metrics Compression

Prometheus uses efficient time-series compression (TSDB format).

**Compression Ratio:** 10:1 to 20:1 (depending on metric cardinality)  
**Implementation:** Native Prometheus TSDB compression  
**Cost Impact:** Reduces metrics storage by 90-95%

#### Trace Compression

Traces are compressed using gzip before storage.

**Compression Ratio:** 3:1 to 5:1 (depending on trace structure)  
**Implementation:** Jaeger with gzip compression enabled  
**Cost Impact:** Reduces trace storage by 70-80%

### 4. Batch Transmission

Telemetry data is batched and transmitted in bulk to reduce network overhead and bandwidth costs.

**Batch Configuration:**
- **Logs:** 10-second batches or 1MB, whichever comes first
- **Metrics:** 15-second scrape interval (natural batching)
- **Traces:** 5-second batches or 100 spans, whichever comes first

**Cost Impact:** Reduces network overhead by 30-50% compared to real-time transmission.

### 5. Local Buffering

Services buffer telemetry data locally during network outages to prevent data loss and reduce retransmission costs.

**Buffer Configuration:**
- **Buffer size:** 100MB per service
- **Buffer duration:** 1 hour maximum
- **Overflow behavior:** Drop oldest data first

**Cost Impact:** Prevents data loss and reduces retransmission costs during network instability.

### 6. Cardinality Control

High-cardinality metrics (metrics with many unique label combinations) are expensive to store and query. We enforce cardinality limits to prevent cost explosions.

**Cardinality Limits:**
- **Maximum labels per metric:** 10
- **Maximum unique label values:** 1000 per label
- **Maximum unique metric series:** 100,000 per service

**Enforcement:** Prometheus relabeling rules drop high-cardinality metrics.

**Cost Impact:** Prevents cardinality explosions that can increase costs by 10x or more.

### 7. Query Optimization

Inefficient queries can consume significant compute resources. We optimize queries to reduce costs.

**Query Optimization Strategies:**
- **Time range limits:** Queries limited to 7 days by default
- **Aggregation:** Pre-aggregate metrics where possible
- **Caching:** Cache frequently accessed queries (Grafana caching)
- **Rate limiting:** Limit query rate to prevent abuse

**Cost Impact:** Reduces query compute costs by 50-70%.

## Cost Estimates

### Small Deployment (< 1000 users, 5 services)

| Component | Volume | Cost/Month |
|-----------|--------|------------|
| Logs (10GB/month) | 10GB × $0.05 | $0.50 |
| Metrics (10K series) | 10K × $0.001 | $10.00 |
| Traces (100K traces/month) | 100K × $0.0001 | $10.00 |
| Storage (100GB) | 100GB × $0.03 | $3.00 |
| Compute (2 CPU, 4GB RAM) | 1 instance | $50.00 |
| **Total** | | **$73.50** |

### Medium Deployment (< 10,000 users, 20 services)

| Component | Volume | Cost/Month |
|-----------|--------|------------|
| Logs (100GB/month) | 100GB × $0.05 | $5.00 |
| Metrics (50K series) | 50K × $0.001 | $50.00 |
| Traces (1M traces/month) | 1M × $0.0001 | $100.00 |
| Storage (500GB) | 500GB × $0.03 | $15.00 |
| Compute (4 CPU, 8GB RAM) | 1 instance | $100.00 |
| **Total** | | **$270.00** |

### Large Deployment (> 10,000 users, 50 services)

| Component | Volume | Cost/Month |
|-----------|--------|------------|
| Logs (1TB/month) | 1TB × $0.05 | $50.00 |
| Metrics (200K series) | 200K × $0.001 | $200.00 |
| Traces (10M traces/month) | 10M × $0.0001 | $1,000.00 |
| Storage (2TB) | 2TB × $0.03 | $60.00 |
| Compute (8 CPU, 16GB RAM) | 1 instance | $200.00 |
| **Total** | | **$1,510.00** |

### Cost Comparison (Without Cost-Aware Strategies)

| Deployment Size | With Cost-Aware | Without Cost-Aware | Savings |
|-----------------|-----------------|---------------------|---------|
| Small | $73.50 | $300-500 | 75-85% |
| Medium | $270.00 | $1,000-1,500 | 73-82% |
| Large | $1,510.00 | $5,000-10,000 | 70-85% |

## Consequences

### Positive

The cost-aware architecture reduces observability costs by 70-85% compared to naive implementations while maintaining sufficient operational visibility.

**Cost Savings:** Significant cost savings enable the platform to remain competitive in cost-sensitive markets like Nigeria.

**Scalability:** Cost-aware strategies scale linearly with platform growth, preventing cost explosions.

**Operational Visibility:** Despite aggressive cost optimization, the platform maintains sufficient visibility to detect and diagnose issues.

### Negative

The cost-aware architecture introduces complexity and may reduce visibility in some scenarios.

**Reduced Visibility:** Sampling reduces visibility into normal operations. Rare issues may not be captured in sampled data.

**Operational Complexity:** Tiered retention, sampling, and compression require careful configuration and monitoring.

**Query Limitations:** Query time range limits may prevent long-term trend analysis.

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Sampling misses critical issues | High | 100% sampling for errors and slow requests |
| Data loss during network outages | Medium | Local buffering with 1-hour retention |
| Insufficient retention for compliance | High | Configurable retention policies per deployment |
| Query performance degradation | Medium | Query optimization and caching |

## Alternatives Considered and Rejected

**No Sampling:** Rejected due to prohibitively high costs (10x increase).

**Uniform Retention:** Rejected due to high storage costs for rarely accessed old data.

**No Compression:** Rejected due to high bandwidth and storage costs.

**Cloud-Native Observability (CloudWatch, Datadog):** Rejected due to very high per-log and per-metric pricing.

## References

- [Wave 5 Planning Package](https://github.com/webwakaagent1/webwaka-governance/blob/main/docs/planning/wave5/WAVE_5_PLANNING_PACKAGE.md)
- [ADR-001: Observability Stack Selection](./ADR-001-observability-stack-selection.md)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Loki Best Practices](https://grafana.com/docs/loki/latest/best-practices/)

## Approval

**Approved By:** WebWaka Infrastructure Team, Finance Team  
**Date:** February 1, 2026  
**Status:** ✅ Accepted

---

**Document Status:** Final  
**Last Updated:** February 1, 2026
