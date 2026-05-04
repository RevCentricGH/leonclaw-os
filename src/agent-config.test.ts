import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import fs from 'fs';
import os from 'os';
import path from 'path';
import yaml from 'js-yaml';

let tmpRoot: string;
let projectRoot: string;
let claudeclawConfig: string;
let storeDir: string;

// Mock config BEFORE importing agent-config so STORE_DIR/PROJECT_ROOT point at tmp.
vi.mock('./config.js', () => {
  return {
    get CLAUDECLAW_CONFIG() { return claudeclawConfig; },
    get PROJECT_ROOT() { return projectRoot; },
    get STORE_DIR() { return storeDir; },
  };
});

// Mock env reader so loadAgentConfig doesn't fail on missing bot token.
vi.mock('./env.js', () => ({
  readEnvFile: () => ({ TEST_BOT_TOKEN: 'dummy' }),
}));

beforeEach(() => {
  tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'claudeclaw-agent-config-'));
  projectRoot = path.join(tmpRoot, 'project');
  claudeclawConfig = path.join(tmpRoot, 'config');
  storeDir = path.join(tmpRoot, 'store');
  fs.mkdirSync(projectRoot, { recursive: true });
  fs.mkdirSync(claudeclawConfig, { recursive: true });
  fs.mkdirSync(storeDir, { recursive: true });
  process.env.TEST_BOT_TOKEN = 'dummy';
});

afterEach(() => {
  delete process.env.TEST_BOT_TOKEN;
  fs.rmSync(tmpRoot, { recursive: true, force: true });
});

function writeAgentYaml(agentId: string, content: Record<string, unknown>): string {
  const agentDir = path.join(projectRoot, 'agents', agentId);
  fs.mkdirSync(agentDir, { recursive: true });
  const yamlPath = path.join(agentDir, 'agent.yaml');
  fs.writeFileSync(yamlPath, yaml.dump(content), 'utf-8');
  return yamlPath;
}


