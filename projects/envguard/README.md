# envguard

**Type-safe, validated environment variables for Node.js — zero dependencies.**

- Full TypeScript inference, no manual type annotations needed
- Runtime validation with clear, actionable error messages
- All missing required variables reported in a single error
- Built-in `.env` file parsing
- Zero runtime dependencies

---

## Installation

```bash
npm install envguard
```

Requires **Node.js 18+**. Compile with `tsc` or use `--experimental-strip-types` on Node 22+.

---

## Quick Start

```typescript
import { guard } from 'envguard';

const env = guard({
  PORT:            { type: 'number',  default: 3000 },
  DATABASE_URL:    { type: 'url',     required: true },
  NODE_ENV:        { type: 'enum',    values: ['development', 'production', 'test'] as const, default: 'development' },
  ENABLE_LOGS:     { type: 'boolean', default: true },
  APP_NAME:        { type: 'string',  required: true },
  MAX_CONNECTIONS: { type: 'number',  min: 1, max: 100, default: 10 },
});

// TypeScript infers all types automatically:
env.PORT            // number
env.DATABASE_URL    // string
env.NODE_ENV        // 'development' | 'production' | 'test'
env.ENABLE_LOGS     // boolean
env.APP_NAME        // string
env.MAX_CONNECTIONS // number
```

Call `guard()` once at startup (e.g. in `src/config.ts`). If anything is wrong the process throws before serving a single request.

---

## .env File Support

```typescript
const env = guard(schema, { dotenv: true });
```

Reads `.env` from `process.cwd()` before checking `process.env`. Values already in `process.env` take precedence.

---

## API Reference

### Field Options

| Option | Types | Description |
|--------|-------|-------------|
| `type` | `'string' \| 'number' \| 'boolean' \| 'url' \| 'enum'` | **Required.** The value type |
| `required` | `boolean` | Throw when absent with no default |
| `default` | matching type | Fallback value |
| `description` | `string` | Shown in error messages |
| `min` / `max` | `number` | Range constraint (number only) |
| `values` | `readonly string[]` | Allowed values (enum only) |

---

## Error Messages

All missing fields reported in a single throw:

```
EnvGuardError: [envguard] Missing required environment variables:
  - DATABASE_URL (url): Database connection string
  - APP_NAME (string): Application display name
  - JWT_SECRET (string): A non-empty string value
```

Validation failures include what was received and what was expected:

```
EnvGuardError: [envguard] Validation failed for "NODE_ENV":
  Received: "staging"
  Expected: one of: "development", "production", "test"
```

---

## Comparison

| Feature | `dotenv` alone | `envguard` |
|---------|---------------|------------|
| Parses `.env` files | Yes | Yes |
| TypeScript types | No | Yes — full inference |
| Runtime validation | No | Yes |
| Missing field errors | Silent (`undefined`) | Throws with all fields listed |
| Type coercion | No | Yes |
| Zero dependencies | Yes | Yes |

---

## License

MIT
