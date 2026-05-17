import * as fs from 'node:fs';
import * as path from 'node:path';

/**
 * Parse a .env file and return a flat key-value record.
 *
 * Supports: KEY=value, quoted values, # comments, export prefix, inline comments.
 * Values in process.env take precedence — merging is done in guard().
 */
export function parseDotenv(cwd: string = process.cwd()): Record<string, string> {
  const filePath = path.resolve(cwd, '.env');
  let content: string;
  try {
    content = fs.readFileSync(filePath, 'utf8');
  } catch {
    return {};
  }

  const result: Record<string, string> = {};
  for (const rawLine of content.split('\n')) {
    const line = rawLine.trim();
    if (line === '' || line.startsWith('#')) continue;

    const withoutExport = line.startsWith('export ') ? line.slice(7) : line;
    const eqIndex = withoutExport.indexOf('=');
    if (eqIndex === -1) continue;

    const key = withoutExport.slice(0, eqIndex).trim();
    if (!key) continue;

    result[key] = parseValue(withoutExport.slice(eqIndex + 1));
  }
  return result;
}

function parseValue(raw: string): string {
  const trimmed = raw.trim();
  if (trimmed.startsWith('"') && trimmed.endsWith('"') && trimmed.length >= 2) {
    return trimmed.slice(1, -1)
      .replace(/\\n/g, '\n').replace(/\\r/g, '\r').replace(/\\t/g, '\t')
      .replace(/\\"/g, '"').replace(/\\\\/g, '\\');
  }
  if (trimmed.startsWith("'") && trimmed.endsWith("'") && trimmed.length >= 2) {
    return trimmed.slice(1, -1);
  }
  const commentMatch = trimmed.match(/^(.*?)\s+#.*$/);
  if (commentMatch) return commentMatch[1].trim();
  return trimmed;
}
