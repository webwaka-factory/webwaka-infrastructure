# ADR-003: Version Pinning Mechanism

**Status:** Accepted

**Date:** 2024-01-30

**Author:** Manus AI

## Context

The system must support version pinning at three levels:

- **Platform Level:** Pin the platform version
- **Suite Level:** Pin individual suite versions
- **Capability Level:** Pin individual capability versions

Pins must be instance-specific, have optional expiration dates, and support reasons for audit purposes.

## Decision

We have implemented a **Version Pinner** component that manages version pins with the following features:

### Pin Storage

Each pin contains:
- Unique pin ID
- Instance ID (scope)
- Component type (platform, suite, capability)
- Component name
- Pinned version string
- Optional reason for pinning
- Optional expiration date
- Creation timestamp

### Pin Resolution

When resolving versions for a deployment:

1. Check if a pin exists for the component
2. If pin exists and not expired, use pinned version
3. If pin exists and expired, remove it and continue
4. If no pin, use manifest-specified version

### Pin Lifecycle

Pins can be created, queried, and deleted. Expired pins are automatically removed during queries.

## Rationale

This approach provides:

1. **Granular Control:** Pins at multiple component levels
2. **Temporal Flexibility:** Optional expiration dates for temporary pins
3. **Auditability:** Reasons are stored for compliance
4. **Automatic Cleanup:** Expired pins are removed automatically
5. **Isolation:** Pins are instance-specific

## Consequences

### Positive
- Fine-grained version control
- Audit trail via pin reasons
- Automatic expiration handling
- Simple implementation

### Negative
- Pin conflicts possible (e.g., platform pin conflicts with suite pin)
- Requires careful dependency management
- Expiration checking adds overhead

## Alternatives Considered

1. **Global Version Locks:** Simpler but less flexible, affects all instances
2. **Constraint-Based Versioning:** More expressive but significantly more complex
3. **Semantic Versioning Ranges:** More flexible but harder to enforce

## Conflict Resolution

When pin conflicts occur (e.g., pinned platform version incompatible with pinned suite version), the deployment validation will fail with a clear error message indicating the conflict.

## Related ADRs

- ADR-001: Deployment Engine Architecture
- ADR-005: Version Compatibility Checking
