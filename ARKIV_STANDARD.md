# Arkiv Standards (Spec v0.1)

**Spec version:** v0.1  
**Last updated:** 2025-12-18

The goal of this document is to consolidate naming conventions, attribute value formats, reference syntax, and base entity templates for Arkiv. 

This document is the canonical guide for cross-project Arkiv usage and should be referenced by implementations and indexers.

---

## Table of Contents

- [System Attributes](#system-attributes)
- [Custom Attributes](#custom-attributes)
  - [Attribute Names](#attribute-names)
    - [Postfix Naming Conventions](#postfix-naming-conventions)
  - [Attribute Values](#attribute-values)
    - [type / typeVersion](#type-attribute-usage)
    - [Arkiv references](#arkiv-references)
    - [ISO timestamps](#iso-timestamps-with-timezone)
    - [Arrays](#arrays-attribute-level)
    - [Location Encoding](#location-encoding-lat--long)
- [Base Entity Types](#base-entity-types)
  - [Why base entity types](#why-base-entity-types)
  - [Anti-patterns](#anti-patterns)
  - [Application extensions](#application-extensions)
- [Entity Mutation Semantics](#entity-mutation-semantics)
  - [Update semantics](#update-semantics)
  - [Attribute removal](#attribute-removal)
  - [System timestamps](#system-timestamps)
- [Change Log](#change-log)

---

## System Attributes

These **system attributes** are available for all Arkiv entities and are managed by Arkiv (typically read-only from application perspective). They do not need to be added explicitly to entity payloads or attributes in most cases.

- `$initialOwner` — initial owner (wallet)
- `$owner` — current owner (wallet)
- `$contentType` — MIME type for bytes stored in `payload` (e.g., `image/png`)
- `$createdAt` — authoritative creation timestamp
- `$lastUpdatedAt` — last updated timestamp
- `$expiresAt` — expiration timestamp (when applicable)


## Custom Attributes

Custom attributes are application-visible attributes you define on entities (as opposed to system attributes which are managed by Arkiv and prefixed with `$`). This section summarizes naming and value conventions for custom attributes; see **Attribute Values** elsewhere in this document for full details.

### Overview
- Custom attribute names MUST follow the attribute-name rules: start with a letter and contain only letters, numbers, underscores or hyphens (regex: `^[A-Za-z][A-Za-z0-9_-]*$`).
- Use **CamelCase** for attribute names (e.g., `displayName`, `profileImageUrl`).
- Distinguish attribute intent with postfixes: `*At` for timestamps, `*Url` for HTTP(S) links, `*Ref` for Arkiv references, `*Version` for numeric schema versions, `*Lat`/`*Long` for encoded coordinates.

### Naming (quick rules)
- Prefer short, descriptive names; avoid abbreviations.  
- Use singular names for single values and plural names for arrays/collections (e.g., `language` vs `languages`).
- Use boolean prefixes for flags (`is`, `has`, `can`).

### Value Formats (quick summary)
- **Strings**: default type for textual attributes (e.g., `displayName`).
- **URLs**: attributes with `Url` postfix must start with `http://` or `https://` and are UI-ready.
- **Arkiv refs**: attributes with `Ref` postfix should use canonical Arkiv ref syntax (`arkiv:[chain:]0x...#attr` or `#payload`) and must be validated before resolution.
- **Timestamps**: attributes with `At` postfix must be ISO 8601 strings including timezone (e.g., `2025-12-18T15:00:00Z`).
- **Arrays**: encode as bracketed comma-separated strings like `"[en,de]"` (simple tokens only) or store JSON in `payload` for complex structures.
- **Coordinates**: `*Lat` and `*Long` are integers encoded as microdegrees (scale = 1e6); use optional `*Decimal` strings for human readability.

### Examples (canonical)
- `displayName: "Alice Example"`
- `username: "alice"`
- `profileImageUrl: "https://cdn.example.com/alice.jpg"`
- `profileImageRef: "arkiv:#payload"`
- `createdAt: "2025-12-18T15:00:00Z"`
- `languages: "[en,de]"`
- `homeLat: 138856613`, `homeLong: 182352222`

See the **Attribute Values** section for full validation patterns, parsing guidance, and resolution semantics.

### Attribute Names

### General Guidelines

1. **Use CamelCase**
  - Start with a lowercase letter, capitalize subsequent words.  
  - Example: `displayName`, `profileImage`, `createdAt`.

2. **Avoid Abbreviations**
  - Use full, descriptive words instead of abbreviations to ensure clarity (e.g., `certifiedAt` not `crtAt`).

3. **Be Descriptive but Concise**
  - Attribute names should clearly describe their purpose without being overly verbose.  
  - Good: `profileImage`, `createdAt` — Avoid: `userProfileImageUrl`, `dateWhenCreated`.

4. **Use Consistent Case for Acronyms**
  - Treat acronyms as a single word in camelCase: `apiKey`, `userId` (avoid `APIKey`).

5. **Use Boolean Prefixes for Flags**
  - Prefer `is`, `has`, `can` prefixes: `isActive`, `hasProfileImage`, `canEdit`.

6. **Use Singular Names for Single-Value Attributes**
  - Good: `username`, `timezone` — Avoid: `usernames` (unless it’s an array).

7. **Use Plural Names for Arrays or Collections**
  - Good: `languages`, `contactLinks` — Avoid: `language` (if it’s an array).

8. **Use Standardized Prefixes for Related Attributes**
  - Group related attributes with consistent prefixes to improve clarity, e.g., `skillId`, `skillExpertise`.


#### Postfix Naming Conventions

1. **Arkiv References**:
    - `Ref` — use for Arkiv references that require resolution (e.g., `profileImageRef`, `mentorProfileRef`). 
    - Values follow canonical Arkiv ref syntax (`arkiv:[chain:]0x...#attr` or `#payload`) see below for details.

2. **Web-Link Attributes**:
    - `.*Url` — use for direct HTTP/HTTPS links safe to use in UI elements (e.g., `profileImageUrl`, `websiteUrl`). 
    - Values must start with `http://` or `https://`.

3. **Version Attributes**:
  - `.*Version` — use for numeric schema/versioning values scoped to an entity or attribute group (e.g., `typeVersion`).
  - Values must be positive integers. Bump the version when the payload schema changes in a non-backward-compatible way.
  - Legacy shorthand `typeV` is tolerated but prefer `typeVersion` for clarity.

4. **Timestamp Attributes**:
    - `.*At` — use for timestamp attributes (e.g., `createdAt`, `lastActiveAt`). Timestamps should be ISO timestamps including timezone info.

5. **Location Attributes**:
  - `.*Lat` and `.*Long` postfixes for geographic coordinates (e.g., `homeLat`, `homeLong`).
  - See **Attribute Values → Location Encoding** for encoding rules and examples.

---

### Attribute Values

This section covers common value types for attributes: how they should be formatted, validated, and resolved.

#### Arkiv references
- **Canonical syntax**:

```
arkiv:[<chainId>:]?[0x<entity-key>]?($|#)<attribute-name>
```

- **Details**:
  - `chainId` (optional) — numeric chain identifier for cross-chain references (decimal like `137` or hex like `0x89`).
  - `0x<entity-key>` (optional) — the Arkiv entity key (hex string). If omitted, the reference targets the current entity.
  - `$` — denotes a **system** attribute (e.g., `$payload`, `$owner`, `$createdAt`).
  - `#` — denotes a **user/custom** attribute (e.g., `#profileImage`, `#displayName`).

- **Attribute-name rules**:
  - Must start with a letter: `[A-Za-z]`
  - Can contain letters, numbers, underscores and hyphens: `[A-Za-z0-9_-]*`
  - Regex: `^[A-Za-z][A-Za-z0-9_-]*$`

- **Validation regex (example)**:
```
^arkiv:(?:(?:\d+|0x[0-9a-fA-F]+):)?(?:0x[0-9a-fA-F]+)?([$#])([A-Za-z][A-Za-z0-9_-]*)$
```

- **Resolution semantics**:
  - If `chainId` is present and differs from local chain, route the resolution to the specified chain.
  - If an entity key is present, fetch that entity; otherwise resolve against the current entity.
  - `$payload` returns raw bytes (respect size limits and content-type checks); other `$` attributes return system metadata; `#` attributes return user attribute values.

- **Security & implementation notes**:
  - Enforce validation and ACLs when resolving remote references.
  - **Prefer server-side resolution:** Arkiv references (especially `arkiv:#payload` and `arkiv:0x...#payload`) should be resolved server-side or via indexer APIs, not directly by clients. Server-side resolution enables:
    - Content-type validation and MIME type checks (`$contentType` validation)
    - Size limit enforcement
    - Security scanning for malicious content
    - CDN caching for images and assets
    - Consistent error handling and fallbacks
  - Avoid returning `$payload` raw to arbitrary clients; prefer server-side fetch, MIME checks, scanning, and CDN caching.
  - Maintain backward compatibility with simple forms like `#payload` and `arkiv:0x...`.

#### `type` attribute (usage)
- **Purpose**: identifies the entity type.
- **Value format**: Use **PascalCase** for `type` values (e.g., `UserProfile`, `Skill`, `Offer`).
- **Notes**: Keep values short and stable; treat them as semantic identifiers used in queries and UI routing.

#### `typeVersion` attribute (usage)
- **Purpose**: numeric schema/version for the entity payload and semantics.
- **Value format**: Positive integer (e.g., `1`, `2`). Prefer the attribute name `typeVersion`; `typeV` is supported as a legacy shorthand but less explicit.
- **Notes**: Increment `typeVersion` when making non-backward-compatible changes to the payload schema so clients and indexers can detect and handle different versions.

**Compatibility expectations:**

- Clients should ignore unknown attributes (forward compatibility)
- Clients should soft-fail on unknown `typeVersion` (show fallback UI, log warning, don't crash)
- Clients should handle missing `typeVersion` gracefully (assume version 1 for legacy entities)
- Indexers may support multiple versions concurrently
- Indexers should expose `typeVersion` in query results
- Indexers should not filter out entities based on unknown `typeVersion`

**Recommendation:** Always set `typeVersion: 1` on initial entity creation to enable future migrations without breaking existing clients.

#### Arrays (attribute-level)

Because Arkiv attributes are limited to strings or positive integers, we recommend a simple, compact convention for array-valued attributes encoded as strings.

- **Format**: a single string value enclosed in square brackets with elements separated by commas: `[elem1,elem2,elem3]`.
- **Element type**: elements are **strings** only (no nested arrays or objects). Prefer simple tokens (e.g., language codes, slugs).
- **Whitespace**: parsers **should** trim whitespace around elements; canonical storage should avoid spaces: use `[en,es,fr]` rather than `[ en, es, fr ]`.
- **Empty array**: use `[]`.
- **Escaping**: if elements may contain commas or brackets, store the array in the `payload` as JSON instead (or use a different attribute convention).

**When to use arrays-as-strings vs JSON payload:**

- Use arrays-as-strings for: language codes, tags, slugs, simple tokens
- Do not use arrays-as-strings for: user-authored content, ordered lists, nested structures, data requiring extensibility

For anything beyond simple tokens, prefer storing JSON in the entity `payload` and referencing it via a `Ref` attribute.

**Parsing guidance**:
- Validate that the value starts with `[` and ends with `]`.
- Remove the brackets, split on `,`, trim each element, and reject empty elements unless explicitly allowed.

**Example**:
- `languages: "[en,de]"`
- `contactTags: "[mentor,designer]"`

For richer or nested arrays, prefer storing JSON in the entity `payload` and reference it from a `Ref` attribute.

#### Timestamps (UTC)
- **Use**: For timestamp attributes (use `*At` postfix, e.g., `createdAt`).
- **Format**: ISO 8601 with timezone information (e.g., `2025-12-18T14:23:00Z` or `2025-12-18T15:23:00+01:00`).
- **Validation**: Parse with a robust ISO 8601 parser (do not rely on regex alone); store and display in local timezone as needed.

#### Location Encoding (Lat / Long)

Use the `Lat` and `Long` postfixes for geographic coordinates when encoding location as numerical attributes (e.g., `homeLat`, `homeLong`). Because Arkiv attributes can only be strings or positive integers, we recommend encoding coordinates as positive integers using a fixed scaling and offset scheme.

**Goals:** worldwide coverage, sub-1m resolution, numeric ordering, and reasonable human readability.

**Recommended encoding**:
- **Scale**: 1_000_000 (microdegrees). Resolution ≈ 0.11 m at equator.
- **Latitude**: `latInt = round((latitude_deg + 90.0) * 1_000_000)` → range 0..180_000_000
- **Longitude**: `longInt = round((longitude_deg + 180.0) * 1_000_000)` → range 0..360_000_000

**Decoding**:
- `latitude_deg = (latInt / 1_000_000) - 90.0`
- `longitude_deg = (longInt / 1_000_000) - 180.0`

**Human-readable alternative**: Store optional decimal-string attributes (e.g., `homeLatDecimal: "48.856613"`) with 6 decimal places to match the integer encoding.

**Ordering & composite keys**:
- Numeric comparison of `latInt` / `longInt` preserves geographic ordering per axis.
- For a single sortable key, either pad and concat (fixed-width strings) or compute `composite = latInt * 360_000_001 + longInt` (beware of numeric overflow in environments with limited integer width).

**Example**:
- Paris: lat 48.856613 → `latInt = round((48.856613 + 90) * 1e6) = 138856613`
- Paris: long 2.352222 → `longInt = round((2.352222 + 180) * 1e6) = 182352222`
- Store as: `homeLat: 138856613`, `homeLong: 182352222`, optionally `homeLatDecimal: "48.856613"`, `homeLongDecimal: "2.352222"`.
- Example field using remote attribute: `"profileImageRef": "arkiv:137:0x123abc...#profileImage"`



## Base Entity Types

Base entity types define a small set of entity types common to many possible use cases.

The goal of base entity types is support effective and efficient entity definitions for most frequently used entity types and support application neutral tooling.

### Why Base Entity Types

Base entity types serve as small, stable, and **application-neutral** schemas that multiple apps can rely on. Keeping base entities pure (i.e., free of app-specific attributes) has several advantages:

- **Isolation & Ownership** — App-specific data can live in separate entities with their own ACLs and lifecycle without affecting the canonical base entity.
- **Schema clarity** — Base types remain small and stable; apps can iterate quickly without risking schema pollution.
- **Reusability** — Other apps and indexers can consume and reason about base entities consistently, improving cross-app interoperability.
- **Versioning & migration** — App extensions can have independent `typeVersion`, enabling targeted migrations and compatibility handling.
- **Privacy & compliance** — Sensitive or app-specific user data remains separate and easier to delete/expire as required.

### Anti-patterns

The following patterns are common mistakes that cause bugs in production applications:

**Do not create new entities for mutable state**

Do not model mutable user state by creating new entities per edit. Reuse entity keys for mutable entities to preserve identity and references. Use `updateEntity()` (SDK v0.4.4+) with stable `entity_key` values for entities that represent mutable application state (profiles, preferences, notifications). Reserve the "create new entity per change" pattern only for true versioning scenarios where each version needs independent identity (e.g., document revisions, immutable audit logs).

**Do not store UI state on base entities**

Do not store UI state, per-user flags, or ephemeral interaction data on base entities. Base entities should remain app-neutral and reusable. Store UI state in app-specific extension entities that reference the base entity via a `Ref` attribute.

**Do not overload array-encoded attributes**

Arrays encoded as strings (e.g., `"[en,de]"`) are intended only for simple, indexable tokens (language codes, tags, slugs). Do not encode user-authored or ordered data this way. For richer or nested arrays, store JSON in the entity `payload` and reference it from a `Ref` attribute.

**Do not assume partial updates**

`updateEntity()` should be treated as a full replacement of the entity's **attribute set** (omitted attributes are not preserved). Applications must fetch current entity state, merge desired changes, and provide complete attribute set to `updateEntity()` to avoid accidental deletions.

**Do not resolve Arkiv references client-side**

Arkiv references (especially `arkiv:#payload` and `arkiv:0x...#payload`) should be resolved server-side or via indexer APIs, not directly by clients. Server-side resolution enables content-type validation, size limit enforcement, security scanning, and CDN caching.


### Base Entity Type: Profile

```json
{
  "type": "UserProfile",
  "typeVersion": 1,
  "displayName": "Alice Example",
  "username": "alice",
  "profileImageUrl": "https://cdn.example.com/alice.jpg",
  "profileImageRef": "arkiv:#payload",
  "timezone": "Europe/Berlin",
  "languages": "[en,de]"
}
```

### Profile attribute reference

| Attribute | Type | Required | Description | Notes |
|---|---:|---:|---|---|
| `type` | string | Yes | Always `UserProfile` | |
| `typeVersion` | number | Yes | Numeric schema/version for the payload shape | Positive integer; bump when making changes |
| `displayName` | string | Yes | Human-facing name | Short, friendly name shown in UIs |
| `username` | string | No | Mentionable, human-friendly identifier (e.g., `@alice`) | Prefer uniqueness enforced by indexer/registry; client-side checks can race |
| `profileImageUrl` | string | No | Direct HTTP(S) URL usable in UI `img` tags | Must start with `http://` or `https://` |
| `profileImageRef` | string | No | Arkiv reference ( eg `arkiv:#payload`) for image data | Resolve server-side, validate `$contentType` and size before publishing a CDN/HTTPS URL |
| `timezone` | string | Yes | IANA timezone (e.g., `Europe/Berlin`) | Required for scheduling & display |
| `languages` | string | No | Array encoded as bracketed string (e.g., `"[en,de]"`) | Use `[]` for empty array; prefer simple tokens like ISO codes |

**Note:** 

- System attributes like `$owner`, `$contentType`, and `$createdAt` are managed by Arkiv and do not need to be stored as custom attributes unless you have a specific reason.

### Application Extensions

Applications that need additional use case specific attributes should create a separate, app-specific entity that points to the base entity rather than adding attributes directly to the base type. This pattern keeps the base clean and makes app data portable.

**Recommended linking attribute**
- Use an attribute named `<baseType>Ref` (camelCase) to point to the base entity. For example, a MentorProfile extension that references a `UserProfile` would use `userProfileRef: "arkiv:0x123..."`.

**Example: MentorProfile (app extension)**
```json
{
  "type": "MentorProfile",
  "typeVersion": 1,
  "userProfileRef": "arkiv:0x123...",
  "mentorSkillIds": "[skill1,skill2]",
  "hourlyRate": 2000000000000
}
```

## Entity Mutation Semantics

This section clarifies how entity updates should be interpreted across Arkiv implementations.

### Update semantics

Updating an existing entity is a **semantic mutation of the same entity identity**, not the creation of a new entity. Applications should reuse the same entity key when modifying mutable state (for example, profiles, preferences, or notification state).

When an entity is updated, the **current entity state** (both attributes and payload) is replaced by the new state provided in the update. Omitted attributes are not preserved. If you want to preserve the existing payload, re-send it in the update call.

**Implication:** Applications should treat updates as full replacements of the entity’s attribute set and avoid assuming partial or merge-style updates.

### Attribute removal

Arkiv does not define a special deletion marker for individual attributes.

To remove an attribute from an entity, it should be omitted from the updated attribute set. Setting attributes to empty strings is discouraged, as empty values are semantically distinct from absence and may complicate indexing and client logic.

Historical transactions may still contain removed attributes; absence applies only to the current entity state.

### System timestamps

The system attribute `$lastUpdatedAt` reflects the most recent entity mutation of any kind. It should not be interpreted as a user-meaningful change indicator.

Applications that require semantic timestamps (for example, “last edited” or “last read”) should model them explicitly as custom attributes.

---

## Change Log

- **v0.1 (2025-12-18)** — Initial consolidation and formalization of naming, attribute value formats, Arkiv ref syntax, and the base `UserProfile` schema.
