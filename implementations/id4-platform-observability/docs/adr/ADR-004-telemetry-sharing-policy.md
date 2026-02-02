# ADR-004: Telemetry Sharing Policy

**Status:** ✅ Accepted  
**Date:** February 1, 2026  
**Decision Makers:** WebWaka Infrastructure Team, Governance Team  
**Consulted:** Legal Team, Privacy Team

## Context

The WebWaka platform supports partner-deployed and self-hosted deployment modes where partners and clients control their own infrastructure and data. WebWaka would benefit from receiving aggregate telemetry data from these deployments to improve the platform, identify bugs, and understand usage patterns. However, telemetry data may contain sensitive information, and partners and clients have legitimate privacy and data sovereignty concerns.

### Telemetry Value

Telemetry data from partner-deployed and self-hosted instances provides valuable insights that can improve the platform for all users.

**Platform Improvement:** Aggregate telemetry helps identify common issues, performance bottlenecks, and feature usage patterns.

**Bug Detection:** Error rates and stack traces help identify bugs that may not be present in the SaaS environment.

**Usage Analytics:** Understanding how features are used helps prioritize development and improve user experience.

**Performance Optimization:** Response time and resource usage data helps optimize performance.

### Privacy and Sovereignty Concerns

Partners and clients have legitimate concerns about sharing telemetry data with WebWaka.

**Sensitive Data:** Telemetry may contain sensitive business information (transaction volumes, user counts, feature usage).

**Competitive Intelligence:** Partners may view telemetry as competitive intelligence that should not be shared.

**Data Sovereignty:** Some jurisdictions require that data remain within specific geographic boundaries.

**Compliance:** GDPR, CCPA, and other regulations impose strict requirements on data sharing.

## Decision Drivers

1. **Privacy-First:** Respect partner and client privacy by default
2. **Opt-In Only:** Telemetry sharing must be explicitly enabled, not opt-out
3. **Anonymization:** All shared telemetry must be anonymized to prevent identification
4. **Transparency:** Partners and clients must understand exactly what data is shared
5. **Value Exchange:** Partners and clients should receive value in exchange for sharing telemetry
6. **Compliance:** Telemetry sharing must comply with all applicable data protection regulations

## Decision

We will implement an **opt-in telemetry sharing policy** with **strict anonymization** and **transparent disclosure** of what data is shared.

## Telemetry Sharing Policy

### Default Behavior

**Partner-Deployed:** Telemetry sharing is **disabled by default**. Partners must explicitly enable it.

**Self-Hosted:** Telemetry sharing is **disabled by default**. Clients must explicitly enable it.

**SaaS:** Not applicable (WebWaka controls all infrastructure and telemetry).

### Opt-In Mechanism

Partners and clients can enable telemetry sharing through a configuration setting.

**Configuration:**
```yaml
telemetry:
  sharing:
    enabled: false  # Default: disabled
    endpoint: https://telemetry.webwaka.com/v1/ingest
    interval: 3600  # Send telemetry every hour
    anonymization: strict  # strict | relaxed (strict is default)
```

**Enabling Telemetry Sharing:**
1. Partner/client reviews telemetry sharing documentation
2. Partner/client sets `telemetry.sharing.enabled: true` in configuration
3. Partner/client deploys updated configuration
4. Telemetry aggregator begins sending anonymized data to WebWaka

### What Data is Shared

Only **aggregate, anonymized** telemetry is shared. No raw logs, traces, or tenant-specific data is transmitted.

#### Metrics (Aggregate Only)

**Shared:**
- Total request count per hour
- Average response time per hour
- Error rate per hour
- Service uptime percentage
- Resource usage (CPU, memory, disk) averages

**Not Shared:**
- Per-tenant metrics
- Per-user metrics
- Absolute values (only aggregates and averages)
- High-cardinality metrics (e.g., per-endpoint metrics)

#### Logs (Error Statistics Only)

**Shared:**
- Error count per hour by error type (anonymized)
- Warning count per hour
- Log volume statistics

**Not Shared:**
- Raw log messages
- Log content
- Stack traces (unless explicitly anonymized)
- Any personally identifiable information (PII)

#### Traces (Statistics Only)

**Shared:**
- Average trace duration per hour
- Trace error rate per hour
- Service dependency graph (anonymized service names)

**Not Shared:**
- Raw traces
- Trace content
- Request/response payloads
- Any tenant or user identifiers

#### System Information (Non-Sensitive Only)

**Shared:**
- Platform version
- Deployment mode (partner-deployed or self-hosted)
- Geographic region (country-level only, e.g., "Nigeria", not city)
- Number of services deployed
- Number of active tenants (count only, no identifiers)

**Not Shared:**
- Partner or client identity
- Deployment-specific identifiers
- Infrastructure details (IP addresses, hostnames)
- Any information that could identify the partner or client

### Anonymization Strategy

All telemetry data is anonymized before transmission using a multi-layered approach.

#### Identifier Removal

All identifiers that could link telemetry to a specific partner, client, or tenant are removed.

**Removed:**
- Partner ID
- Client ID
- Tenant ID
- User ID
- Session ID
- IP addresses
- Hostnames
- Domain names

**Replaced With:** Random UUIDs that are regenerated daily (no cross-day correlation).

#### Aggregation

All metrics are aggregated to hourly or daily granularity to prevent fine-grained analysis.

**Example:** Instead of sending "100 requests at 10:00:00, 120 requests at 10:00:15", send "7200 requests between 10:00:00 and 11:00:00".

#### Sampling

Only a small sample (1-5%) of aggregate data is transmitted to minimize data volume and privacy risk.

#### Hashing

Any data that must be transmitted in non-aggregate form (e.g., error types) is hashed using SHA-256 with a daily rotating salt.

**Example:** Error type "DatabaseConnectionError" becomes "a3f8e9d2..." (hash changes daily).

### Transparency and Disclosure

Partners and clients receive full transparency into what data is shared.

#### Documentation

Comprehensive documentation explains:
- What data is shared
- What data is not shared
- How data is anonymized
- How data is used by WebWaka
- How to enable/disable telemetry sharing
- How to verify what data is being sent

#### Telemetry Dashboard

Partners and clients can view a dashboard showing exactly what telemetry data is being sent to WebWaka.

**Dashboard Features:**
- Real-time view of telemetry being transmitted
- Historical view of telemetry sent
- Ability to download telemetry data for audit
- Ability to disable telemetry sharing instantly

#### Audit Logs

All telemetry transmissions are logged locally for audit purposes.

**Audit Log Contents:**
- Timestamp of transmission
- Data volume transmitted
- Anonymization method used
- Transmission status (success/failure)

### Value Exchange

Partners and clients who enable telemetry sharing receive benefits in exchange.

**Benefits:**
- **Priority Support:** Faster response times for support requests
- **Early Access:** Early access to new features and beta releases
- **Platform Insights:** Aggregate platform insights and benchmarking data
- **Influence:** Greater influence on platform roadmap and feature prioritization

### Compliance

The telemetry sharing policy is designed to comply with major data protection regulations.

#### GDPR Compliance

**Lawful Basis:** Legitimate interest (platform improvement) with explicit consent (opt-in).

**Data Minimization:** Only aggregate, anonymized data is shared.

**Right to Erasure:** Partners and clients can disable telemetry sharing at any time, and all previously shared data will be deleted within 30 days.

**Data Protection Impact Assessment (DPIA):** A DPIA has been conducted and approved by the legal team.

#### CCPA Compliance

**Opt-In Consent:** Telemetry sharing requires explicit opt-in consent.

**Right to Opt-Out:** Partners and clients can opt-out at any time.

**Right to Deletion:** All shared telemetry data is deleted within 30 days of opt-out.

#### NDPR Compliance (Nigeria)

**Consent:** Telemetry sharing requires explicit consent.

**Data Localization:** Telemetry data is processed in Nigeria before transmission (if applicable).

**Right to Withdraw Consent:** Partners and clients can withdraw consent at any time.

## Implementation Details

### Telemetry Aggregator Component

A dedicated telemetry aggregator component is deployed in partner-deployed and self-hosted environments (optional, only if telemetry sharing is enabled).

**Responsibilities:**
- Collect telemetry from local observability infrastructure
- Anonymize and aggregate telemetry data
- Transmit telemetry to WebWaka telemetry receiver
- Provide local dashboard for transparency
- Generate audit logs

**Deployment:** Docker container or Kubernetes pod, deployed alongside observability stack.

### WebWaka Telemetry Receiver

A dedicated telemetry receiver service is deployed in the WebWaka SaaS environment.

**Responsibilities:**
- Receive telemetry from partner-deployed and self-hosted instances
- Validate anonymization (reject any non-anonymized data)
- Store telemetry in secure, isolated database
- Provide aggregate insights to WebWaka team
- Enforce retention policies (delete data after 90 days)

**Security:** TLS encryption, mutual authentication, rate limiting.

### Telemetry Data Retention

**Retention Period:** 90 days

**Deletion:** All telemetry data is automatically deleted after 90 days.

**Opt-Out Deletion:** If a partner or client disables telemetry sharing, all previously shared data is deleted within 30 days.

## Consequences

### Positive

The opt-in telemetry sharing policy with strict anonymization respects partner and client privacy while enabling WebWaka to improve the platform.

**Privacy Respected:** Partners and clients have full control over telemetry sharing.

**Transparency:** Partners and clients understand exactly what data is shared.

**Platform Improvement:** WebWaka receives valuable telemetry to improve the platform.

**Compliance:** The policy complies with major data protection regulations.

### Negative

The opt-in policy may result in low adoption rates, limiting the value of telemetry data.

**Low Adoption:** Many partners and clients may choose not to enable telemetry sharing.

**Incomplete Data:** Telemetry data may be biased toward partners who opt in.

**Operational Overhead:** Maintaining the telemetry aggregator and receiver adds operational complexity.

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Anonymization failure | High | Automated validation, reject non-anonymized data |
| Data breach | High | TLS encryption, secure storage, minimal retention |
| Low opt-in rate | Medium | Provide value exchange (priority support, early access) |
| Compliance violations | High | Legal review, DPIA, regular audits |

## Alternatives Considered and Rejected

**Opt-Out Telemetry:** Rejected because it violates privacy-first principles and may not comply with GDPR.

**No Telemetry Sharing:** Rejected because WebWaka would have no visibility into partner-deployed and self-hosted instances.

**Raw Telemetry Sharing:** Rejected because it violates privacy and data sovereignty requirements.

## References

- [GDPR Article 6 (Lawful Basis)](https://gdpr-info.eu/art-6-gdpr/)
- [CCPA Section 1798.100 (Consumer Rights)](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1798.100)
- [NDPR (Nigeria Data Protection Regulation)](https://nitda.gov.ng/ndpr/)
- [Wave 5 Planning Package](https://github.com/webwakaagent1/webwaka-governance/blob/main/docs/planning/wave5/WAVE_5_PLANNING_PACKAGE.md)
- [ADR-002: Multi-Deployment Mode Strategy](./ADR-002-multi-deployment-mode-strategy.md)

## Approval

**Approved By:** WebWaka Infrastructure Team, Governance Team, Legal Team  
**Date:** February 1, 2026  
**Status:** ✅ Accepted

---

**Document Status:** Final  
**Last Updated:** February 1, 2026
