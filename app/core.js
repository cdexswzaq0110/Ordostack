(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
    return;
  }

  root.LearningPlannerCore = factory();
})(typeof self !== "undefined" ? self : this, function () {
  const STATUS_TODO = "todo";
  const STATUS_DONE = "done";

  function createSubject(input) {
    return {
      id: input.id || createId("subject"),
      title: cleanText(input.title) || "未命名大項",
      createdAt: input.createdAt || new Date().toISOString(),
      tasks: Array.isArray(input.tasks) ? input.tasks.map(createTask) : [],
    };
  }

  function createTask(input) {
    return {
      id: input.id || createId("task"),
      title: cleanText(input.title),
      estimatedMinutes: normalizeMinutes(input.estimatedMinutes),
      priority: normalizePriority(input.priority),
      status: input.status === STATUS_DONE ? STATUS_DONE : STATUS_TODO,
      createdAt: input.createdAt || new Date().toISOString(),
      completedAt: input.completedAt || null,
    };
  }

  function migrateTasksToSubjects(rawItems) {
    if (!Array.isArray(rawItems) || rawItems.length === 0) {
      return [];
    }

    if (rawItems.some((item) => Array.isArray(item.tasks))) {
      return rawItems.map(createSubject);
    }

    const grouped = rawItems.reduce((subjects, task) => {
      const title = cleanText(task.category) || "一般任務";
      if (!subjects[title]) {
        subjects[title] = createSubject({ title, tasks: [] });
      }
      subjects[title].tasks.push(createTask(task));
      return subjects;
    }, {});

    return Object.values(grouped);
  }

  function validateSubjectInput(input) {
    if (!cleanText(input.title)) {
      return "請輸入大項名稱。";
    }

    return "";
  }

  function validateTaskInput(input) {
    if (!cleanText(input.title)) {
      return "請輸入細項名稱。";
    }

    if (normalizeMinutes(input.estimatedMinutes) > 480) {
      return "單一細項預估時間不應超過 480 分鐘。";
    }

    return "";
  }

  function addSubject(subjects, input) {
    return [createSubject(input), ...subjects.map(createSubject)];
  }

  function deleteSubject(subjects, subjectId) {
    return subjects.filter((subject) => subject.id !== subjectId).map(createSubject);
  }

  function addTaskToSubject(subjects, subjectId, input) {
    return subjects.map((subject) => {
      const nextSubject = createSubject(subject);
      if (nextSubject.id !== subjectId) {
        return nextSubject;
      }

      return {
        ...nextSubject,
        tasks: [createTask(input), ...nextSubject.tasks],
      };
    });
  }

  function deleteTask(subjects, subjectId, taskId) {
    return subjects.map((subject) => {
      const nextSubject = createSubject(subject);
      if (nextSubject.id !== subjectId) {
        return nextSubject;
      }

      return {
        ...nextSubject,
        tasks: nextSubject.tasks.filter((task) => task.id !== taskId),
      };
    });
  }

  function toggleTaskStatus(subjects, subjectId, taskId) {
    return subjects.map((subject) => {
      const nextSubject = createSubject(subject);
      if (nextSubject.id !== subjectId) {
        return nextSubject;
      }

      return {
        ...nextSubject,
        tasks: nextSubject.tasks.map((task) => {
          if (task.id !== taskId) {
            return task;
          }

          if (task.status === STATUS_DONE) {
            return { ...task, status: STATUS_TODO, completedAt: null };
          }

          return { ...task, status: STATUS_DONE, completedAt: new Date().toISOString() };
        }),
      };
    });
  }

  function recommendTasks(subjects, availableMinutes, maxTasks) {
    const limit = Number.isInteger(maxTasks) && maxTasks > 0 ? maxTasks : 3;
    const available = normalizeMinutes(availableMinutes);
    const unfinished = flattenTasks(subjects)
      .filter((entry) => entry.status !== STATUS_DONE)
      .sort(compareTasks);

    const selected = [];
    let usedMinutes = 0;

    for (const task of unfinished) {
      if (selected.length >= limit) {
        break;
      }

      if (usedMinutes + task.estimatedMinutes <= available) {
        selected.push(task);
        usedMinutes += task.estimatedMinutes;
      }
    }

    if (selected.length > 0) {
      return selected;
    }

    return unfinished.slice(0, limit);
  }

  function calculateCompletionRate(subjects) {
    const tasks = flattenTasks(subjects);
    if (tasks.length === 0) {
      return 0;
    }

    const completed = tasks.filter((task) => task.status === STATUS_DONE).length;
    return Math.round((completed / tasks.length) * 100);
  }

  function getSubjectSummary(subjects) {
    return subjects.map((subject) => {
      const nextSubject = createSubject(subject);
      const total = nextSubject.tasks.length;
      const completed = nextSubject.tasks.filter((task) => task.status === STATUS_DONE).length;
      const estimatedMinutes = nextSubject.tasks.reduce(
        (minutes, task) => minutes + task.estimatedMinutes,
        0
      );

      return {
        id: nextSubject.id,
        title: nextSubject.title,
        total,
        completed,
        estimatedMinutes,
        completionRate: total === 0 ? 0 : Math.round((completed / total) * 100),
      };
    });
  }

  function flattenTasks(subjects) {
    return subjects.flatMap((subject) => {
      const nextSubject = createSubject(subject);
      return nextSubject.tasks.map((task) => ({
        ...task,
        subjectId: nextSubject.id,
        subjectTitle: nextSubject.title,
      }));
    });
  }

  function normalizePriority(priority) {
    const value = Number(priority);
    if (!Number.isFinite(value)) {
      return 1;
    }
    return Math.min(5, Math.max(1, Math.round(value)));
  }

  function normalizeMinutes(minutes) {
    const value = Number(minutes);
    if (!Number.isFinite(value) || value <= 0) {
      return 30;
    }
    return Math.round(value);
  }

  function compareTasks(left, right) {
    if (right.priority !== left.priority) {
      return right.priority - left.priority;
    }

    if (left.estimatedMinutes !== right.estimatedMinutes) {
      return left.estimatedMinutes - right.estimatedMinutes;
    }

    return left.createdAt.localeCompare(right.createdAt);
  }

  function cleanText(value) {
    return String(value || "").trim();
  }

  function createId(prefix) {
    if (typeof crypto !== "undefined" && crypto.randomUUID) {
      return crypto.randomUUID();
    }

    return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }

  return {
    STATUS_TODO,
    STATUS_DONE,
    createSubject,
    createTask,
    migrateTasksToSubjects,
    validateSubjectInput,
    validateTaskInput,
    addSubject,
    deleteSubject,
    addTaskToSubject,
    deleteTask,
    toggleTaskStatus,
    recommendTasks,
    calculateCompletionRate,
    getSubjectSummary,
    flattenTasks,
  };
});
