import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs';
import * as path from 'node:path';
import * as os from 'node:os';
import { guard, EnvGuardError } from '../src/index.js';

function withEnv(vars: Record<string, string | undefined>, fn: () => void): void {
  const saved: Record<string, string | undefined> = {};
  for (const [k, v] of Object.entries(vars)) {
    saved[k] = process.env[k];
    if (v === undefined) delete process.env[k]; else process.env[k] = v;
  }
  try { fn(); } finally {
    for (const [k, v] of Object.entries(saved)) {
      if (v === undefined) delete process.env[k]; else process.env[k] = v;
    }
  }
}

function makeTempEnv(content: string): string {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'envguard-'));
  fs.writeFileSync(path.join(dir, '.env'), content, 'utf8');
  return dir;
}

describe('happy path', () => {
  it('parses string', () => withEnv({ EG_X: 'hello' }, () => {
    assert.equal(guard({ EG_X: { type: 'string', required: true } }).EG_X, 'hello');
  }));
  it('parses number', () => withEnv({ EG_X: '42' }, () => {
    assert.equal(guard({ EG_X: { type: 'number', required: true } }).EG_X, 42);
  }));
  it('parses boolean true variants', () => {
    for (const v of ['true', '1', 'yes', 'on', 'TRUE']) {
      withEnv({ EG_X: v }, () => assert.equal(guard({ EG_X: { type: 'boolean', required: true } }).EG_X, true));
    }
  });
  it('parses boolean false variants', () => {
    for (const v of ['false', '0', 'no', 'off', 'FALSE']) {
      withEnv({ EG_X: v }, () => assert.equal(guard({ EG_X: { type: 'boolean', required: true } }).EG_X, false));
    }
  });
  it('parses url', () => withEnv({ EG_X: 'https://example.com' }, () => {
    assert.equal(guard({ EG_X: { type: 'url', required: true } }).EG_X, 'https://example.com');
  }));
  it('parses enum', () => withEnv({ EG_X: 'production' }, () => {
    assert.equal(guard({ EG_X: { type: 'enum', values: ['development', 'production'] as const, required: true } }).EG_X, 'production');
  }));
});

describe('defaults', () => {
  it('uses default when absent', () => withEnv({ EG_X: undefined }, () => {
    assert.equal(guard({ EG_X: { type: 'number', default: 3000 } }).EG_X, 3000);
  }));
  it('env overrides default', () => withEnv({ EG_X: '9000' }, () => {
    assert.equal(guard({ EG_X: { type: 'number', default: 3000 } }).EG_X, 9000);
  }));
});

describe('missing required', () => {
  it('throws on missing required field', () => withEnv({ EG_X: undefined }, () => {
    assert.throws(() => guard({ EG_X: { type: 'url', required: true } }), EnvGuardError);
  }));
  it('lists all missing fields in one error', () => withEnv({ EG_A: undefined, EG_B: undefined }, () => {
    assert.throws(
      () => guard({ EG_A: { type: 'string', required: true }, EG_B: { type: 'url', required: true } }),
      (err) => {
        assert.ok(err instanceof EnvGuardError);
        assert.ok((err as Error).message.includes('EG_A'));
        assert.ok((err as Error).message.includes('EG_B'));
        return true;
      }
    );
  }));
  it('does not throw for optional absent field', () => withEnv({ EG_X: undefined }, () => {
    assert.doesNotThrow(() => guard({ EG_X: { type: 'string' } }));
  }));
});

describe('enum validation', () => {
  it('rejects invalid enum value', () => withEnv({ EG_X: 'staging' }, () => {
    assert.throws(() => guard({ EG_X: { type: 'enum', values: ['dev', 'prod'] as const, required: true } }), EnvGuardError);
  }));
});

describe('number min/max', () => {
  it('rejects below min', () => withEnv({ EG_X: '0' }, () => {
    assert.throws(() => guard({ EG_X: { type: 'number', min: 1, required: true } }), EnvGuardError);
  }));
  it('rejects above max', () => withEnv({ EG_X: '999' }, () => {
    assert.throws(() => guard({ EG_X: { type: 'number', max: 100, required: true } }), EnvGuardError);
  }));
  it('accepts boundary values', () => {
    withEnv({ EG_X: '1' }, () => assert.equal(guard({ EG_X: { type: 'number', min: 1, max: 20, required: true } }).EG_X, 1));
    withEnv({ EG_X: '20' }, () => assert.equal(guard({ EG_X: { type: 'number', min: 1, max: 20, required: true } }).EG_X, 20));
  });
});

describe('url validation', () => {
  it('rejects non-url', () => withEnv({ EG_X: 'not-a-url' }, () => {
    assert.throws(() => guard({ EG_X: { type: 'url', required: true } }), EnvGuardError);
  }));
  it('rejects ftp://', () => withEnv({ EG_X: 'ftp://example.com' }, () => {
    assert.throws(() => guard({ EG_X: { type: 'url', required: true } }), EnvGuardError);
  }));
});

describe('.env file support', () => {
  it('reads from .env file', () => {
    const dir = makeTempEnv('EG_X=from-file\n');
    withEnv({ EG_X: undefined }, () => {
      assert.equal(guard({ EG_X: { type: 'string', required: true } }, { dotenv: true, cwd: dir }).EG_X, 'from-file');
    });
    fs.rmSync(dir, { recursive: true });
  });
  it('process.env takes precedence over .env', () => {
    const dir = makeTempEnv('EG_X=from-file\n');
    withEnv({ EG_X: 'from-process' }, () => {
      assert.equal(guard({ EG_X: { type: 'string', required: true } }, { dotenv: true, cwd: dir }).EG_X, 'from-process');
    });
    fs.rmSync(dir, { recursive: true });
  });
});
