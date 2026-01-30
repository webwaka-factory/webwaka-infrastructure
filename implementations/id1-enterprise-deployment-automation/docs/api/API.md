# Enterprise Deployment Automation API Documentation

## Overview

The Enterprise Deployment Automation API provides comprehensive endpoints for managing deployments, policies, versions, security patches, and rollback operations.

**Base URL:** `http://localhost:8000/api/v1`

**API Version:** 1.0.0

## Authentication

Currently, the API does not require authentication. In production, implement OAuth 2.0 or JWT-based authentication.

## Response Format

All responses are in JSON format. Successful responses include the requested data, while error responses include an error message.

## Deployment Endpoints

### Create Deployment

**POST** `/deployments`

Create a new deployment for an enterprise instance.

**Request Body:**
```json
{
  "manifest_id": "manifest-001",
  "instance_id": "instance-prod-01",
  "dry_run": false,
  "skip_validation": false
}
```

**Response (201 Created):**
```json
{
  "id": "deploy-001",
  "status": "pending",
  "manifest_id": "manifest-001",
  "instance_id": "instance-prod-01",
  "created_at": "2024-01-30T10:00:00Z",
  "started_at": null,
  "completed_at": null,
  "error_message": null
}
```

### Get Deployment

**GET** `/deployments/{deployment_id}`

Retrieve deployment details by ID.

**Response (200 OK):**
```json
{
  "id": "deploy-001",
  "status": "deployed",
  "manifest_id": "manifest-001",
  "instance_id": "instance-prod-01",
  "created_at": "2024-01-30T10:00:00Z",
  "started_at": "2024-01-30T10:05:00Z",
  "completed_at": "2024-01-30T10:15:00Z",
  "error_message": null
}
```

### List Deployments

**GET** `/deployments?instance_id={instance_id}`

List deployments, optionally filtered by instance.

**Response (200 OK):**
```json
[
  {
    "id": "deploy-001",
    "status": "deployed",
    "manifest_id": "manifest-001",
    "instance_id": "instance-prod-01",
    "created_at": "2024-01-30T10:00:00Z",
    "started_at": "2024-01-30T10:05:00Z",
    "completed_at": "2024-01-30T10:15:00Z",
    "error_message": null
  }
]
```

## Policy Endpoints

### Create Policy

**POST** `/policies?instance_id={instance_id}&policy_type={type}&description={desc}`

Create an update channel policy for an instance.

**Query Parameters:**
- `instance_id` (required): Instance ID
- `policy_type` (required): One of `auto_update`, `manual_approval`, `frozen`
- `description` (optional): Policy description

**Response (201 Created):**
```json
{
  "id": "policy-001",
  "instance_id": "instance-prod-01",
  "policy_type": "manual_approval",
  "enabled": true,
  "description": "Production instance requires manual approval",
  "created_at": "2024-01-30T10:00:00Z",
  "updated_at": "2024-01-30T10:00:00Z"
}
```

### Get Policy

**GET** `/policies/{policy_id}`

Retrieve policy details by ID.

### List Policies

**GET** `/policies?instance_id={instance_id}`

List policies, optionally filtered by instance.

### Update Policy

**PUT** `/policies/{policy_id}`

Update an existing policy.

### Delete Policy

**DELETE** `/policies/{policy_id}`

Delete a policy.

## Version Endpoints

### List Versions

**GET** `/versions?component_type={type}&component_name={name}`

List available versions, optionally filtered by component.

### Pin Version

**POST** `/versions/pin?instance_id={instance_id}`

Pin a version for an instance.

**Request Body:**
```json
{
  "component_type": "suite",
  "component_name": "commerce",
  "pinned_version": "1.5.0",
  "reason": "Compatibility with legacy system"
}
```

### Unpin Version

**DELETE** `/versions/pin/{pin_id}`

Remove a version pin.

### Get Instance Pins

**GET** `/versions/pins/{instance_id}`

Get all version pins for an instance.

### Check Compatibility

**POST** `/versions/compatibility`

Check version compatibility.

**Request Body:**
```json
{
  "platform_version": "2.0.0",
  "suites": {
    "commerce": "1.5.0",
    "mlas": "1.2.0"
  },
  "capabilities": {
    "reporting": "1.0.0"
  }
}
```

## Security Patch Endpoints

### List Patches

**GET** `/security/patches?component_type={type}&component_name={name}`

List available security patches.

### Get Critical Patches

**GET** `/security/patches/critical`

Get all critical security patches.

### Apply Patch

**POST** `/security/patches/apply?instance_id={instance_id}`

Apply a security patch to an instance.

**Request Body:**
```json
{
  "patch_id": "patch-001",
  "dry_run": false,
  "force": false
}
```

### Get Patch Status

**GET** `/security/patches/status/{instance_id}`

Get patch status for an instance.

## Rollback Endpoints

### Initiate Rollback

**POST** `/rollback?instance_id={instance_id}`

Initiate a rollback operation.

**Request Body:**
```json
{
  "to_manifest_id": "manifest-001",
  "reason": "Deployment caused performance degradation",
  "dry_run": false,
  "skip_validation": false
}
```

### Get Rollback

**GET** `/rollback/{rollback_id}`

Retrieve rollback details by ID.

### Get Rollback History

**GET** `/rollback/history/{instance_id}`

Get rollback history for an instance.

### List Rollbacks

**GET** `/rollback?instance_id={instance_id}`

List rollback operations, optionally filtered by instance.

## Error Handling

The API returns appropriate HTTP status codes:

- **200 OK:** Successful GET request
- **201 Created:** Successful POST request
- **204 No Content:** Successful DELETE request
- **400 Bad Request:** Invalid request parameters
- **404 Not Found:** Resource not found
- **500 Internal Server Error:** Server error

Error responses include a detail message:

```json
{
  "detail": "Deployment not found"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. In production, implement rate limiting to prevent abuse.

## Webhooks

Webhook support for deployment events is planned for a future release.

## SDKs

SDKs for popular languages are planned for a future release.
