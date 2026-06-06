const STORAGE_KEY = "learning-planner.subjects.v2";
const LEGACY_STORAGE_KEY = "learning-planner.tasks.v1";

const elements = {
  subjectForm: document.querySelector("[data-subject-form]"),
  subjectTitle: document.querySelector("[data-subject-title]"),
  availableMinutes: document.querySelector("[data-available-minutes]"),
  subjectError: document.querySelector("[data-subject-error]"),
  subjectList: document.querySelector("[data-subject-list]"),
  recommendationList: document.querySelector("[data-recommendation-list]"),
  completionRate: document.querySelector("[data-completion-rate]"),
  subjectSummary: document.querySelector("[data-subject-summary]"),
};

let subjects = loadSubjects();

elements.subjectForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const input = { title: elements.subjectTitle.value };
  const error = LearningPlannerCore.validateSubjectInput(input);
  if (error) {
    elements.subjectError.textContent = error;
    return;
  }

  subjects = LearningPlannerCore.addSubject(subjects, input);
  elements.subjectForm.reset();
  elements.subjectError.textContent = "";
  saveSubjects();
  render();
});

elements.availableMinutes.addEventListener("input", render);

function loadSubjects() {
  try {
    const rawSubjects = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    if (Array.isArray(rawSubjects) && rawSubjects.length > 0) {
      return LearningPlannerCore.migrateTasksToSubjects(rawSubjects);
    }

    const legacyTasks = JSON.parse(localStorage.getItem(LEGACY_STORAGE_KEY) || "[]");
    return LearningPlannerCore.migrateTasksToSubjects(legacyTasks);
  } catch (_error) {
    return [];
  }
}

function saveSubjects() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(subjects));
}

function render() {
  renderSubjects();
  renderRecommendations();
  renderProgress();
}

function renderSubjects() {
  elements.subjectList.innerHTML = "";

  if (subjects.length === 0) {
    elements.subjectList.append(createEmptyState("尚未建立學習目標"));
    return;
  }

  for (const subject of subjects) {
    const item = document.createElement("li");
    item.className = "subject-card";

    const header = document.createElement("div");
    header.className = "subject-header";

    const titleGroup = document.createElement("div");
    titleGroup.className = "subject-title-group";
    titleGroup.innerHTML = `
      <strong>${escapeHtml(subject.title)}</strong>
      <span>${subject.tasks.length} 個任務</span>
    `;

    const actions = document.createElement("div");
    actions.className = "subject-actions";

    const deleteSubjectButton = document.createElement("button");
    deleteSubjectButton.type = "button";
    deleteSubjectButton.className = "icon-button danger-button";
    deleteSubjectButton.textContent = "-";
    deleteSubjectButton.setAttribute("aria-label", `刪除目標 ${subject.title}`);
    deleteSubjectButton.addEventListener("click", () => {
      if (!confirm(`刪除「${subject.title}」會一起刪除底下所有任務。確定刪除？`)) {
        return;
      }

      subjects = LearningPlannerCore.deleteSubject(subjects, subject.id);
      saveSubjects();
      render();
    });

    actions.append(deleteSubjectButton);
    header.append(titleGroup, actions);

    const taskForm = createTaskForm(subject);
    const taskList = document.createElement("ul");
    taskList.className = "nested-task-list";

    if (subject.tasks.length === 0) {
      taskList.append(createEmptyState("尚未建立任務"));
    } else {
      for (const task of subject.tasks) {
        taskList.append(createTaskItem(subject, task));
      }
    }

    item.append(header, taskForm, taskList);
    elements.subjectList.append(item);
  }
}

function createTaskForm(subject) {
  const form = document.createElement("form");
  form.className = "subtask-form";
  form.innerHTML = `
    <label>
      <span class="label-text">任務名稱</span>
      <input name="title" type="text" autocomplete="off" placeholder="輸入任務">
    </label>
    <label>
      <span class="label-text">分鐘</span>
      <input name="estimatedMinutes" type="number" min="5" max="480" step="5" value="30">
    </label>
    <label>
      <span class="label-text">優先級</span>
      <input name="priority" type="number" min="1" max="5" step="1" value="3">
    </label>
    <button class="small-add-button" type="submit" aria-label="新增 ${escapeHtml(subject.title)} 的任務">+</button>
  `;

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const input = {
      title: formData.get("title"),
      estimatedMinutes: formData.get("estimatedMinutes"),
      priority: formData.get("priority"),
    };
    const error = LearningPlannerCore.validateTaskInput(input);
    if (error) {
      elements.subjectError.textContent = error;
      return;
    }

    subjects = LearningPlannerCore.addTaskToSubject(subjects, subject.id, input);
    elements.subjectError.textContent = "";
    saveSubjects();
    render();
  });

  return form;
}

function createTaskItem(subject, task) {
  const item = document.createElement("li");
  item.className = `nested-task-item ${task.status === LearningPlannerCore.STATUS_DONE ? "is-done" : ""}`;

  const content = document.createElement("div");
  content.className = "task-content";
  content.innerHTML = `
    <strong>${escapeHtml(task.title)}</strong>
    <span>${task.estimatedMinutes} 分鐘 / P${task.priority}</span>
  `;

  const actions = document.createElement("div");
  actions.className = "task-actions";

  const toggleButton = document.createElement("button");
  toggleButton.type = "button";
  toggleButton.textContent = task.status === LearningPlannerCore.STATUS_DONE ? "復原" : "完成";
  toggleButton.setAttribute("aria-label", `${toggleButton.textContent} ${task.title}`);
  toggleButton.addEventListener("click", () => {
    subjects = LearningPlannerCore.toggleTaskStatus(subjects, subject.id, task.id);
    saveSubjects();
    render();
  });

  const deleteButton = document.createElement("button");
  deleteButton.type = "button";
  deleteButton.className = "danger-button";
  deleteButton.textContent = "-";
  deleteButton.setAttribute("aria-label", `刪除任務 ${task.title}`);
  deleteButton.addEventListener("click", () => {
    subjects = LearningPlannerCore.deleteTask(subjects, subject.id, task.id);
    saveSubjects();
    render();
  });

  actions.append(toggleButton, deleteButton);
  item.append(content, actions);
  return item;
}

function renderRecommendations() {
  elements.recommendationList.innerHTML = "";
  const recommendations = LearningPlannerCore.recommendTasks(
    subjects,
    Number(elements.availableMinutes.value),
    3
  );

  if (recommendations.length === 0) {
    elements.recommendationList.append(createEmptyState("尚無建議任務"));
    return;
  }

  for (const task of recommendations) {
    const item = document.createElement("li");
    item.className = "recommendation-item";
    item.innerHTML = `
      <strong>${escapeHtml(task.title)}</strong>
      <span>${escapeHtml(task.subjectTitle)} / ${task.estimatedMinutes} 分鐘 / P${task.priority}</span>
    `;
    elements.recommendationList.append(item);
  }
}

function renderProgress() {
  elements.completionRate.textContent = `${LearningPlannerCore.calculateCompletionRate(subjects)}%`;
  elements.subjectSummary.innerHTML = "";

  const summary = LearningPlannerCore.getSubjectSummary(subjects);
  if (summary.length === 0) {
    elements.subjectSummary.append(createEmptyState("尚無進度資料"));
    return;
  }

  for (const subject of summary) {
    const item = document.createElement("li");
    item.innerHTML = `
      <span>${escapeHtml(subject.title)}</span>
      <span>${subject.completed}/${subject.total} / ${subject.estimatedMinutes}m</span>
    `;
    elements.subjectSummary.append(item);
  }
}

function createEmptyState(text) {
  const item = document.createElement("li");
  item.className = "empty-state";
  item.textContent = text;
  return item;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

render();

if ("serviceWorker" in navigator && location.protocol !== "file:") {
  navigator.serviceWorker.register("./service-worker.js");
}
