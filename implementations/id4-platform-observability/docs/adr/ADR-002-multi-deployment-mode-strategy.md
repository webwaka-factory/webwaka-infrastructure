# ADR-002: Multi-Deployment Mode Strategy

**Status:** ✅ Accepted  
**Date:** February 1, 2026  
**Decision Makers:** WebWaka Infrastructure Team  
**Consulted:** Platform Foundation Team, Governance Team

## Context

The WebWaka platform supports three distinct deployment modes, each with different operational ownership, data residency requirements, and privacy expectations. The observability infrastructure must support all three modes while respecting the unique characteristics and constraints of each.

### Deployment Modes

**SaaS (Shared Multi-Tenant):** WebWaka operates a centralized platform serving multiple tenants. All infrastructure, including observability, is owned and managed by WebWaka. Telemetry data is centralized for operational efficiency.

**Partner-Deployed (White-Label):** Partners deploy the WebWaka platform in their own infrastructure under their brand. Partners own and control all infrastructure, including observability. Partners may optionally share telemetry with WebWaka to improve the platform.

**Self-Hosted (Enterprise):** Enterprise clients deploy the WebWaka platform in their own infrastructure for maximum control and data residency compliance. Clients own and control all infrastructure. No telemetry is shared with WebWaka by default.

## Decision Drivers

1. **Data Sovereignty:** Partners and clients must have full control over their telemetry data
2. **Privacy:** Telemetry sharing must be opt-in, not opt-out
3. **Operational Independence:** Partners and clients must be able to operate without WebWaka involvement
4. **Platform Improvement:** WebWaka benefits from aggregate telemetry to improve the platform
5. **Simplicity:** Each deployment mode should be as simple as possible to deploy and operate
6. **Consistency:** The observability experience should be consistent across all modes

## Decision

We will implement a **decentralized observability architecture** with **optional telemetry aggregation** for partner-deployed and self-hosted modes.

### Architecture Overview

#### SaaS Mode (Centralized)

All services send telemetry to a centralized observability cluster managed by WebWaka. This cluster provides dashboards, alerting, and operational insights for the WebWaka operations team.

**Telemetry Flow:**
```
Service → Prometheus/Loki/Jaeger (WebWaka-managed) → Grafana (WebWaka-managed)
```

**Characteristics:**
- Centralized observability infrastructure
- All telemetry data stored in WebWaka-controlled systems
- Alerts routed to WebWaka operations team
- Multi-tenant isolation via labels (tenant_id)
- WebWaka responsible for all operational decisions

#### Partner-Deployed Mode (Decentralized with Optional Aggregation)

Partners deploy a complete observability stack in their own infrastructure. All telemetry data is stored and processed in partner-controlled systems. Partners may optionally forward aggregate, anonymized telemetry to WebWaka for platform improvement.

**Telemetry Flow (Without Aggregation):**
```
Service → Prometheus/Loki/Jaeger (Partner-managed) → Grafana (Partner-managed)
```

**Telemetry Flow (With Opt-In Aggregation):**
```
Service → Prometheus/Loki/Jaeger (Partner-managed) → Grafana (Partner-managed)
                                                   ↓
                                    Telemetry Aggregator (anonymizes, samples)
                                                   ↓
                               WebWaka Telemetry Receiver (opt-in)
```

**Characteristics:**
- Partner-controlled observability infrastructure
- All raw telemetry data stays in partner systems
- Alerts routed to partner operations team
- Optional telemetry forwarding (aggregate, anonymized, sampled)
- Partner responsible for all operational decisions
- WebWaka provides support but does not have direct access

#### Self-Hosted Mode (Fully Decentralized)

Clients deploy a complete observability stack in their own infrastructure. All telemetry data is stored and processed in client-controlled systems. No telemetry is shared with WebWaka by default.

**Telemetry Flow:**
```
Service → Prometheus/Loki/Jaeger (Client-managed) → Grafana (Client-managed)
```

**Characteristics:**
- Client-controlled observability infrastructure
- All telemetry data stays in client systems
- Alerts routed to client operations team
- No telemetry sharing with WebWaka (privacy-first)
- Client responsible for all operational decisions
- WebWaka provides documentation but no operational support

## Implementation Details

### Deployment Templates

Each deployment mode will have a dedicated deployment template that includes all necessary configuration, scripts, and documentation.

#### SaaS Template

The SaaS template deploys a centralized, high-availability observability cluster with multi-tenant isolation.

**Components:**
- Prometheus (3 replicas, federated)
- Loki (3 replicas, S3 backend)
- Jaeger (3 replicas, Elasticsearch backend)
- Grafana (2 replicas, PostgreSQL backend)
- Alertmanager (3 replicas, clustered)

**Deployment:**
- Kubernetes-based deployment
- Helm charts for all components
- Automated backup and disaster recovery
- High availability and load balancing

**Configuration:**
- Multi-tenant label enforcement
- Centralized alert routing
- WebWaka-specific dashboards

#### Partner-Deployed Template

The partner-deployed template provides a complete, self-contained observability stack that partners can deploy in their own infrastructure.

**Components:**
- Prometheus (1-3 replicas, configurable)
- Loki (1-3 replicas, configurable storage backend)
- Jaeger (1-3 replicas, configurable backend)
- Grafana (1-2 replicas, configurable backend)
- Alertmanager (1-3 replicas, configurable)
- Optional: Telemetry Aggregator (for opt-in sharing)

**Deployment:**
- Docker Compose or Kubernetes
- Terraform/CloudFormation for cloud deployments
- Ansible playbooks for on-premises deployments
- Automated installation scripts

**Configuration:**
- Partner-specific branding in Grafana
- Partner-controlled alert routing
- Optional telemetry aggregator configuration

#### Self-Hosted Template

The self-hosted template is identical to the partner-deployed template but without the telemetry aggregator component.

**Components:**
- Prometheus (1-3 replicas, configurable)
- Loki (1-3 replicas, configurable storage backend)
- Jaeger (1-3 replicas, configurable backend)
- Grafana (1-2 replicas, configurable backend)
- Alertmanager (1-3 replicas, configurable)

**Deployment:**
- Same options as partner-deployed template
- Simplified configuration (no aggregator)

**Configuration:**
- Client-specific branding in Grafana
- Client-controlled alert routing
- No external telemetry transmission

### Telemetry Aggregation (Opt-In)

For partners who choose to share telemetry with WebWaka, a telemetry aggregator component will anonymize, aggregate, and sample telemetry data before transmission.

**Aggregation Strategy:**

**Metrics:** Only aggregate metrics (e.g., request count, average response time) are forwarded. No raw metrics or tenant-specific data is shared.

**Logs:** No logs are forwarded. Only error counts and error types (anonymized) are shared.

**Traces:** Only trace statistics (e.g., average span duration, error rate) are forwarded. No raw traces or tenant-specific data is shared.

**Anonymization:** All tenant identifiers, user identifiers, and personally identifiable information (PII) are removed before transmission.

**Sampling:** Only 1% of aggregate data is forwarded to minimize bandwidth and storage costs.

**Opt-In Mechanism:** Partners must explicitly enable telemetry sharing via configuration. It is disabled by default.

### Alert Routing

Alert routing is deployment-mode-specific to ensure alerts reach the appropriate operations team.

#### SaaS Mode
- All alerts routed to WebWaka operations team
- Email, Slack, PagerDuty integration
- 24/7 on-call rotation

#### Partner-Deployed Mode
- All alerts routed to partner operations team
- Partner-configured channels (email, Slack, etc.)
- Optional escalation to WebWaka support (partner-controlled)

#### Self-Hosted Mode
- All alerts routed to client operations team
- Client-configured channels (email, Slack, etc.)
- No WebWaka involvement

### Data Residency Compliance (INV-007)

Observability data is subject to the same data residency requirements as application data.

**SaaS Mode:** Observability data is stored in the same region as the tenant's application data. Multi-region deployments have region-specific observability clusters.

**Partner-Deployed Mode:** Partners deploy observability infrastructure in the same region as their application infrastructure. Data residency is partner-controlled.

**Self-Hosted Mode:** Clients deploy observability infrastructure in the same region as their application infrastructure. Data residency is client-controlled.

## Consequences

### Positive

The decentralized architecture with optional aggregation provides maximum flexibility and control for partners and clients while still enabling WebWaka to improve the platform through aggregate telemetry.

**For WebWaka:** Aggregate telemetry from opt-in partners provides valuable insights for platform improvement without violating privacy or data sovereignty requirements.

**For Partners:** Full control over observability infrastructure and telemetry data. Optional telemetry sharing enables partners to contribute to platform improvement while maintaining privacy.

**For Clients:** Complete data sovereignty and privacy. No telemetry sharing with WebWaka. Full operational independence.

### Negative

The decentralized architecture increases operational complexity for WebWaka, as each deployment mode requires separate deployment templates, documentation, and support processes.

**Operational Overhead:** WebWaka must maintain three separate deployment templates and provide support for partner-deployed and self-hosted modes.

**Limited Visibility:** WebWaka has limited visibility into partner-deployed and self-hosted instances, making it harder to diagnose issues and provide support.

**Telemetry Fragmentation:** Aggregate telemetry from opt-in partners may be incomplete or biased, as not all partners will choose to share data.

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Partners misconfigure observability | High | Provide comprehensive deployment guides and validation scripts |
| Clients lack expertise to operate observability stack | Medium | Provide detailed documentation and optional paid support |
| Telemetry aggregation violates privacy | High | Strict anonymization and opt-in only |
| WebWaka lacks visibility for support | Medium | Provide diagnostic tools and encourage opt-in telemetry sharing |

## Alternatives Considered and Rejected

**Centralized Observability for All Modes:** Rejected because it violates data sovereignty and privacy requirements for partner-deployed and self-hosted modes.

**No Telemetry Aggregation:** Rejected because WebWaka would have no visibility into partner-deployed and self-hosted instances, making platform improvement difficult.

**Opt-Out Telemetry Sharing:** Rejected because it violates privacy-first principles and may not comply with data protection regulations (GDPR, CCPA).

## References

- [Wave 5 Planning Package](https://github.com/webwakaagent1/webwaka-governance/blob/main/docs/planning/wave5/WAVE_5_PLANNING_PACKAGE.md)
- [INV-002: Strict Tenant Isolation](https://github.com/webwakaagent1/webwaka-governance/blob/main/docs/invariants/INV-002.md)
- [INV-007: Data Residency as Declarative Governance](https://github.com/webwakaagent1/webwaka-governance/blob/main/docs/invariants/INV-007.md)

## Approval

**Approved By:** WebWaka Infrastructure Team, Governance Team  
**Date:** February 1, 2026  
**Status:** ✅ Accepted

---

**Document Status:** Final  
**Last Updated:** February 1, 2026
