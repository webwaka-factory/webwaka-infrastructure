# Global Expansion & Multi-Region API Documentation

## Overview

The Global Expansion & Multi-Region API provides comprehensive endpoints for managing multi-region deployments, data residency policies, data classification, and cross-border access controls.

**Base URL:** `http://localhost:8000/api/v1`

**API Version:** 1.0.0

## Authentication

Currently, the API does not require authentication. In production, implement OAuth 2.0 or JWT-based authentication.

## Response Format

All responses are in JSON format. Successful responses include the requested data, while error responses include an error message.

## Region Management Endpoints

### List Regions

**GET** `/regions`

List all configured regions.

**Response (200 OK):**
```json
[
  {
    "id": "region-us-east-1",
    "name": "US East (N. Virginia)",
    "aws_region": "us-east-1",
    "country_code": "US",
    "status": "active",
    "created_at": "2024-01-30T10:00:00Z",
    "updated_at": "2024-01-30T10:00:00Z"
  }
]
```

### Create Region

**POST** `/regions`

Register a new region.

**Request Body:**
```json
{
  "name": "US East (N. Virginia)",
  "aws_region": "us-east-1",
  "country_code": "US",
  "data_center_location": "Virginia, USA",
  "availability_zones": ["us-east-1a", "us-east-1b", "us-east-1c"]
}
```

### Get Region

**GET** `/regions/{region_id}`

Get region details.

### Update Region

**PUT** `/regions/{region_id}`

Update region configuration.

### Delete Region

**DELETE** `/regions/{region_id}`

Remove a region.

## Data Residency Endpoints

### List Residency Modes

**GET** `/residency/modes`

List available residency modes.

### Create Residency Policy

**POST** `/residency/policies`

Create a data residency policy.

**Request Body:**
```json
{
  "name": "EU Data Residency",
  "residency_mode": "regional",
  "policy_type": "mandatory",
  "allowed_regions": ["eu-west-1", "eu-central-1"]
}
```

### Get Residency Policy

**GET** `/residency/policies/{policy_id}`

Get policy details.

### List Residency Policies

**GET** `/residency/policies`

List all residency policies.

### Update Residency Policy

**PUT** `/residency/policies/{policy_id}`

Update a policy.

### Delete Residency Policy

**DELETE** `/residency/policies/{policy_id}`

Delete a policy.

## Data Classification Endpoints

### List Classification Levels

**GET** `/classification/levels`

List available classification levels.

### Classify Data

**POST** `/data/classify`

Classify data at creation time.

**Request Body:**
```json
{
  "data_id": "data-12345",
  "classification_level": "identity",
  "data_type": "user_profile",
  "sensitivity": "high",
  "pii_present": true,
  "encryption_required": true
}
```

### Get Data Classification

**GET** `/data/{data_id}/classification`

Get classification for data.

### Update Data Classification

**PUT** `/data/{data_id}/classification`

Update data classification.

## Cross-Border Access Control Endpoints

### Create Access Request

**POST** `/access/request`

Request cross-border access.

**Request Body:**
```json
{
  "data_id": "data-456",
  "target_region": "eu-west-1",
  "access_type": "read",
  "reason": "Customer support investigation"
}
```

### Get Access Request

**GET** `/access/requests/{request_id}`

Get access request status.

### List Access Requests

**GET** `/access/requests`

List all access requests.

### Approve Access Request

**POST** `/access/approve`

Approve an access request.

**Request Body:**
```json
{
  "request_id": "access-req-001",
  "approved": true,
  "reason": "Approved for customer support"
}
```

### Revoke Access

**POST** `/access/revoke`

Revoke an access grant.

**Request Body:**
```json
{
  "grant_id": "grant-001"
}
```

### Get Access Audit Logs

**GET** `/access/audit`

Get access audit logs with optional filters.

**Query Parameters:**
- `user_id` (optional): Filter by user
- `data_id` (optional): Filter by data
- `action` (optional): Filter by action type

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
  "detail": "Region not found"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. In production, implement rate limiting to prevent abuse.

## Webhooks

Webhook support for region and access events is planned for a future release.

## SDKs

SDKs for popular languages are planned for a future release.
