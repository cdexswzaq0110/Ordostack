const assert = require("node:assert");
const core = require("../app/core.js");

function subject(overrides) {
  return core.createSubject({
    id: overrides.id,
    title: overrides.title || "研究所考試",
    createdAt: overrides.createdAt || "2026-06-06T00:00:00.000Z",
    tasks: overrides.tasks || [],
  });
}

function task(overrides) {
  return core.createTask({
    id: overrides.id,
    title: overrides.title || "線性代數",
    estimatedMinutes: overrides.estimatedMinutes || 30,
    priority: overrides.priority || 3,
    status: overrides.status || core.STATUS_TODO,
    createdAt: overrides.createdAt || "2026-06-06T00:00:00.000Z",
  });
}

function test(name, fn) {
  try {
    fn();
    console.log(`ok - ${name}`);
  } catch (error) {
    console.error(`not ok - ${name}`);
    throw error;
  }
}

test("addSubject creates a customizable major item", () => {
  const subjects = core.addSubject([], { title: "研究所考試" });
  assert.strictEqual(subjects.length, 1);
  assert.strictEqual(subjects[0].title, "研究所考試");
});

test("addTaskToSubject adds a sub item under a major item", () => {
  const subjects = [subject({ id: "graduate", tasks: [] })];
  const nextSubjects = core.addTaskToSubject(subjects, "graduate", {
    id: "linear",
    title: "線性代數",
    estimatedMinutes: 60,
    priority: 5,
  });

  assert.strictEqual(nextSubjects[0].tasks.length, 1);
  assert.strictEqual(nextSubjects[0].tasks[0].title, "線性代數");
});

test("deleteSubject removes the major item and its sub items", () => {
  const subjects = [
    subject({ id: "graduate", tasks: [task({ id: "linear" })] }),
    subject({ id: "leetcode", title: "LeetCode" }),
  ];

  assert.deepStrictEqual(
    core.deleteSubject(subjects, "graduate").map((item) => item.id),
    ["leetcode"]
  );
});

test("deleteTask removes only the selected sub item", () => {
  const subjects = [
    subject({ id: "graduate", tasks: [task({ id: "linear" }), task({ id: "os", title: "作業系統" })] }),
  ];

  assert.deepStrictEqual(
    core.deleteTask(subjects, "graduate", "linear")[0].tasks.map((item) => item.id),
    ["os"]
  );
});

test("recommendTasks returns at most three unfinished sub items with subject metadata", () => {
  const subjects = [
    subject({
      id: "graduate",
      title: "研究所考試",
      tasks: [
        task({ id: "linear", priority: 5 }),
        task({ id: "os", title: "作業系統", priority: 4 }),
      ],
    }),
    subject({
      id: "leetcode",
      title: "LeetCode",
      tasks: [
        task({ id: "dp", title: "DP 題目", priority: 3 }),
        task({ id: "graph", title: "Graph 題目", priority: 2 }),
      ],
    }),
  ];

  const recommendations = core.recommendTasks(subjects, 240);
  assert.deepStrictEqual(
    recommendations.map((item) => item.id),
    ["linear", "os", "dp"]
  );
  assert.strictEqual(recommendations[0].subjectTitle, "研究所考試");
});

test("toggleTaskStatus updates completion rate", () => {
  const subjects = [subject({ id: "graduate", tasks: [task({ id: "linear" }), task({ id: "os" })] })];
  const nextSubjects = core.toggleTaskStatus(subjects, "graduate", "linear");

  assert.strictEqual(core.calculateCompletionRate(nextSubjects), 50);
});

test("migrateTasksToSubjects groups legacy flat tasks by category", () => {
  const subjects = core.migrateTasksToSubjects([
    { id: "a", title: "線性代數", category: "研究所考試" },
    { id: "b", title: "DP 題目", category: "LeetCode" },
  ]);

  assert.deepStrictEqual(
    subjects.map((item) => item.title),
    ["研究所考試", "LeetCode"]
  );
});
