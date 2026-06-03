import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertCircle,
  BarChart3,
  Bell,
  Brain,
  CalendarDays,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Clock3,
  Command,
  LayoutDashboard,
  ListTodo,
  Loader2,
  MoreHorizontal,
  Pause,
  Play,
  Plus,
  RotateCcw,
  Search,
  Settings,
  SkipForward,
  Sparkles,
  Target,
  Timer,
  Trash2,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

type NavigationItem = {
  label: string;
  icon: LucideIcon;
  isActive?: boolean;
};

type TaskStatus = "pending" | "in_progress" | "completed" | "skipped";

type ApiTask = {
  id: number;
  user_id: number;
  title: string;
  description: string;
  category: string;
  estimated_minutes: number;
  predicted_minutes: number | null;
  priority: number;
  difficulty: number;
  deadline: string | null;
  requires_focus: boolean;
  is_fixed: boolean;
  is_splittable: boolean;
  dependency_ids: number[];
  status: TaskStatus;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
};

type ApiFixedEvent = {
  id: number;
  user_id: number;
  title: string;
  start_time: string;
  end_time: string;
  event_type: string | null;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
};

type ApiScheduleItem = {
  type: "task" | "fixed_event";
  title: string;
  start_time: string;
  end_time: string;
  planned_minutes: number;
  order_index: number;
  task_id: number | null;
  fixed_event_id: number | null;
  category: string | null;
  requires_focus: boolean;
  score: number | null;
};

type ApiAlgorithmSummary = {
  available_minutes: number;
  selected_task_count: number;
  scheduled_task_count: number;
  skipped_task_count: number;
  total_task_minutes: number;
  applied_algorithms: string[];
  warnings: string[];
};

type ApiScheduleResponse = {
  schedule_date: string;
  planning_mode: string;
  items: ApiScheduleItem[];
  algorithm_summary: ApiAlgorithmSummary;
};

type ScheduleSource = "none" | "saved" | "generated";

type ApiTaskExecutionSummary = {
  task_id: number;
  title: string;
  status: TaskStatus;
  estimated_minutes: number;
  actual_minutes: number;
  estimate_delta_minutes: number;
};

type ApiDailyAnalytics = {
  user_id: number;
  target_date: string;
  total_tasks: number;
  completed_tasks: number;
  skipped_tasks: number;
  in_progress_tasks: number;
  estimated_minutes: number;
  actual_minutes: number;
  estimate_delta_minutes: number;
  completion_rate: number;
  focus_minutes: number;
  task_summaries: ApiTaskExecutionSummary[];
};

type ApiDurationPrediction = {
  task_id: number;
  predicted_minutes: number;
  confidence: number;
  model_name: string;
  reason: string;
};

type ApiDurationPredictionResponse = {
  user_id: number;
  target_date: string;
  model_name: string;
  model_version: string;
  predictions: ApiDurationPrediction[];
};

type TimelineItem = {
  start: string;
  end: string;
  title: string;
  meta: string;
  type: "focus" | "fixed" | "admin" | "break";
};

type InsightItem = {
  label: string;
  value: string;
  detail: string;
};

type TaskFormState = {
  title: string;
  category: string;
  estimatedMinutes: string;
  priority: string;
  difficulty: string;
  deadlineTime: string;
  requiresFocus: boolean;
};

type FixedEventFormState = {
  title: string;
  eventType: string;
  startTime: string;
  endTime: string;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";
const DEMO_USER_ID = 1;
const SELECTED_DATE = "2026-06-03";

const navigationItems: NavigationItem[] = [
  { label: "Today", icon: LayoutDashboard, isActive: true },
  { label: "Tasks", icon: ListTodo },
  { label: "Schedule", icon: CalendarDays },
  { label: "Analytics", icon: BarChart3 },
  { label: "MLOps", icon: Brain },
  { label: "Settings", icon: Settings },
];

const emptyTaskForm: TaskFormState = {
  title: "",
  category: "study",
  estimatedMinutes: "45",
  priority: "4",
  difficulty: "3",
  deadlineTime: "18:00",
  requiresFocus: true,
};

const emptyFixedEventForm: FixedEventFormState = {
  title: "",
  eventType: "meeting",
  startTime: "16:00",
  endTime: "17:00",
};

const serviceHealth = ["backend-api", "scheduler-service", "ml-service"];

function formatMinutes(totalMinutes: number): string {
  if (totalMinutes < 60) {
    return `${totalMinutes}m`;
  }

  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  return minutes === 0 ? `${hours}h` : `${hours}h ${minutes}m`;
}

function formatSignedMinutes(totalMinutes: number): string {
  if (totalMinutes === 0) {
    return "0m";
  }

  const prefix = totalMinutes > 0 ? "+" : "-";
  return `${prefix}${formatMinutes(Math.abs(totalMinutes))}`;
}

function formatTime(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(new Date(value));
}

function formatSelectedDate(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  }).format(new Date(`${value}T00:00:00`));
}

function formatWeekday(value: string): string {
  return new Intl.DateTimeFormat("en-US", { weekday: "long" }).format(new Date(`${value}T00:00:00`));
}

function addMinutes(dateTime: Date, minutes: number): Date {
  return new Date(dateTime.getTime() + minutes * 60_000);
}

function toTimeLabel(dateTime: Date): string {
  return new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(dateTime);
}

function priorityLabel(priority: number): string {
  return `P${6 - priority}`;
}

function priorityClass(priority: number): string {
  if (priority >= 5) {
    return "p1";
  }

  if (priority >= 3) {
    return "p2";
  }

  return "p3";
}

function taskStateLabel(status: TaskStatus): string {
  const labels: Record<TaskStatus, string> = {
    pending: "Ready",
    in_progress: "Doing",
    completed: "Done",
    skipped: "Skipped",
  };

  return labels[status];
}

function buildTimeline(tasks: ApiTask[], fixedEvents: ApiFixedEvent[]): TimelineItem[] {
  const taskStarts = ["09:00", "10:45", "13:30", "15:00"];
  const pendingTasks = tasks
    .filter((task) => task.status !== "completed" && task.status !== "skipped")
    .sort((left, right) => right.priority - left.priority || left.estimated_minutes - right.estimated_minutes)
    .slice(0, taskStarts.length);

  const taskBlocks = pendingTasks.map((task, index) => {
    const start = new Date(`${SELECTED_DATE}T${taskStarts[index]}:00`);
    const end = addMinutes(start, task.estimated_minutes);
    return {
      start: toTimeLabel(start),
      end: toTimeLabel(end),
      title: task.title,
      meta: `${task.category} | ${formatMinutes(task.estimated_minutes)} | priority ${task.priority}`,
      type: task.requires_focus ? "focus" : "admin",
    } satisfies TimelineItem;
  });

  const fixedBlocks = fixedEvents.map((event) => ({
    start: formatTime(event.start_time),
    end: formatTime(event.end_time),
    title: event.title,
    meta: `${event.event_type ?? "fixed"} | protected`,
    type: "fixed",
  })) satisfies TimelineItem[];

  return [...taskBlocks, ...fixedBlocks].sort((left, right) => left.start.localeCompare(right.start));
}

function buildTimelineFromSchedule(items: ApiScheduleItem[]): TimelineItem[] {
  return items
    .map((item) => {
      const timelineItem: TimelineItem = {
        start: formatTime(item.start_time),
        end: formatTime(item.end_time),
        title: item.title,
        meta:
          item.type === "fixed_event"
            ? `${item.category ?? "fixed"} | protected`
            : `${item.category ?? "task"} | ${formatMinutes(item.planned_minutes)} | score ${
                item.score?.toFixed(1) ?? "n/a"
              }`,
        type: item.type === "fixed_event" ? "fixed" : item.requires_focus ? "focus" : "admin",
      };

      return timelineItem;
    })
    .sort((left, right) => left.start.localeCompare(right.start));
}

async function sendJsonRequest<T>(url: string, options?: RequestInit, allowNotFound = false): Promise<T | null> {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    ...options,
  });

  if (allowNotFound && response.status === 404) {
    return null;
  }

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

async function requestJson<T>(url: string, options?: RequestInit): Promise<T> {
  return sendJsonRequest<T>(url, options) as Promise<T>;
}

async function requestOptionalJson<T>(url: string, options?: RequestInit): Promise<T | null> {
  return sendJsonRequest<T>(url, options, true);
}

export function App() {
  const [tasks, setTasks] = useState<ApiTask[]>([]);
  const [fixedEvents, setFixedEvents] = useState<ApiFixedEvent[]>([]);
  const [schedule, setSchedule] = useState<ApiScheduleResponse | null>(null);
  const [scheduleSource, setScheduleSource] = useState<ScheduleSource>("none");
  const [analytics, setAnalytics] = useState<ApiDailyAnalytics | null>(null);
  const [durationPredictions, setDurationPredictions] = useState<ApiDurationPredictionResponse | null>(null);
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isMutating, setIsMutating] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isTaskFormOpen, setIsTaskFormOpen] = useState(false);
  const [isFixedEventFormOpen, setIsFixedEventFormOpen] = useState(false);
  const [taskForm, setTaskForm] = useState<TaskFormState>(emptyTaskForm);
  const [fixedEventForm, setFixedEventForm] = useState<FixedEventFormState>(emptyFixedEventForm);

  async function loadDashboardData() {
    setIsLoading(true);
    setError(null);

    try {
      const [nextTasks, nextFixedEvents, nextAnalytics, nextDurationPredictions, latestSchedule] = await Promise.all([
        requestJson<ApiTask[]>(
          `${API_BASE_URL}/tasks?user_id=${DEMO_USER_ID}&target_date=${SELECTED_DATE}`,
        ),
        requestJson<ApiFixedEvent[]>(
          `${API_BASE_URL}/fixed-events?user_id=${DEMO_USER_ID}&target_date=${SELECTED_DATE}`,
        ),
        requestJson<ApiDailyAnalytics>(
          `${API_BASE_URL}/analytics/daily?user_id=${DEMO_USER_ID}&target_date=${SELECTED_DATE}`,
        ),
        requestJson<ApiDurationPredictionResponse>(
          `${API_BASE_URL}/ml/duration-predictions?user_id=${DEMO_USER_ID}&target_date=${SELECTED_DATE}`,
        ),
        requestOptionalJson<ApiScheduleResponse>(
          `${API_BASE_URL}/schedules/latest?user_id=${DEMO_USER_ID}&target_date=${SELECTED_DATE}`,
        ),
      ]);

      setTasks(nextTasks);
      setFixedEvents(nextFixedEvents);
      setAnalytics(nextAnalytics);
      setDurationPredictions(nextDurationPredictions);
      setSchedule(latestSchedule);
      setScheduleSource(latestSchedule ? "saved" : "none");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to load dashboard data");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadDashboardData();
  }, []);

  const filteredTasks = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    if (normalizedQuery.length === 0) {
      return tasks;
    }

    return tasks.filter((task) => {
      return (
        task.title.toLowerCase().includes(normalizedQuery) ||
        task.category.toLowerCase().includes(normalizedQuery)
      );
    });
  }, [query, tasks]);

  const timelineItems = useMemo(
    () => (schedule ? buildTimelineFromSchedule(schedule.items) : buildTimeline(tasks, fixedEvents)),
    [fixedEvents, schedule, tasks],
  );
  const analyticsByTask = useMemo(() => {
    return new Map((analytics?.task_summaries ?? []).map((summary) => [summary.task_id, summary]));
  }, [analytics]);
  const predictionsByTask = useMemo(() => {
    return new Map((durationPredictions?.predictions ?? []).map((prediction) => [prediction.task_id, prediction]));
  }, [durationPredictions]);
  const completedTasks = analytics?.completed_tasks ?? tasks.filter((task) => task.status === "completed").length;
  const totalTasks = analytics?.total_tasks ?? tasks.length;
  const plannedMinutes = analytics?.estimated_minutes ?? tasks.reduce((total, task) => total + task.estimated_minutes, 0);
  const actualMinutes = analytics?.actual_minutes ?? 0;
  const estimateDeltaMinutes = analytics?.estimate_delta_minutes ?? actualMinutes - plannedMinutes;
  const predictedMinutes = durationPredictions?.predictions.reduce(
    (total, prediction) => total + prediction.predicted_minutes,
    0,
  ) ?? plannedMinutes;
  const scheduledTaskMinutes =
    schedule?.items
      .filter((item) => item.type === "task")
      .reduce((total, item) => total + item.planned_minutes, 0) ?? plannedMinutes;
  const completionRate = analytics?.completion_rate ?? (tasks.length === 0 ? 0 : Math.round((completedTasks / tasks.length) * 100));
  const focusMinutes =
    analytics?.focus_minutes ??
    tasks
      .filter((task) => task.requires_focus && task.status !== "completed")
      .reduce((total, task) => total + task.estimated_minutes, 0);
  const algorithmSummary = schedule?.algorithm_summary ?? null;
  const scheduleKicker =
    scheduleSource === "saved" ? "Saved schedule" : scheduleSource === "generated" ? "Generated schedule" : "Today planner";
  const plannedTimeDetail =
    scheduleSource === "saved"
      ? "from latest saved schedule"
      : scheduleSource === "generated"
        ? "from generated schedule"
        : "from backend tasks";
  const planScore = algorithmSummary
    ? Math.max(0, Math.min(98, 82 + algorithmSummary.scheduled_task_count * 4 - algorithmSummary.skipped_task_count * 6))
    : Math.min(98, completionRate + 24);

  const insights: InsightItem[] = algorithmSummary
    ? [
        {
          label: "Scheduled tasks",
          value: `${algorithmSummary.scheduled_task_count}/${algorithmSummary.selected_task_count}`,
          detail: `${algorithmSummary.skipped_task_count} skipped by capacity or dependencies`,
        },
        {
          label: "Free capacity",
          value: formatMinutes(algorithmSummary.available_minutes),
          detail: `${algorithmSummary.applied_algorithms.length} scheduler algorithms applied`,
        },
        {
          label: "Work selected",
          value: formatMinutes(scheduledTaskMinutes),
          detail: algorithmSummary.warnings[0] ?? "No scheduler warnings",
        },
      ]
    : [
        {
          label: "Completion forecast",
          value: `${Math.min(96, completionRate + 24)}%`,
          detail: "Uses current queue and protected events",
        },
        {
          label: "Estimate drift",
          value: formatSignedMinutes(estimateDeltaMinutes),
          detail: "Actual minus estimated work time",
        },
        {
          label: "Predicted workload",
          value: formatMinutes(predictedMinutes),
          detail: durationPredictions
            ? `${durationPredictions.model_name} ${durationPredictions.model_version}`
            : "ML service not loaded",
        },
      ];

  async function generatePlan() {
    setIsGenerating(true);
    setError(null);

    try {
      const nextSchedule = await requestJson<ApiScheduleResponse>(`${API_BASE_URL}/schedules/generate`, {
        method: "POST",
        body: JSON.stringify({
          user_id: DEMO_USER_ID,
          target_date: SELECTED_DATE,
          planning_mode: "balanced",
          start_hour: 9,
          end_hour: 23,
          buffer_minutes: 10,
          include_fixed_events: true,
        }),
      });

      setSchedule(nextSchedule);
      setScheduleSource("generated");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to generate plan");
    } finally {
      setIsGenerating(false);
    }
  }

  async function createTask() {
    if (taskForm.title.trim().length === 0) {
      setError("Task title is required");
      return;
    }

    setIsMutating(true);
    setError(null);

    try {
      await requestJson<ApiTask>(`${API_BASE_URL}/tasks`, {
        method: "POST",
        body: JSON.stringify({
          user_id: DEMO_USER_ID,
          title: taskForm.title.trim(),
          description: "",
          category: taskForm.category.trim(),
          estimated_minutes: Number(taskForm.estimatedMinutes),
          priority: Number(taskForm.priority),
          difficulty: Number(taskForm.difficulty),
          deadline: `${SELECTED_DATE}T${taskForm.deadlineTime}:00`,
          requires_focus: taskForm.requiresFocus,
          is_fixed: false,
          is_splittable: false,
          dependency_ids: [],
        }),
      });

      setTaskForm(emptyTaskForm);
      setIsTaskFormOpen(false);
      await loadDashboardData();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to create task");
    } finally {
      setIsMutating(false);
    }
  }

  async function createFixedEvent() {
    if (fixedEventForm.title.trim().length === 0) {
      setError("Fixed event title is required");
      return;
    }

    setIsMutating(true);
    setError(null);

    try {
      await requestJson<ApiFixedEvent>(`${API_BASE_URL}/fixed-events`, {
        method: "POST",
        body: JSON.stringify({
          user_id: DEMO_USER_ID,
          title: fixedEventForm.title.trim(),
          event_type: fixedEventForm.eventType.trim(),
          start_time: `${SELECTED_DATE}T${fixedEventForm.startTime}:00`,
          end_time: `${SELECTED_DATE}T${fixedEventForm.endTime}:00`,
        }),
      });

      setFixedEventForm(emptyFixedEventForm);
      setIsFixedEventFormOpen(false);
      await loadDashboardData();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to create fixed event");
    } finally {
      setIsMutating(false);
    }
  }

  async function recordExecutionEvent(taskId: number, eventType: "start" | "pause" | "complete" | "skip") {
    setIsMutating(true);
    setError(null);

    try {
      await requestJson(`${API_BASE_URL}/tasks/${taskId}/execution/${eventType}`, {
        method: "POST",
        body: JSON.stringify({ user_id: DEMO_USER_ID }),
      });
      await loadDashboardData();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to record execution event");
    } finally {
      setIsMutating(false);
    }
  }

  async function updateTaskStatus(taskId: number, status: TaskStatus) {
    setIsMutating(true);
    setError(null);

    try {
      const endpoint =
        status === "pending"
          ? `${API_BASE_URL}/tasks/${taskId}/reopen`
          : `${API_BASE_URL}/tasks/${taskId}`;
      await requestJson<ApiTask>(endpoint, {
        method: status === "pending" ? "POST" : "PATCH",
        body: status === "pending" ? undefined : JSON.stringify({ status }),
      });
      await loadDashboardData();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to update task");
    } finally {
      setIsMutating(false);
    }
  }

  async function deleteTask(taskId: number) {
    setIsMutating(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, { method: "DELETE" });
      if (!response.ok) {
        throw new Error(`Delete failed with ${response.status}`);
      }

      await loadDashboardData();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to delete task");
    } finally {
      setIsMutating(false);
    }
  }

  return (
    <div className="product-shell">
      <aside className="sidebar" aria-label="Workspace navigation">
        <div className="brand-lockup">
          <div className="brand-mark" aria-hidden="true">
            O
          </div>
          <div>
            <strong>OrdoStack</strong>
            <span>Daily Planning OS</span>
          </div>
        </div>

        <nav className="sidebar-nav" aria-label="Primary">
          {navigationItems.map((item) => (
            <a key={item.label} className={item.isActive ? "nav-item active" : "nav-item"} href="#">
              <item.icon size={18} aria-hidden="true" />
              <span>{item.label}</span>
            </a>
          ))}
        </nav>

        <div className="sidebar-status" aria-label="Service health">
          <div className="status-heading">
            <Activity size={16} aria-hidden="true" />
            <span>System</span>
          </div>
          {serviceHealth.map((service) => (
            <div key={service} className="status-row">
              <span className="health-dot" aria-hidden="true" />
              <span>{service}</span>
              <strong>ok</strong>
            </div>
          ))}
        </div>
      </aside>

      <main className="workspace" aria-labelledby="page-title">
        <header className="topbar">
          <div className="date-control" aria-label="Selected date">
            <button className="icon-button" type="button" aria-label="Previous day" disabled>
              <ChevronLeft size={18} />
            </button>
            <div>
              <span>{formatWeekday(SELECTED_DATE)}</span>
              <strong>{formatSelectedDate(SELECTED_DATE)}</strong>
            </div>
            <button className="icon-button" type="button" aria-label="Next day" disabled>
              <ChevronRight size={18} />
            </button>
          </div>

          <div className="topbar-actions">
            <label className="search-box" aria-label="Search tasks">
              <Search size={17} aria-hidden="true" />
              <input
                type="search"
                placeholder="Search tasks"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
            </label>
            <button className="icon-button" type="button" aria-label="Notifications" disabled>
              <Bell size={18} />
            </button>
            <button
              className="primary-action"
              type="button"
              disabled={isGenerating || isLoading || isMutating}
              onClick={() => void generatePlan()}
            >
              {isGenerating ? (
                <Loader2 className="spinning" size={18} aria-hidden="true" />
              ) : (
                <Sparkles size={18} aria-hidden="true" />
              )}
              <span>{isGenerating ? "Generating" : "Generate Plan"}</span>
            </button>
          </div>
        </header>

        {error ? (
          <div className="alert-banner" role="alert">
            <AlertCircle size={18} aria-hidden="true" />
            <span>{error}</span>
          </div>
        ) : null}

        {isLoading ? (
          <section className="loading-panel" aria-label="Loading dashboard data">
            <Loader2 size={22} aria-hidden="true" />
            <span>Loading task and fixed event data...</span>
          </section>
        ) : (
          <>
            <section className="overview-strip" aria-label="Daily overview">
              <article>
                <span>Completion</span>
                <strong>{completionRate}%</strong>
                <em>
                  {completedTasks} of {totalTasks} tasks done
                </em>
              </article>
              <article>
                <span>Planned time</span>
                <strong>{formatMinutes(scheduledTaskMinutes)}</strong>
                <em>{plannedTimeDetail}</em>
              </article>
              <article>
                <span>Protected events</span>
                <strong>{fixedEvents.length}</strong>
                <em>fixed schedule blocks</em>
              </article>
              <article>
                <span>Actual time</span>
                <strong>{formatMinutes(actualMinutes)}</strong>
                <em>{formatSignedMinutes(estimateDeltaMinutes)} estimate drift</em>
              </article>
            </section>

            <div className="workspace-grid">
              <section className="timeline-surface" aria-labelledby="page-title">
                <div className="section-header">
                  <div>
                    <p className="section-kicker">{scheduleKicker}</p>
                    <h1 id="page-title">Focused schedule</h1>
                  </div>
                  <button
                    className="secondary-action"
                    type="button"
                    onClick={() => setIsTaskFormOpen((isOpen) => !isOpen)}
                  >
                    <Plus size={17} aria-hidden="true" />
                    <span>Add task</span>
                  </button>
                </div>

                {isTaskFormOpen ? (
                  <form
                    className="inline-form"
                    onSubmit={(event) => {
                      event.preventDefault();
                      void createTask();
                    }}
                  >
                    <div className="form-grid">
                      <label>
                        <span>Title</span>
                        <input
                          value={taskForm.title}
                          onChange={(event) => setTaskForm({ ...taskForm, title: event.target.value })}
                          placeholder="Task title"
                        />
                      </label>
                      <label>
                        <span>Category</span>
                        <input
                          value={taskForm.category}
                          onChange={(event) => setTaskForm({ ...taskForm, category: event.target.value })}
                        />
                      </label>
                      <label>
                        <span>Minutes</span>
                        <input
                          type="number"
                          min="1"
                          value={taskForm.estimatedMinutes}
                          onChange={(event) =>
                            setTaskForm({ ...taskForm, estimatedMinutes: event.target.value })
                          }
                        />
                      </label>
                      <label>
                        <span>Priority</span>
                        <input
                          type="number"
                          min="1"
                          max="5"
                          value={taskForm.priority}
                          onChange={(event) => setTaskForm({ ...taskForm, priority: event.target.value })}
                        />
                      </label>
                      <label>
                        <span>Difficulty</span>
                        <input
                          type="number"
                          min="1"
                          max="5"
                          value={taskForm.difficulty}
                          onChange={(event) => setTaskForm({ ...taskForm, difficulty: event.target.value })}
                        />
                      </label>
                      <label>
                        <span>Deadline</span>
                        <input
                          type="time"
                          value={taskForm.deadlineTime}
                          onChange={(event) => setTaskForm({ ...taskForm, deadlineTime: event.target.value })}
                        />
                      </label>
                    </div>
                    <label className="checkbox-row">
                      <input
                        type="checkbox"
                        checked={taskForm.requiresFocus}
                        onChange={(event) => setTaskForm({ ...taskForm, requiresFocus: event.target.checked })}
                      />
                      <span>Requires focus block</span>
                    </label>
                    <button className="primary-action" type="submit" disabled={isMutating}>
                      <Plus size={17} aria-hidden="true" />
                      <span>Create task</span>
                    </button>
                  </form>
                ) : null}

                <div className="timeline">
                  {timelineItems.map((item) => (
                    <article key={`${item.start}-${item.title}`} className={`timeline-item ${item.type}`}>
                      <div className="time-range">
                        <strong>{item.start}</strong>
                        <span>{item.end}</span>
                      </div>
                      <div className="timeline-block">
                        <div>
                          <h2>{item.title}</h2>
                          <p>{item.meta}</p>
                        </div>
                        <button className="ghost-button" type="button" aria-label={`More options for ${item.title}`}>
                          <MoreHorizontal size={18} />
                        </button>
                      </div>
                    </article>
                  ))}
                </div>
              </section>

              <section className="queue-surface" aria-labelledby="queue-title">
                <div className="section-header compact">
                  <div>
                    <p className="section-kicker">Task queue</p>
                    <h2 id="queue-title">Next candidates</h2>
                  </div>
                  <button className="icon-button" type="button" aria-label="Command palette" disabled>
                    <Command size={17} />
                  </button>
                </div>

                <div className="task-list">
                  {filteredTasks.length === 0 ? (
                    <div className="empty-state">No matching tasks.</div>
                  ) : (
                    filteredTasks.map((task) => {
                      const taskExecutionSummary = analyticsByTask.get(task.id);
                      const taskPrediction = predictionsByTask.get(task.id);
                      return (
                      <article key={task.id} className="task-row">
                        <button
                          className="task-check"
                          type="button"
                          aria-label={`Mark ${task.title} completed`}
                          disabled={isMutating || task.status === "completed" || task.status === "skipped"}
                          onClick={() => void recordExecutionEvent(task.id, "complete")}
                        >
                          <CheckCircle2 size={18} />
                        </button>
                        <div className="task-copy">
                          <h3>{task.title}</h3>
                          <p>
                            {task.category} | estimate {formatMinutes(task.estimated_minutes)} | predicted{" "}
                            {formatMinutes(taskPrediction?.predicted_minutes ?? task.predicted_minutes ?? task.estimated_minutes)} | actual{" "}
                            {formatMinutes(taskExecutionSummary?.actual_minutes ?? 0)}
                          </p>
                        </div>
                        <div className="task-meta">
                          <span className={`priority ${priorityClass(task.priority)}`}>
                            {priorityLabel(task.priority)}
                          </span>
                          <strong>{taskStateLabel(task.status)}</strong>
                        </div>
                        <div className="row-actions">
                          {task.status === "pending" ? (
                            <button
                              className="ghost-button"
                              type="button"
                              aria-label={`Start ${task.title}`}
                              disabled={isMutating}
                              onClick={() => void recordExecutionEvent(task.id, "start")}
                            >
                              <Play size={17} />
                            </button>
                          ) : null}
                          {task.status === "in_progress" ? (
                            <button
                              className="ghost-button"
                              type="button"
                              aria-label={`Pause ${task.title}`}
                              disabled={isMutating}
                              onClick={() => void recordExecutionEvent(task.id, "pause")}
                            >
                              <Pause size={17} />
                            </button>
                          ) : null}
                          {task.status === "pending" || task.status === "in_progress" ? (
                            <button
                              className="ghost-button"
                              type="button"
                              aria-label={`Skip ${task.title}`}
                              disabled={isMutating}
                              onClick={() => void recordExecutionEvent(task.id, "skip")}
                            >
                              <SkipForward size={17} />
                            </button>
                          ) : null}
                          {task.status === "completed" || task.status === "skipped" ? (
                            <button
                              className="ghost-button"
                              type="button"
                              aria-label={`Reopen ${task.title}`}
                              disabled={isMutating}
                              onClick={() => void updateTaskStatus(task.id, "pending")}
                            >
                              <RotateCcw size={17} />
                            </button>
                          ) : null}
                          <button
                            className="ghost-button danger"
                            type="button"
                            aria-label={`Delete ${task.title}`}
                            disabled={isMutating}
                            onClick={() => void deleteTask(task.id)}
                          >
                            <Trash2 size={17} />
                          </button>
                        </div>
                      </article>
                      );
                    })
                  )}
                </div>

                <div className="fixed-events-panel">
                  <div className="section-header compact">
                    <div>
                      <p className="section-kicker">Fixed events</p>
                      <h2>Protected time</h2>
                    </div>
                    <button
                      className="secondary-action"
                      type="button"
                      onClick={() => setIsFixedEventFormOpen((isOpen) => !isOpen)}
                    >
                      <Plus size={16} aria-hidden="true" />
                      <span>Add</span>
                    </button>
                  </div>

                  {isFixedEventFormOpen ? (
                    <form
                      className="inline-form compact-form"
                      onSubmit={(event) => {
                        event.preventDefault();
                        void createFixedEvent();
                      }}
                    >
                      <label>
                        <span>Title</span>
                        <input
                          value={fixedEventForm.title}
                          onChange={(event) =>
                            setFixedEventForm({ ...fixedEventForm, title: event.target.value })
                          }
                          placeholder="Meeting"
                        />
                      </label>
                      <div className="form-grid two-column">
                        <label>
                          <span>Start</span>
                          <input
                            type="time"
                            value={fixedEventForm.startTime}
                            onChange={(event) =>
                              setFixedEventForm({ ...fixedEventForm, startTime: event.target.value })
                            }
                          />
                        </label>
                        <label>
                          <span>End</span>
                          <input
                            type="time"
                            value={fixedEventForm.endTime}
                            onChange={(event) =>
                              setFixedEventForm({ ...fixedEventForm, endTime: event.target.value })
                            }
                          />
                        </label>
                      </div>
                      <button className="primary-action" type="submit" disabled={isMutating}>
                        <Plus size={16} aria-hidden="true" />
                        <span>Create event</span>
                      </button>
                    </form>
                  ) : null}

                  <div className="fixed-event-list">
                    {fixedEvents.map((event) => (
                      <article key={event.id} className="fixed-event-row">
                        <CalendarDays size={17} aria-hidden="true" />
                        <div>
                          <strong>{event.title}</strong>
                          <span>
                            {formatTime(event.start_time)} - {formatTime(event.end_time)}
                          </span>
                        </div>
                      </article>
                    ))}
                  </div>
                </div>
              </section>

              <aside className="insight-surface" aria-labelledby="insight-title">
                <div className="section-header compact">
                  <div>
                    <p className="section-kicker">AI review</p>
                    <h2 id="insight-title">Plan quality</h2>
                  </div>
                  <Target size={19} aria-hidden="true" />
                </div>

                <div className="score-ring" aria-label={`Plan score ${planScore} out of 100`}>
                  <span>{planScore}</span>
                  <strong>Plan score</strong>
                </div>

                <div className="insight-list">
                  {insights.map((insight) => (
                    <article key={insight.label} className="insight-row">
                      <div>
                        <span>{insight.label}</span>
                        <strong>{insight.value}</strong>
                      </div>
                      <p>{insight.detail}</p>
                    </article>
                  ))}
                </div>

                <div className="model-panel">
                  <div>
                    <Brain size={18} aria-hidden="true" />
                    <span>
                      {schedule
                        ? `${scheduleSource === "saved" ? "saved " : ""}scheduler-mvp + ${
                            durationPredictions?.model_name ?? "estimate-fallback"
                          }`
                        : durationPredictions?.model_name ?? "duration-baseline"}
                    </span>
                  </div>
                  <strong>{schedule ? "v0.5.0" : durationPredictions?.model_version ?? "v0.2.0"}</strong>
                </div>
              </aside>
            </div>

            <section className="bottom-rail" aria-label="Execution state">
              <div>
                <Timer size={18} aria-hidden="true" />
                <span>Current focus</span>
                <strong>
                  {tasks.find((task) => task.status === "in_progress")?.title ??
                    tasks.find((task) => task.requires_focus && task.status === "pending")?.title ??
                    "No focus task"}
                </strong>
              </div>
              <div>
                <Clock3 size={18} aria-hidden="true" />
                <span>Next fixed event</span>
                <strong>{fixedEvents[0]?.title ?? "No fixed event"}</strong>
              </div>
              <div>
                <CalendarDays size={18} aria-hidden="true" />
                <span>Data source</span>
                <strong>execution analytics MVP</strong>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}
