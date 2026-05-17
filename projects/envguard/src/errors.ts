/**
 * Custom error class for envguard validation failures.
 */
export class EnvGuardError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'EnvGuardError';
    Object.setPrototypeOf(this, EnvGuardError.prototype);
  }
}

/**
 * Build a "missing required variables" error message.
 */
export function buildMissingError(
  missing: Array<{ name: string; field: { type: string; description?: string } }>
): EnvGuardError {
  const lines = missing.map(({ name, field }) => {
    const desc = field.description ? field.description : typeDescription(field.type);
    return `  - ${name} (${field.type}): ${desc}`;
  });
  return new EnvGuardError(
    `[envguard] Missing required environment variables:\n${lines.join('\n')}`
  );
}

/**
 * Build a "validation failed" error message.
 */
export function buildValidationError(
  name: string,
  received: string,
  expected: string,
  description?: string
): EnvGuardError {
  const descPart = description ? ` (${description})` : '';
  return new EnvGuardError(
    `[envguard] Validation failed for "${name}"${descPart}:\n  Received: ${JSON.stringify(received)}\n  Expected: ${expected}`
  );
}

function typeDescription(type: string): string {
  switch (type) {
    case 'string': return 'A non-empty string value';
    case 'number': return 'A numeric value';
    case 'boolean': return 'A boolean value (true/false, 1/0, yes/no)';
    case 'url': return 'A valid URL (http:// or https://)';
    case 'enum': return 'One of the allowed enum values';
    default: return 'A required value';
  }
}
