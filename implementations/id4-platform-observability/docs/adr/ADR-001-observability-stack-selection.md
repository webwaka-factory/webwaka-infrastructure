# ADR-001: Observability Stack Selection

**Status:** ✅ Accepted  
**Date:** February 1, 2026  
**Decision Makers:** WebWaka Infrastructure Team  
**Consulted:** Platform Foundation Team

## Context

The WebWaka platform requires a comprehensive observability solution that supports logging, metrics, distributed tracing, and alerting across all deployment modes (SaaS, Partner-Deployed, Self-Hosted). The solution must be cost-effective for Nigeria-first operations, portable across cloud providers, and capable of handling multi-tenant workloads with strict tenant isolation.

## Decision Drivers

1. **Cost-Effectiveness:** Nigeria-first operations require minimal infrastructure costs
2. **Portability:** Must work across AWS, Azure, GCP, and on-premises deployments
3. **Multi-Tenant Support:** Strict tenant isolation is a platform invariant (INV-002)
4. **Open Source:** Avoid vendor lock-in and reduce licensing costs
5. **Proven Technology:** Use battle-tested tools with strong community support
6. **Ease of Operation:** Minimize operational complexity for partners and clients
7. **Scalability:** Support growth from small deployments to large-scale operations

## Options Considered

### Option A: Open-Source Stack (Prometheus + Grafana + Loki + Jaeger)

**Components:**
- **Metrics:** Prometheus
- **Visualization:** Grafana
- **Logging:** Loki
- **Tracing:** Jaeger
- **Alerting:** Alertmanager (part of Prometheus)

**Pros:**
- ✅ Fully open-source, no licensing costs
- ✅ Highly portable across all cloud providers and on-premises
- ✅ Strong community support and extensive documentation
- ✅ Proven at scale (used by CNCF, Kubernetes, and many enterprises)
- ✅ Native multi-tenancy support in Prometheus and Loki
- ✅ Low resource footprint (Loki is particularly lightweight)
- ✅ Easy to deploy with Docker Compose or Kubernetes

**Cons:**
- ⚠️ Requires self-management (no managed service for all components)
- ⚠️ Separate tools require integration and configuration
- ⚠️ Jaeger can be resource-intensive at scale

**Cost Estimate (Small Deployment):**
- Infrastructure: $50-100/month (2 CPU, 4GB RAM)
- Storage: $20-50/month (100GB)
- **Total: $70-150/month**

### Option B: Cloud-Native Stack (AWS CloudWatch + X-Ray)

**Components:**
- **Metrics:** CloudWatch Metrics
- **Visualization:** CloudWatch Dashboards
- **Logging:** CloudWatch Logs
- **Tracing:** AWS X-Ray
- **Alerting:** CloudWatch Alarms + SNS

**Pros:**
- ✅ Fully managed, minimal operational overhead
- ✅ Deep integration with AWS services
- ✅ Auto-scaling and high availability built-in
- ✅ Pay-as-you-go pricing

**Cons:**
- ❌ AWS-only, not portable to other clouds or on-premises
- ❌ High costs at scale (per-log, per-metric pricing)
- ❌ Vendor lock-in
- ❌ Limited multi-tenancy support (requires custom tagging and filtering)
- ❌ Not suitable for partner-deployed or self-hosted modes

**Cost Estimate (Small Deployment):**
- Metrics: $50-100/month (10,000 metrics)
- Logs: $100-200/month (10GB ingestion)
- Traces: $50-100/month (1M traces)
- **Total: $200-400/month**

### Option C: Hybrid Stack (Datadog / New Relic / Dynatrace)

**Components:**
- All-in-one observability platform (SaaS)

**Pros:**
- ✅ Fully managed, zero operational overhead
- ✅ Best-in-class UI and user experience
- ✅ Advanced features (AI-powered anomaly detection, APM)
- ✅ Multi-cloud support

**Cons:**
- ❌ Very high costs ($15-30 per host per month)
- ❌ Vendor lock-in
- ❌ Not suitable for partner-deployed or self-hosted modes
- ❌ Data privacy concerns (all telemetry sent to third-party SaaS)

**Cost Estimate (Small Deployment):**
- 10 hosts × $20/month = $200/month
- Additional costs for logs, traces, and custom metrics
- **Total: $300-500/month**

### Option D: Elastic Stack (ELK)

**Components:**
- **Metrics:** Metricbeat + Elasticsearch
- **Visualization:** Kibana
- **Logging:** Logstash/Filebeat + Elasticsearch
- **Tracing:** APM Server + Elasticsearch
- **Alerting:** Elasticsearch Alerting

**Pros:**
- ✅ Open-source (with paid features)
- ✅ Powerful search and analytics capabilities
- ✅ Unified platform for logs, metrics, and traces
- ✅ Strong community support

**Cons:**
- ❌ High resource requirements (Elasticsearch is memory-intensive)
- ❌ Complex to operate and tune
- ❌ Licensing changes (Elastic License, not fully open-source)
- ❌ Higher costs at scale due to resource requirements

**Cost Estimate (Small Deployment):**
- Infrastructure: $150-300/month (4 CPU, 8GB RAM minimum)
- Storage: $50-100/month (200GB)
- **Total: $200-400/month**

## Decision

**Selected Option: A - Open-Source Stack (Prometheus + Grafana + Loki + Jaeger)**

## Rationale

The open-source stack is the clear winner for the WebWaka platform based on the following analysis:

### 1. Cost-Effectiveness (Critical for Nigeria-First)
- **Lowest total cost of ownership:** $70-150/month vs. $200-500/month for alternatives
- **No per-metric or per-log pricing:** Predictable costs as the platform scales
- **Minimal resource footprint:** Loki is significantly lighter than Elasticsearch

### 2. Portability (Critical for Multi-Deployment Modes)
- **Works everywhere:** AWS, Azure, GCP, on-premises, bare metal
- **No cloud provider lock-in:** Partners and clients can deploy anywhere
- **Standard deployment models:** Docker Compose, Kubernetes, systemd

### 3. Multi-Tenancy (Platform Invariant INV-002)
- **Native support:** Prometheus and Loki have built-in label-based multi-tenancy
- **Tenant isolation:** Query filters enforce strict tenant separation
- **No custom development required:** Multi-tenancy works out-of-the-box

### 4. Operational Simplicity
- **Well-documented:** Extensive community documentation and examples
- **Battle-tested:** Used by Kubernetes, CNCF, and thousands of enterprises
- **Easy to troubleshoot:** Large community for support

### 5. Scalability
- **Proven at scale:** Prometheus handles millions of metrics, Loki handles terabytes of logs
- **Horizontal scaling:** All components can scale horizontally
- **Efficient storage:** Prometheus uses TSDB, Loki uses object storage

### 6. Alignment with Platform Values
- **Open-source first:** Aligns with WebWaka's commitment to open standards
- **Privacy-first:** No third-party SaaS, all data stays under control
- **Community-driven:** Strong ecosystem and community support

## Implementation Details

### Component Selection

| Component | Tool | Version | Purpose |
|-----------|------|---------|---------|
| Metrics | Prometheus | 2.45+ | Time-series metrics storage and querying |
| Visualization | Grafana | 10.0+ | Dashboards and visualization |
| Logging | Loki | 2.9+ | Log aggregation and querying |
| Tracing | Jaeger | 1.50+ | Distributed tracing |
| Alerting | Alertmanager | 0.26+ | Alert routing and management |
| Exporters | Node Exporter, Custom | Latest | Infrastructure and business metrics |

### Deployment Architecture

#### SaaS Mode
- Centralized Prometheus, Loki, Jaeger, Grafana
- All services send telemetry to central observability cluster
- High availability with replication and load balancing

#### Partner-Deployed Mode
- Partner deploys full observability stack in their infrastructure
- Optional telemetry forwarding to WebWaka (opt-in)
- Partner-controlled dashboards and alerts

#### Self-Hosted Mode
- Client deploys full observability stack in their infrastructure
- No telemetry sharing with WebWaka
- Client-controlled dashboards and alerts

### Cost Optimization Strategies

1. **Sampling:** 10% trace sampling, 1% debug log sampling
2. **Retention:** Tiered storage (hot/warm/cold)
3. **Compression:** gzip compression for all telemetry
4. **Aggregation:** Pre-aggregate metrics where possible
5. **Efficient Queries:** Optimize Prometheus and Loki queries

## Consequences

### Positive

- ✅ **Low cost:** Minimal infrastructure and zero licensing costs
- ✅ **High portability:** Works across all deployment modes
- ✅ **Strong multi-tenancy:** Native support for tenant isolation
- ✅ **Operational simplicity:** Well-documented and widely used
- ✅ **Scalability:** Proven at large scale
- ✅ **Privacy:** No third-party data sharing

### Negative

- ⚠️ **Self-managed:** Requires operational expertise (mitigated by strong documentation)
- ⚠️ **Integration overhead:** Multiple tools require configuration (mitigated by automation)
- ⚠️ **Limited advanced features:** No AI-powered anomaly detection (acceptable for Phase 1)

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Operational complexity | Medium | Provide comprehensive runbooks and automation |
| Component failures | High | Deploy with high availability and monitoring |
| Resource exhaustion | Medium | Implement cost-aware sampling and retention policies |
| Skill gap | Low | Extensive community documentation and training materials |

## Alternatives Considered and Rejected

- **CloudWatch:** Rejected due to vendor lock-in and high costs
- **Datadog/New Relic:** Rejected due to very high costs and vendor lock-in
- **Elastic Stack:** Rejected due to high resource requirements and licensing concerns

## References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [CNCF Observability Landscape](https://landscape.cncf.io/card-mode?category=observability-and-analysis)
- [Wave 5 Planning Package](https://github.com/webwakaagent1/webwaka-governance/blob/main/docs/planning/wave5/WAVE_5_PLANNING_PACKAGE.md)

## Approval

**Approved By:** WebWaka Infrastructure Team  
**Date:** February 1, 2026  
**Status:** ✅ Accepted

---

**Document Status:** Final  
**Last Updated:** February 1, 2026
