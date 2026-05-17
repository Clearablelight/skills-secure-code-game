import type { GuardSchema, GuardOptions, InferEnv } from './types.js';
import { validateField } from './validators.js';
import { parseDotenv } from './parser.js';
import { buildMissingError } from './errors.js';

export { EnvGuardError } from './errors.js';
export type { FieldSchema, GuardSchema, GuardOptions, InferEnv } from './types.js';

/**
 * Validate and parse environment variables according to the provided schema.
 *
 * @param schema  - Field definitions keyed by environment variable name.
 * @param options - Optional configuration (e.g. dotenv file loading).
 * @returns A fully-typed, validated record of environment variable values.
 *
 * @example
 * ```ts
 * const env = guard({
 *   PORT:         { type: 'number', default: 3000 },
 *   DATABASE_URL: { type: 'url', required: true },
 *   NODE_ENV:     { type: 'enum', values: ['development', 'production', 'test'], default: 'development' },
 * });
 * // env.PORT     → number
 * // env.NODE_ENV → 'development' | 'production' | 'test'
 * ```
 */
export function guard<S extends GuardSchema>(
  schema: S,
  options: GuardOptions = {}
): InferEnv<S> {
  let envSource: Record<string, string | undefined> = { ...process.env };

  if (options.dotenv) {
    const dotenvValues = parseDotenv(options.cwd);
    for (const [key, value] of Object.entries(dotenvValues)) {
      if (!(key in envSource) || envSource[key] === undefined) {
        envSource[key] = value;
      }
    }
  }

  const result: Record<string, unknown> = {};
  const missing: Array<{ name: string; field: { type: string; description?: string } }> = [];

  for (const [name, field] of Object.entries(schema)) {
    const raw = envSource[name];
    if (raw === undefined || raw === '') {
      if ('default' in field && field.default !== undefined) {
        result[name] = field.default;
      } else if (field.required === true) {
        missing.push({ name, field });
      } else {
        result[name] = undefined;
      }
    } else {
      result[name] = validateField(name, raw, field);
    }
  }

  if (missing.length > 0) throw buildMissingError(missing);

  return result as InferEnv<S>;
}
