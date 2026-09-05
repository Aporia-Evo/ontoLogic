// Retrospective cost measurement. Run beside the D16/D21 HTML files:
// node operator_learning_actual_cost_prototype.cjs > actual_cost_result.json
// The existing D16 selection rule and full-table enumeration are preserved.
// Each evaluation arm builds one fresh cost-9 table, shared by all 20 tasks.
// Learning includes D16 module initialization, discovery, and winner retrieval.
// Evaluation includes D21 module initialization, enumeration, lookup and formatting.
// Timers cover these instrumented phases; counters count executed AST arithmetic,
// signature calls (including rejected expressions), and enumeration sort comparisons.
// File I/O, report serialization and validation are outside phase timers.
// Three sequential rounds, alternating evaluation order. These are timing repeats.
// Decision: compare learning + evaluation against baseline evaluation on this block.
// No new target-aware stopping or operator restriction is introduced here.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const os = require('node:os');
const assert = require('node:assert/strict');
const { performance } = require('node:perf_hooks');
const sources = [
  ['operator_learning_d16_generated_operator_holdout_prototype.html', '2886f552ff4f219162b08d44574a1f613f058895d895a9c80674240a352b290a'],
  ['operator_learning_d21_depth_vs_search_work_diagnostic_prototype.html', '8f46bf663e50d285af236a2bc6286f84189cbc51afdf64a166212e6b087e820b']
];
const metrics = ['primitiveEvaluations', 'signatureEvaluations', 'sortComparisons'];
const zero = () => Object.fromEntries(metrics.map(k => [k, 0]));
const sha = s => crypto.createHash('sha256').update(s).digest('hex');
function replaceOnce(s, from, to) {
  assert.equal(s.split(from).length, 2, `Expected one source seam: ${from}`);
  return s.replace(from, to);
}
function load([file, hash], index) {
  const html = fs.readFileSync(path.join(__dirname, file), 'utf8');
  assert.equal(sha(html), hash, `Source changed: ${file}`);
  let code = html.match(/<script>\s*([\s\S]*?)<\/script>/)[1];
  code = replaceOnce(code, 'const value = OPS[ast.op].fn', 'meter.primitiveEvaluations += 1;\n    const value = OPS[ast.op].fn');
  code = replaceOnce(code, 'function signature(ast,macros = {}) {', 'function signature(ast,macros = {}) { meter.signatureEvaluations += 1;');
  code = replaceOnce(code, 'batch.sort((left,right) => key(left).localeCompare(key(right)));',
    'batch.sort((left,right) => { meter.sortComparisons += 1; return key(left).localeCompare(key(right)); });');
  const extra = index === 0 ? 'buildCandidates,' : 'enumerate,format,evalAst,V,C,B,Call,';
  code = replaceOnce(code, 'return Object.freeze({ EXPECTED,', `return Object.freeze({ ${extra}EXPECTED,`);
  return code + `\nreturn D${index === 0 ? 16 : 21}Experiment;`;
}
const [learningCode, evaluationCode] = sources.map(load);
function measure(code, action) {
  const meter = zero();
  const cpuStart = process.cpuUsage();
  const start = performance.now();
  const value = action(new Function('meter', code)(meter));
  const wallMs = performance.now() - start;
  const cpu = process.cpuUsage(cpuStart);
  return { value, stats: { ...meter, wallMs, cpuMs: (cpu.user + cpu.system) / 1000 } };
}
function train(api) {
  const discovery = api.runDiscovery();
  assert.equal(discovery.protocolIntegrity, true);
  const winner = api.buildCandidates().find(c => c.id === discovery.selection.candidateId);
  return { winner, discovery };
}
function evaluate(api, winner) {
  const macros = winner ? { op: { name: 'op', definition: winner.definition } } : {};
  const table = api.enumerate(macros);
  const rows = api.TASKS.map(task => {
    const ast = table.seen.get(task.signature);
    return { taskId: task.id, signature: task.signature, found: Boolean(ast),
      cost: ast?.cost ?? null, program: ast ? api.format(ast) : null };
  });
  return { rows, tableSize: table.seen.size, tablesBuilt: 1, lookups: rows.length };
}
// Tiny counter checks use the actual evaluator, including a rejected value.
function checkCounters() {
  const meter = zero();
  const api = new Function('meter', evaluationCode)(meter);
  const cases = [
    [api.B('mul', api.V(), api.V()), {}, 3, 9, 1],
    [api.Call('op', api.B('add', api.V(), api.C(1))),
      { op: { definition: api.B('mul', api.V(), api.V()) } }, 3, 16, 2],
    [api.B('mul', api.C(1000000), api.C(2)), {}, 0, NaN, 1]
  ];
  for (const [ast, macros, input, expected, count] of cases) {
    const before = meter.primitiveEvaluations;
    assert.equal(api.evalAst(ast, input, macros), expected);
    assert.equal(meter.primitiveEvaluations - before, count);
  }
}
checkCounters();
if (process.argv.includes('--check')) { console.log('Counter checks passed (3 cases).'); process.exit(0); }
const rounds = [];
for (let i = 0; i < 3; i++) {
  const learning = measure(learningCode, train);
  const { winner, discovery } = learning.value;
  const arms = {};
  const order = i % 2 ? ['learned', 'baseline'] : ['baseline', 'learned'];
  for (const arm of order) {
    arms[arm] = measure(evaluationCode, api => evaluate(api, arm === 'learned' ? winner : null));
  }
  const total = Object.fromEntries([...metrics, 'wallMs', 'cpuMs'].map(k =>
    [k, learning.stats[k] + arms.learned.stats[k]]));
  const round = { round: i + 1, order, selected: { id: winner.id, key: winner.structuralKey },
    discoverySeal: discovery.discoverySeal, trainingTasks: discovery.split.discoveryCount,
    learning: learning.stats, baseline: arms.baseline, learned: arms.learned, total };
  rounds.push(round);
  console.error(`Round ${i + 1}: ${winner.structuralKey}; learning ${learning.stats.wallMs.toFixed(0)} ms; baseline ${arms.baseline.stats.wallMs.toFixed(0)} ms; learned ${arms.learned.stats.wallMs.toFixed(0)} ms`);
}
// Validate report consistency after all measurements; do not select by test results.
for (const r of rounds) {
  assert.equal(r.discoverySeal, '580acdca');
  for (const arm of ['baseline', 'learned']) {
    assert.equal(r[arm].value.rows.length, 20);
    assert(r[arm].value.rows.every(x => x.found));
    assert.deepEqual(r[arm].value.rows, rounds[0][arm].value.rows);
  }
  for (const phase of ['learning', 'baseline', 'learned']) for (const k of metrics) {
    assert.equal((r[phase].stats ?? r[phase])[k], (rounds[0][phase].stats ?? rounds[0][phase])[k]);
  }
}
const median = xs => [...xs].sort((a, b) => a - b)[1];
const summary = {};
for (const phase of ['learning', 'baseline', 'learned', 'total']) {
  const samples = rounds.map(r => r[phase].stats ?? r[phase]);
  summary[phase] = { ...Object.fromEntries(metrics.map(k => [k, samples[0][k]])),
    medianWallMs: median(samples.map(s => s.wallMs)), medianCpuMs: median(samples.map(s => s.cpuMs)) };
}
summary.totalToBaselinePrimitiveRatio = summary.total.primitiveEvaluations / summary.baseline.primitiveEvaluations;
summary.totalToBaselineMedianWallRatio = summary.total.medianWallMs / summary.baseline.medianWallMs;
summary.blockAmortizedByPrimitives = summary.total.primitiveEvaluations < summary.baseline.primitiveEvaluations;
summary.blockAmortizedByMedianWall = summary.total.medianWallMs < summary.baseline.medianWallMs;
const report = { protocol: 'actual-cost-v1', date: new Date().toISOString(),
  environment: { node: process.version, platform: process.platform, arch: process.arch, cpu: os.cpus()[0]?.model },
  sources: sources.map(([file, sha256]) => ({ file, sha256 })),
  accounting: 'One shared fresh cost-9 table per evaluation arm; full cost-7 D16 discovery charged once per round. Timings include instrumentation. Known D20 tasks; retrospective engineering measurement.',
  checks: '3 evaluator cases; original discovery seal; all tasks found; counters and returned programs identical across 3 rounds',
  selected: rounds[0].selected, summary, rounds };
console.log(JSON.stringify(report, null, 2));
