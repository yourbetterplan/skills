#!/usr/bin/env node
// Compile a Playbook Definition into an importable Betterplan template and
// validate it against the live ProjectImportRequest schema.
//
//   node compile.mjs <playbook-dir> [--team <id>] [--spec <url|path>] [--out <file>]
//
// See ../references/playbook-format.md for the input contract.

import { readFile, writeFile, mkdir } from 'node:fs/promises'
import { randomUUID } from 'node:crypto'
import { basename, join, resolve } from 'node:path'
import { parse } from 'yaml'
import Ajv from 'ajv/dist/2020.js'

const SPEC_URL = 'https://app.yourbetterplan.com/api/openapi.json'
const ESTIMATION_SCALE = [0, 1, 2, 3, 5, 8, 13, 20, 40, 60, 100]
const ROOT_STORY_TYPES = ['project', 'dev']
const DEFAULT_TAG_COLOR = '#9AA0A6'
const REQUIRED_META = ['title', 'version', 'language', 'description', 'icon']

const errors = []
const warnings = []

const err = (path, msg) => errors.push(`${path}: ${msg}`)
const warn = (msg) => warnings.push(msg)

function parseArgs(argv) {
  const opts = { dir: null, team: null, spec: SPEC_URL, out: null }
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]
    if (a === '--team') opts.team = argv[++i]
    else if (a === '--spec') opts.spec = argv[++i]
    else if (a === '--out') opts.out = argv[++i]
    else if (a.startsWith('--')) die(`unknown flag ${a}`)
    else if (opts.dir === null) opts.dir = a
    else die(`unexpected argument ${a}`)
  }
  if (!opts.dir) die('usage: compile.mjs <playbook-dir> [--team <id>] [--spec <url|path>] [--out <file>]')
  return opts
}

function die(msg) {
  console.error(`✗ ${msg}`)
  process.exit(1)
}

async function readYaml(path) {
  try {
    return parse(await readFile(path, 'utf8')) ?? {}
  } catch (e) {
    die(`cannot read ${path} — ${e.message}`)
  }
}

async function loadSchema(specRef) {
  let doc
  if (/^https?:\/\//.test(specRef)) {
    const res = await fetch(specRef).catch((e) => die(`cannot fetch ${specRef} — ${e.message}`))
    if (!res.ok) die(`cannot fetch ${specRef} — HTTP ${res.status}`)
    doc = await res.json()
  } else {
    doc = JSON.parse(await readFile(specRef, 'utf8').catch((e) => die(`cannot read ${specRef} — ${e.message}`)))
  }
  const schemas = doc?.components?.schemas
  if (!schemas?.ProjectImportRequest) die(`${specRef} has no components.schemas.ProjectImportRequest`)

  // Keep the original $ref paths resolvable by re-hosting components.schemas
  // under an $id, and drop paths/info so ajv never walks the route objects.
  const ajv = new Ajv({ strict: false, allErrors: true, validateFormats: false })
  ajv.addSchema({ $id: 'bp', components: { schemas } })
  return {
    version: doc?.info?.version ?? 'unknown',
    validate: ajv.compile({ $ref: 'bp#/components/schemas/ProjectImportRequest' }),
  }
}

// ---------------------------------------------------------------------------

function checkMeta(meta) {
  for (const key of REQUIRED_META) {
    if (!meta[key]) err('playbook.yml', `missing required key \`${key}\``)
  }
}

function tagColors(meta) {
  const colors = new Map()
  for (const entry of meta.tags ?? []) {
    if (!entry?.name) err('playbook.yml', 'a `tags` entry has no `name`')
    else colors.set(entry.name, entry.color ?? DEFAULT_TAG_COLOR)
  }
  return colors
}

function checkTags(tags, path) {
  for (const tag of tags) {
    if (typeof tag !== 'string') { err(path, 'a tag is not a string'); continue }
    if (tag.startsWith('progress:')) {
      err(path, `remove \`${tag}\` — the server sets the starting phase per type`)
    } else if (!/^project:[^:]+$/.test(tag)) {
      err(path, `tag \`${tag}\` must be \`project:<value>\` with exactly one colon`)
    }
  }
}

function buildTasks(storymap) {
  const tasks = []

  const emit = (node, type, parentId, order, path) => {
    if (!node || typeof node !== 'object') { err(path, 'is not a mapping'); return null }
    if (!node.title || typeof node.title !== 'string' || !node.title.trim()) {
      err(path, 'needs a non-empty `title`')
    }
    if ('type' in node && type !== 'project' && type !== 'dev') {
      err(path, `remove \`type:\` — the key name already makes this a \`${type}\``)
    }
    if ('estimation' in node && node.estimation != null) {
      if (type !== 'story') err(path, `\`estimation\` is only valid on a User Story, not a \`${type}\``)
      else if (!ESTIMATION_SCALE.includes(node.estimation)) {
        err(path, `estimation ${node.estimation} is off the scale (${ESTIMATION_SCALE.join(', ')})`)
      }
    }
    for (const forbidden of ['id', 'parentId', 'displayOrder', 'metadata']) {
      if (forbidden in node) err(path, `remove \`${forbidden}\` — the compiler generates it`)
    }

    const task = { id: randomUUID(), type, title: String(node.title ?? '').trim() }
    if (parentId) task.parentId = parentId
    task.displayOrder = { storyboard: order }
    if (node.description != null) {
      const text = String(node.description).trim()
      if (text) task.description = text
    }
    if (node.tags != null) {
      if (!Array.isArray(node.tags)) err(path, '`tags` must be a list')
      else if (node.tags.length) { checkTags(node.tags, path); task.tags = node.tags }
    }
    if (node.estimation != null && type === 'story') task.estimation = node.estimation

    tasks.push(task)
    return task.id
  }

  const emitWorkitems = (story, storyId, path) => {
    const items = story?.workitems ?? []
    if (!Array.isArray(items)) { err(path, '`workitems` must be a list'); return }
    items.forEach((wi, i) => emit(wi, 'workitem', storyId, i, `${path}.workitems[${i}]`))
  }

  let rootOrder = 0

  const initiatives = storymap.initiatives ?? []
  if (!Array.isArray(initiatives)) err('storymap.yml', '`initiatives` must be a list')
  else initiatives.forEach((init, i) => {
    const ipath = `initiatives[${i}]`
    const initId = emit(init, 'initiative', null, rootOrder++, ipath)
    const epics = init?.epics ?? []
    if (!Array.isArray(epics)) { err(ipath, '`epics` must be a list'); return }
    epics.forEach((epic, j) => {
      const epath = `${ipath}.epics[${j}]`
      const epicId = emit(epic, 'epic', initId, j, epath)
      const stories = epic?.stories ?? []
      if (!Array.isArray(stories)) { err(epath, '`stories` must be a list'); return }
      stories.forEach((story, k) => {
        const spath = `${epath}.stories[${k}]`
        const storyId = emit(story, 'story', epicId, k, spath)
        emitWorkitems(story, storyId, spath)
      })
    })
  })

  const rootStories = storymap.stories ?? []
  if (!Array.isArray(rootStories)) err('storymap.yml', '`stories` must be a list')
  else rootStories.forEach((story, i) => {
    const path = `stories[${i}]`
    const type = story?.type
    if (!ROOT_STORY_TYPES.includes(type)) {
      err(path, `root-level stories need \`type: project\` or \`type: dev\` (got ${type === undefined ? 'nothing' : `\`${type}\``}) — a User Story belongs under an Epic`)
      return
    }
    const storyId = emit(story, type, null, rootOrder++, path)
    emitWorkitems(story, storyId, path)
  })

  if (!tasks.length) err('storymap.yml', 'produced no tasks')
  return tasks
}

function buildTagDefinitions(tasks, colors) {
  const used = new Set()
  for (const task of tasks) for (const tag of task.tags ?? []) used.add(tag)
  return [...used].sort().map((name) => {
    if (!colors.has(name)) warn(`tag \`${name}\` has no color in playbook.yml — using ${DEFAULT_TAG_COLOR}`)
    return { name, color: colors.get(name) ?? DEFAULT_TAG_COLOR }
  })
}

// ---------------------------------------------------------------------------

const opts = parseArgs(process.argv.slice(2))
const dir = resolve(opts.dir)
const slug = basename(dir)

const meta = await readYaml(join(dir, 'playbook.yml'))
const storymap = await readYaml(join(dir, 'storymap.yml'))

checkMeta(meta)
const colors = tagColors(meta)
const tasks = buildTasks(storymap)

if (errors.length) {
  console.error(`✗ ${errors.length} problem${errors.length === 1 ? '' : 's'} in the Playbook Definition:\n`)
  for (const e of errors) console.error(`  ${e}`)
  process.exit(1)
}

const description = String(meta.description ?? '').trim()

const payload = {
  title: String(meta.title ?? '').trim(),
  tasks,
  settings: {
    description,
    tagDefinitions: buildTagDefinitions(tasks, colors),
  },
  releases: [],
  iterations: [],
}
if (opts.team) payload.team_id = opts.team

const { version, validate } = await loadSchema(opts.spec)
if (!validate(payload)) {
  console.error(`✗ payload does not satisfy ProjectImportRequest (spec ${version}):\n`)
  for (const e of validate.errors) {
    console.error(`  ${e.instancePath || '/'} ${e.message}${e.params ? ` ${JSON.stringify(e.params)}` : ''}`)
  }
  process.exit(1)
}

const template = {
  ...payload,
  metadata: { description, icon: meta.icon, taskCount: tasks.length },
}

const out = opts.out ? resolve(opts.out) : join(dir, 'output', `${slug}.json`)
await mkdir(resolve(out, '..'), { recursive: true })
await writeFile(out, `${JSON.stringify(template, null, 2)}\n`)

for (const w of warnings) console.warn(`! ${w}`)
console.log(`✓ ${tasks.length} tasks, valid against ProjectImportRequest (spec ${version})`)
console.log(`  ${out}`)
if (!opts.team) console.log('  note: no --team given; add `team_id` before POSTing to /projects/import (400 without it)')
