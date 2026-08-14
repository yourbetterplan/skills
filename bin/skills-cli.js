#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const SKILLS_FILE = path.join(process.cwd(), 'skills.json');

function loadManifest() {
  if (!fs.existsSync(SKILLS_FILE)) {
    console.error('❌ skills.json not found. Are you in the repository root?');
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(SKILLS_FILE, 'utf-8'));
}

function saveManifest(manifest) {
  fs.writeFileSync(SKILLS_FILE, JSON.stringify(manifest, null, 2) + '\n');
}

function extractFrontmatter(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return null;

  const fm = match[1];
  const data = {};
  let key = null;
  let valueLines = [];

  for (const line of fm.split('\n')) {
    const kv = line.match(/^(\w+):\s*(.*)$/);
    if (kv) {
      if (key) data[key] = valueLines.join('\n').trim();
      key = kv[1];
      valueLines = [kv[2]];
    } else if (key && line.startsWith('  ')) {
      valueLines.push(line.trim());
    }
  }
  if (key) data[key] = valueLines.join('\n').trim();

  return data;
}

function list() {
  const manifest = loadManifest();
  console.log('\n📦 Betterplan Skills\n');
  if (manifest.skills.length === 0) {
    console.log('   (no skills registered)');
  } else {
    const maxId = Math.max(...manifest.skills.map(s => s.id.length), 4);
    console.log(`   ${'ID'.padEnd(maxId)}  Version  Path`);
    console.log(`   ${'-'.repeat(maxId)}  -------  ----`);
    manifest.skills.forEach(s => {
      console.log(`   ${s.id.padEnd(maxId)}  ${s.version.padEnd(7)}  ${s.path}`);
    });
  }
  console.log(`\n   Total: ${manifest.skills.length} skill(s)\n`);
}

function add(sourcePath) {
  if (!sourcePath) {
    console.error('❌ Please provide a source path: skills add <path-to-skill-folder>');
    process.exit(1);
  }

  const absSource = path.resolve(sourcePath);
  if (!fs.existsSync(absSource)) {
    console.error(`❌ Source path not found: ${absSource}`);
    process.exit(1);
  }

  const skillMd = path.join(absSource, 'SKILL.md');
  if (!fs.existsSync(skillMd)) {
    console.error(`❌ No SKILL.md found in ${absSource}.`);
    process.exit(1);
  }

  const fm = extractFrontmatter(skillMd);
  if (!fm || !fm.name) {
    console.error(`❌ Invalid frontmatter in ${skillMd}`);
    process.exit(1);
  }

  const id = fm.name;
  const version = (fm.metadata && fm.metadata.version) ? fm.metadata.version : '0.1.0';
  const description = fm.description || '';
  const targetDir = path.join(process.cwd(), id);

  if (fs.existsSync(targetDir)) {
    console.error(`❌ Target directory already exists: ${targetDir}`);
    process.exit(1);
  }

  fs.cpSync(absSource, targetDir, { recursive: true });

  const manifest = loadManifest();
  if (manifest.skills.some(s => s.id === id)) {
    console.warn(`⚠️  Skill "${id}" was already in the manifest — updating entry.`);
    manifest.skills = manifest.skills.filter(s => s.id !== id);
  }

  manifest.skills.push({ id, name: id, path: id, version, description });
  saveManifest(manifest);

  console.log(`✅ Skill "${id}" @ ${version} added.`);
  console.log(`   Source:  ${absSource}`);
  console.log(`   Target:  ${targetDir}`);
}

function remove(skillId) {
  if (!skillId) {
    console.error('❌ Please provide a skill ID: skills remove <skill-id>');
    process.exit(1);
  }

  const manifest = loadManifest();
  const skill = manifest.skills.find(s => s.id === skillId);
  if (!skill) {
    console.error(`❌ Skill "${skillId}" not found in manifest.`);
    process.exit(1);
  }

  const targetDir = path.join(process.cwd(), skill.path);
  if (fs.existsSync(targetDir)) {
    fs.rmSync(targetDir, { recursive: true });
    console.log(`🗑️  Directory removed: ${targetDir}`);
  } else {
    console.warn(`⚠️  Directory ${targetDir} did not exist — removing from manifest only.`);
  }

  manifest.skills = manifest.skills.filter(s => s.id !== skillId);
  saveManifest(manifest);

  console.log(`✅ Skill "${skillId}" removed from registry.`);
}

function help() {
  console.log(`
Usage: skills <command> [args]

Commands:
  list                    Show all registered skills
  add  <path>             Copy skill folder into the repository and register it
  remove <skill-id>       Remove skill from repository and registry

Examples:
  npx skills list
  npx skills add ~/Downloads/my-skill
  npx skills remove betterplan-create-epic
`);
}

const [,, cmd, ...args] = process.argv;

switch (cmd) {
  case 'list':
    list();
    break;
  case 'add':
    add(args[0]);
    break;
  case 'remove':
    remove(args[0]);
    break;
  case '--help':
  case '-h':
  case 'help':
  default:
    help();
    break;
}
