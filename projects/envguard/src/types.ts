/**
 * Defines the shape of a single field in the schema.
 */
export type FieldSchema =
  | StringField
  | NumberField
  | BooleanField
  | UrlField
  | EnumField;

export interface BaseField {
  required?: boolean;
  description?: string;
}

export interface StringField extends BaseField {
  type: 'string';
  default?: string;
}

export interface NumberField extends BaseField {
  type: 'number';
  default?: number;
  min?: number;
  max?: number;
}

export interface BooleanField extends BaseField {
  type: 'boolean';
  default?: boolean;
}

export interface UrlField extends BaseField {
  type: 'url';
  default?: string;
}

export interface EnumField extends BaseField {
  type: 'enum';
  values: readonly string[];
  default?: string;
}

/**
 * A schema is a record mapping env var names to field definitions.
 */
export type GuardSchema = Record<string, FieldSchema>;

/**
 * Options passed to guard().
 */
export interface GuardOptions {
  /** If true, reads .env from cwd before checking process.env */
  dotenv?: boolean;
  /** Override the directory to search for .env (defaults to process.cwd()) */
  cwd?: string;
}

// ---------------------------------------------------------------------------
// Type inference helpers
// ---------------------------------------------------------------------------

/** Infer the raw TypeScript type for a single field. */
type InferFieldType<F extends FieldSchema> =
  F extends EnumField
    ? F['values'][number]
    : F extends NumberField
    ? number
    : F extends BooleanField
    ? boolean
    : string; // string | url

type InferField<F extends FieldSchema> = InferFieldType<F>;

/**
 * Infer the complete environment record type from a GuardSchema.
 */
export type InferEnv<S extends GuardSchema> = {
  [K in keyof S]: InferField<S[K]>;
};
