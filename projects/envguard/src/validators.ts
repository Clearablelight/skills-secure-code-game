import type { FieldSchema, StringField, NumberField, BooleanField, UrlField, EnumField } from './types.js';
import { buildValidationError } from './errors.js';

/**
 * Validate and coerce a raw string value according to a FieldSchema.
 * Throws EnvGuardError on failure, returns the coerced value on success.
 */
export function validateField(name: string, raw: string, field: FieldSchema): unknown {
  switch (field.type) {
    case 'string':  return validateString(name, raw, field);
    case 'number':  return validateNumber(name, raw, field);
    case 'boolean': return validateBoolean(name, raw, field);
    case 'url':     return validateUrl(name, raw, field);
    case 'enum':    return validateEnum(name, raw, field);
    default: {
      const _never: never = field;
      throw new Error(`[envguard] Unknown field type for "${name}"`);
    }
  }
}

function validateString(name: string, raw: string, field: StringField): string {
  if (raw.trim() === '') {
    throw buildValidationError(name, raw, 'a non-empty string', field.description);
  }
  return raw;
}

function validateNumber(name: string, raw: string, field: NumberField): number {
  const n = Number(raw);
  if (!Number.isFinite(n)) {
    throw buildValidationError(name, raw, 'a finite number', field.description);
  }
  if (field.min !== undefined && n < field.min) {
    throw buildValidationError(name, raw, `a number >= ${field.min}`, field.description);
  }
  if (field.max !== undefined && n > field.max) {
    throw buildValidationError(name, raw, `a number <= ${field.max}`, field.description);
  }
  return n;
}

const TRUTHY = new Set(['true', '1', 'yes', 'on']);
const FALSY  = new Set(['false', '0', 'no', 'off']);

function validateBoolean(name: string, raw: string, field: BooleanField): boolean {
  const lower = raw.trim().toLowerCase();
  if (TRUTHY.has(lower)) return true;
  if (FALSY.has(lower))  return false;
  throw buildValidationError(
    name, raw, 'one of: true, false, 1, 0, yes, no, on, off', field.description
  );
}

function validateUrl(name: string, raw: string, field: UrlField): string {
  try {
    const url = new URL(raw.trim());
    if (url.protocol !== 'http:' && url.protocol !== 'https:') throw new Error('bad protocol');
    return raw.trim();
  } catch {
    throw buildValidationError(
      name, raw, 'a valid URL starting with http:// or https://', field.description
    );
  }
}

function validateEnum(name: string, raw: string, field: EnumField): string {
  if (!field.values.includes(raw)) {
    throw buildValidationError(
      name, raw,
      `one of: ${field.values.map((v) => JSON.stringify(v)).join(', ')}`,
      field.description
    );
  }
  return raw;
}
