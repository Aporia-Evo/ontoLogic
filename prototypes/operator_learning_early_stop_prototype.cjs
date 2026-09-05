// Retrospective early-stop measurement. Run beside the D16/D21 HTML files:
// node operator_learning_early_stop_prototype.cjs > early_stop_result.json
// D16 learning is preserved. Both evaluation arms stop on the last target found.
// Each arm builds one shared table up to cost 9; current-layer sorting is charged.
// Learning includes D16 module initialization, discovery, and winner retrieval.
// Evaluation includes D21 module initialization, enumeration, lookup and formatting.
// Timers cover these instrumented phases; counters count executed AST arithmetic,
// signature calls (including rejected expressions), and enumeration sort comparisons.
// File I/O, report serialization and validation are outside phase timers.
// Three sequential rounds, alternating evaluation order. These are timing repeats.
// Decision: compare learning + evaluation against baseline evaluation on this block.
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
  if (index === 1) {
    code = replaceOnce(code, 'function enumerate(macros = {}) {',
      'function enumerate(macros = {}, targets = []) {\n    const pending = new Set(targets);\n    let stopCost = null;');
    code = replaceOnce(code, 'byCost[cost].push(ast);',
      'byCost[cost].push(ast);\n        if (pending.delete(sig) && pending.size === 0) { stopCost = cost; return true; }');
    code = replaceOnce(code, 'accept(1,[V(),...CONSTANTS.map(C)]);',
      'const solvedAtOne = accept(1,[V(),...CONSTANTS.map(C)]);');
    code = replaceOnce(code, 'for (let cost = 2; cost <= MAX_COST; cost += 1) {',
      'for (let cost = 2; !solvedAtOne && cost <= MAX_COST; cost += 1) {');
    code = replaceOnce(code, 'accept(cost,batch);', 'if (accept(cost,batch)) break;');
    code = replaceOnce(code, 'return { byCost,seen,attemptsByCost,workByCost };',
      'return { byCost,seen,attemptsByCost,workByCost,stopCost,remainingTargets:pending.size };');
  }
  const extra = index === 0 ? 'buildCandidates,' : 'enumerate,format,signature,evalAst,V,C,B,Call,';
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
  const table = api.enumerate(macros, api.TASKS.map(task => task.signature));
  const rows = api.TASKS.map(task => {
    const ast = table.seen.get(task.signature);
    return { taskId: task.id, signature: task.signature, found: Boolean(ast),
      cost: ast?.cost ?? null, program: ast ? api.format(ast) : null };
  });
  return { rows, tableSize: table.seen.size, tablesBuilt: 1, lookups: rows.length,
    stopCost: table.stopCost, remainingTargets: table.remainingTargets };
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
function checkStopping() {
  const meter = zero();
  const api = new Function('meter', evaluationCode)(meter);
  const square = api.B('mul', api.V(), api.V());
  const macros = { op: { definition: square } };
  const atom = api.signature(api.C(-2));
  const target = api.signature(square);
  const first = api.enumerate({}, [atom]);
  assert.equal(first.stopCost, 1);
  assert(first.seen.size < 7); // Stops inside the first batch, not at its end.
  assert.equal([...first.seen.keys()].at(-1), atom);
  for (const [operators, expectedCost] of [[{}, 3], [macros, 2]]) {
    const table = api.enumerate(operators, [atom, target]);
    assert.equal(table.stopCost, expectedCost);
    assert.equal(table.remainingTargets, 0);
    assert(table.seen.has(atom) && table.seen.has(target));
    assert(table.byCost.slice(expectedCost + 1).every(layer => layer.length === 0));
    assert.equal([...table.seen.keys()].at(-1), target);
  }
}
if (process.argv.includes('--check')) {
  checkStopping();
  console.log('Passed: 3 evaluator cases; immediate stop; both arms wait for every target.');
  process.exit(0);
}
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
    assert.equal(r[arm].value.remainingTargets, 0);
    assert(r[arm].value.stopCost !== null);
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
const report = { protocol: 'early-stop-v1', date: new Date().toISOString(),
  environment: { node: process.version, platform: process.platform, arch: process.arch, cpu: os.cpus()[0]?.model },
  sources: sources.map(([file, sha256]) => ({ file, sha256 })),
  accounting: 'One shared fresh table per evaluation arm, stopping immediately after all 20 target signatures are accepted, at most cost 9. Current-layer generation and sorting remain charged. Full cost-7 D16 discovery charged once per round. Timings include instrumentation. Known D20 tasks; retrospective engineering measurement.',
  checks: '3 evaluator cases; original discovery seal; all tasks found; counters and returned programs identical across 3 rounds',
  selected: rounds[0].selected, summary, rounds };
console.log(JSON.stringify(report, null, 2));
