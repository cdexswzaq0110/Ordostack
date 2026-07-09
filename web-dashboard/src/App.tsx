import { useEffect, useMemo, useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import {
  Activity,
  AlertCircle,
  BarChart3,
  Brain,
  CalendarDays,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Clock3,
  Download,
  LayoutDashboard,
  ListFilter,
  ListTodo,
  LogIn,
  LogOut,
  Lock,
  Loader2,
  Pause,
  Pencil,
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
  Unlock,
  UserCircle,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import {
  DEFAULT_LOCALE,
  LOCALE_STORAGE_KEY,
  localeOptions,
  resolveLocale,
  translate,
  type LocaleCode,
  type Translator,
} from "./i18n";

type WorkspaceView = "today" | "tasks" | "schedule" | "analytics" | "mlops" | "settings";

type NavigationItem = {
  view: WorkspaceView;
  label: string;
  icon: LucideIcon;
};

type TaskStatus = "pending" | "in_progress" | "completed" | "skipped";
type TaskStatusFilter = "all" | TaskStatus;
type TaskFocusFilter = "all" | "focus" | "non_focus";
type TaskSortMode = "priority" | "deadline" | "estimate" | "status";

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
  locked?: boolean;
  manual_override?: boolean;
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

type ApiScheduleHistoryItem = {
  id: number;
  title: string;
  created_at: string;
  planning_mode: string;
  scheduled_task_count: number;
  item_count: number;
  schedule: ApiScheduleResponse;
};

type ApiScheduleDiffItem = {
  item_key: string;
  change_type: "added" | "removed" | "changed";
  title: string;
  previous_start_time: string | null;
  next_start_time: string | null;
  previous_planned_minutes: number | null;
  next_planned_minutes: number | null;
};

type ApiScheduleDiffResponse = {
  base_run_id: number;
  compare_run_id: number;
  added_count: number;
  removed_count: number;
  changed_count: number;
  unchanged_count: number;
  total_delta_minutes: number;
  changes: ApiScheduleDiffItem[];
};

type ApiScheduleExportResponse = {
  filename: string;
  format: "markdown" | "csv" | "pdf";
  content_type: string;
  content: string;
  encoding?: "utf-8" | "base64";
};

type ScheduleSource = "none" | "saved" | "generated" | "history";

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

type ApiUser = {
  id: number;
  email: string;
  display_name: string;
  created_at: string;
};

type ApiAuthToken = {
  access_token: string;
  token_type: "bearer";
  expires_at: string;
  user: ApiUser;
};

type TimelineItem = {
  start: string;
  end: string;
  title: string;
  meta: string;
  type: "focus" | "fixed" | "admin" | "break";
  itemKey?: string;
  locked?: boolean;
  manualOverride?: boolean;
  startsAt?: Date;
  endsAt?: Date;
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

type AuthFormState = {
  email: string;
  displayName: string;
  password: string;
};

type AuthMode = "login" | "register";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";
const DEMO_USER_ID = 1;
const DEMO_AUTH_EMAIL = "demo@ordostack.local";
const DEMO_AUTH_PASSWORD = "ordostack-demo";
const DEFAULT_SELECTED_DATE = "2026-06-03";
const AUTH_TOKEN_STORAGE_KEY = "ordostack.authToken";

const navigationItems: NavigationItem[] = [
  { view: "today", label: "Today", icon: LayoutDashboard },
  { view: "tasks", label: "Tasks", icon: ListTodo },
  { view: "schedule", label: "Schedule", icon: CalendarDays },
  { view: "analytics", label: "Analytics", icon: BarChart3 },
  { view: "mlops", label: "MLOps", icon: Brain },
  { view: "settings", label: "Settings", icon: Settings },
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

const emptyAuthForm: AuthFormState = {
  email: DEMO_AUTH_EMAIL,
  displayName: "Demo User",
  password: DEMO_AUTH_PASSWORD,
};

const serviceHealth = ["backend-api", "scheduler-service", "ml-service"];

type TaskMutationPayload = {
  title: string;
  category: string;
  estimated_minutes: number;
  priority: number;
  difficulty: number;
  deadline: string;
  requires_focus: boolean;
};

type FixedEventMutationPayload = {
  title: string;
  event_type: string;
  start_time: string;
  end_time: string;
};

type TaskFormFieldsProps = {
  form: TaskFormState;
  onChange: Dispatch<SetStateAction<TaskFormState>>;
  t: Translator;
};

type FixedEventFormFieldsProps = {
  form: FixedEventFormState;
  onChange: Dispatch<SetStateAction<FixedEventFormState>>;
  t: Translator;
};

function TaskFormFields({ form, onChange, t }: TaskFormFieldsProps) {
  return (
    <>
      <div className="form-grid">
        <label>
          <span>{t("Title")}</span>
          <input
            value={form.title}
            onChange={(event) =>
              onChange((currentForm) => ({ ...currentForm, title: event.target.value }))
            }
            placeholder={t("Task title")}
          />
        </label>
        <label>
          <span>{t("Category")}</span>
          <input
            value={form.category}
            onChange={(event) =>
              onChange((currentForm) => ({ ...currentForm, category: event.target.value }))
            }
          />
        </label>
        <label>
          <span>{t("Minutes")}</span>
          <input
            type="number"
            min="1"
            step="1"
            value={form.estimatedMinutes}
            onChange={(event) =>
              onChange((currentForm) => ({ ...currentForm, estimatedMinutes: event.target.value }))
            }
          />
        </label>
        <label>
          <span>{t("Priority")}</span>
          <input
            type="number"
            min="1"
            max="5"
            step="1"
            value={form.priority}
            onChange={(event) =>
              onChange((currentForm) => ({ ...currentForm, priority: event.target.value }))
            }
          />
        </label>
        <label>
          <span>{t("Difficulty")}</span>
          <input
            type="number"
            min="1"
            max="5"
            step="1"
            value={form.difficulty}
            onChange={(event) =>
              onChange((currentForm) => ({ ...currentForm, difficulty: event.target.value }))
            }
          />
        </label>
        <label>
          <span>{t("Deadline")}</span>
          <input
            type="text"
            inputMode="numeric"
            maxLength={5}
            pattern="^([01]\d|2[0-3]):[0-5]\d$"
            placeholder="18:00"
            value={form.deadlineTime}
            onChange={(event) =>
              onChange((currentForm) => ({ ...currentForm, deadlineTime: event.target.value }))
            }
          />
        </label>
      </div>
      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={form.requiresFocus}
          onChange={(event) =>
            onChange((currentForm) => ({ ...currentForm, requiresFocus: event.target.checked }))
          }
        />
        <span>{t("Requires focus block")}</span>
      </label>
    </>
  );
}

function FixedEventFormFields({ form, onChange, t }: FixedEventFormFieldsProps) {
  return (
    <>
      <label>
        <span>{t("Title")}</span>
        <input
          value={form.title}
          onChange={(event) =>
            onChange((currentForm) => ({ ...currentForm, title: event.target.value }))
          }
          placeholder={t("Meeting")}
        />
      </label>
      <label>
        <span>{t("Type")}</span>
        <input
          value={form.eventType}
          onChange={(event) =>
            onChange((currentForm) => ({ ...currentForm, eventType: event.target.value }))
          }
          placeholder={t("meeting")}
        />
      </label>
      <div className="form-grid two-column">
        <label>
          <span>{t("Start")}</span>
          <input
            type="text"
            inputMode="numeric"
            maxLength={5}
            pattern="^([01]\d|2[0-3]):[0-5]\d$"
            placeholder="16:00"
            value={form.startTime}
            onChange={(event) =>
              onChange((currentForm) => ({ ...currentForm, startTime: event.target.value }))
            }
          />
        </label>
        <label>
          <span>{t("End")}</span>
          <input
            type="text"
            inputMode="numeric"
            maxLength={5}
            pattern="^([01]\d|2[0-3]):[0-5]\d$"
            placeholder="17:00"
            value={form.endTime}
            onChange={(event) =>
              onChange((currentForm) => ({ ...currentForm, endTime: event.target.value }))
            }
          />
        </label>
      </div>
    </>
  );
}

function getTaskFormError(form: TaskFormState, t: Translator): string | null {
  if (form.title.trim().length === 0) {
    return t("Task title is required");
  }

  if (form.category.trim().length === 0) {
    return t("Task category is required");
  }

  const estimatedMinutes = Number(form.estimatedMinutes);
  if (!Number.isInteger(estimatedMinutes) || estimatedMinutes < 1) {
    return t("Estimated minutes must be a whole number greater than 0");
  }

  const priority = Number(form.priority);
  if (!Number.isInteger(priority) || priority < 1 || priority > 5) {
    return t("Priority must be a whole number from 1 to 5");
  }

  const difficulty = Number(form.difficulty);
  if (!Number.isInteger(difficulty) || difficulty < 1 || difficulty > 5) {
    return t("Difficulty must be a whole number from 1 to 5");
  }

  if (form.deadlineTime.length === 0) {
    return t("Deadline time is required");
  }

  if (!/^([01]\d|2[0-3]):[0-5]\d$/.test(form.deadlineTime)) {
    return t("Deadline time must use HH:MM format");
  }

  return null;
}

function getFixedEventFormError(form: FixedEventFormState, t: Translator): string | null {
  if (form.title.trim().length === 0) {
    return t("Fixed event title is required");
  }

  if (form.eventType.trim().length === 0) {
    return t("Fixed event type is required");
  }

  if (!/^([01]\d|2[0-3]):[0-5]\d$/.test(form.startTime)) {
    return t("Start time must use HH:MM format");
  }

  if (!/^([01]\d|2[0-3]):[0-5]\d$/.test(form.endTime)) {
    return t("End time must use HH:MM format");
  }

  if (form.endTime <= form.startTime) {
    return t("End time must be later than start time");
  }

  return null;
}

function buildTaskMutationPayload(form: TaskFormState, selectedDate: string): TaskMutationPayload {
  return {
    title: form.title.trim(),
    category: form.category.trim(),
    estimated_minutes: Number(form.estimatedMinutes),
    priority: Number(form.priority),
    difficulty: Number(form.difficulty),
    deadline: `${selectedDate}T${form.deadlineTime}:00`,
    requires_focus: form.requiresFocus,
  };
}

function buildFixedEventMutationPayload(form: FixedEventFormState, selectedDate: string): FixedEventMutationPayload {
  return {
    title: form.title.trim(),
    event_type: form.eventType.trim(),
    start_time: `${selectedDate}T${form.startTime}:00`,
    end_time: `${selectedDate}T${form.endTime}:00`,
  };
}

function taskFormFromTask(task: ApiTask): TaskFormState {
  return {
    title: task.title,
    category: task.category,
    estimatedMinutes: String(task.estimated_minutes),
    priority: String(task.priority),
    difficulty: String(task.difficulty),
    deadlineTime: task.deadline ? task.deadline.slice(11, 16) : emptyTaskForm.deadlineTime,
    requiresFocus: task.requires_focus,
  };
}

function fixedEventFormFromEvent(event: ApiFixedEvent): FixedEventFormState {
  return {
    title: event.title,
    eventType: event.event_type ?? emptyFixedEventForm.eventType,
    startTime: event.start_time.slice(11, 16),
    endTime: event.end_time.slice(11, 16),
  };
}

function formatMinutes(totalMinutes: number, locale: LocaleCode = DEFAULT_LOCALE): string {
  if (totalMinutes < 60) {
    if (locale === "zh-TW") {
      return `${totalMinutes} 分鐘`;
    }
    return `${totalMinutes}m`;
  }

  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (locale === "zh-TW") {
    return minutes === 0 ? `${hours} 小時` : `${hours} 小時 ${minutes} 分鐘`;
  }
  return minutes === 0 ? `${hours}h` : `${hours}h ${minutes}m`;
}

function formatSignedMinutes(totalMinutes: number, locale: LocaleCode = DEFAULT_LOCALE): string {
  if (totalMinutes === 0) {
    return formatMinutes(0, locale);
  }

  const prefix = totalMinutes > 0 ? "+" : "-";
  return `${prefix}${formatMinutes(Math.abs(totalMinutes), locale)}`;
}

function formatTime(value: string, locale: LocaleCode = DEFAULT_LOCALE): string {
  return new Intl.DateTimeFormat(locale, {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(new Date(value));
}

function formatSelectedDate(value: string, locale: LocaleCode = DEFAULT_LOCALE): string {
  return new Intl.DateTimeFormat(locale, {
    month: "long",
    day: "numeric",
    year: "numeric",
  }).format(new Date(`${value}T00:00:00`));
}

function formatWeekday(value: string, locale: LocaleCode = DEFAULT_LOCALE): string {
  return new Intl.DateTimeFormat(locale, { weekday: "long" }).format(new Date(`${value}T00:00:00`));
}

function shiftDate(value: string, days: number): string {
  const date = new Date(`${value}T00:00:00`);
  date.setDate(date.getDate() + days);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function todayDateString(): string {
  const date = new Date();
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function addMinutes(dateTime: Date, minutes: number): Date {
  return new Date(dateTime.getTime() + minutes * 60_000);
}

function toTimeLabel(dateTime: Date, locale: LocaleCode = DEFAULT_LOCALE): string {
  return new Intl.DateTimeFormat(locale, {
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

function taskStateLabel(status: TaskStatus, t: Translator): string {
  const labels: Record<TaskStatus, string> = {
    pending: "Ready",
    in_progress: "Doing",
    completed: "Done",
    skipped: "Skipped",
  };

  return t(labels[status]);
}

function deadlineTimeValue(task: ApiTask): number {
  return task.deadline ? new Date(task.deadline).getTime() : Number.MAX_SAFE_INTEGER;
}

function compareTasks(sortMode: TaskSortMode): (left: ApiTask, right: ApiTask) => number {
  const statusRank: Record<TaskStatus, number> = {
    in_progress: 0,
    pending: 1,
    completed: 2,
    skipped: 3,
  };

  return (left, right) => {
    if (sortMode === "deadline") {
      return deadlineTimeValue(left) - deadlineTimeValue(right) || right.priority - left.priority || left.id - right.id;
    }

    if (sortMode === "estimate") {
      return right.estimated_minutes - left.estimated_minutes || right.priority - left.priority || left.id - right.id;
    }

    if (sortMode === "status") {
      return statusRank[left.status] - statusRank[right.status] || right.priority - left.priority || left.id - right.id;
    }

    return right.priority - left.priority || deadlineTimeValue(left) - deadlineTimeValue(right) || left.id - right.id;
  };
}

function buildTimeline(
  tasks: ApiTask[],
  fixedEvents: ApiFixedEvent[],
  selectedDate: string,
  locale: LocaleCode,
  t: Translator,
): TimelineItem[] {
  const taskStarts = ["09:00", "10:45", "13:30", "15:00"];
  const pendingTasks = tasks
    .filter((task) => task.status !== "completed" && task.status !== "skipped")
    .sort((left, right) => right.priority - left.priority || left.estimated_minutes - right.estimated_minutes)
    .slice(0, taskStarts.length);

  const taskBlocks = pendingTasks.map((task, index) => {
    const start = new Date(`${selectedDate}T${taskStarts[index]}:00`);
    const end = addMinutes(start, task.estimated_minutes);
    return {
      start: toTimeLabel(start, locale),
      end: toTimeLabel(end, locale),
      title: task.title,
      meta: `${task.category} | ${formatMinutes(task.estimated_minutes, locale)} | ${t("priority")} ${task.priority}`,
      type: task.requires_focus ? "focus" : "admin",
      startsAt: start,
      endsAt: end,
    } satisfies TimelineItem;
  });

  const fixedBlocks = fixedEvents.map((event) => ({
    start: formatTime(event.start_time, locale),
    end: formatTime(event.end_time, locale),
    title: event.title,
    meta: `${event.event_type ?? t("fixed")} | ${t("protected")}`,
    type: "fixed",
    startsAt: new Date(event.start_time),
    endsAt: new Date(event.end_time),
  })) satisfies TimelineItem[];

  return [...taskBlocks, ...fixedBlocks].sort((left, right) => left.start.localeCompare(right.start));
}

function buildTimelineFromSchedule(items: ApiScheduleItem[], locale: LocaleCode, t: Translator): TimelineItem[] {
  return items
    .map((item) => {
      const stateLabels = [
        item.locked ? t("Locked") : null,
        item.manual_override ? t("Manual") : null,
      ].filter(Boolean);
      const timelineItem: TimelineItem = {
        start: formatTime(item.start_time, locale),
        end: formatTime(item.end_time, locale),
        title: item.title,
        meta:
          item.type === "fixed_event"
            ? `${item.category ?? t("fixed")} | ${t("protected")}`
            : `${item.category ?? t("task")} | ${formatMinutes(item.planned_minutes, locale)} | ${t("score")} ${
                item.score?.toFixed(1) ?? "n/a"
              }${stateLabels.length > 0 ? ` | ${stateLabels.join(" | ")}` : ""}`,
        type: item.type === "fixed_event" ? "fixed" : item.requires_focus ? "focus" : "admin",
        itemKey: scheduleItemKey(item),
        locked: item.locked ?? false,
        manualOverride: item.manual_override ?? false,
        startsAt: new Date(item.start_time),
        endsAt: new Date(item.end_time),
      };

      return timelineItem;
    })
    .sort((left, right) => left.start.localeCompare(right.start));
}

function isCurrentTimelineItem(item: TimelineItem, now: Date): boolean {
  return item.startsAt !== undefined && item.endsAt !== undefined && item.startsAt <= now && now < item.endsAt;
}

function scheduleItemKey(item: ApiScheduleItem): string {
  if (item.type === "task" && item.task_id !== null) {
    return `task:${item.task_id}`;
  }
  if (item.type === "fixed_event" && item.fixed_event_id !== null) {
    return `fixed_event:${item.fixed_event_id}`;
  }
  return `${item.type}:${item.title}:${item.order_index}`;
}

function offsetDateTime(value: string, offsetMinutes: number): string {
  const normalizedValue = value.length === 16 ? `${value}:00` : value.slice(0, 19);
  const [datePart, timePart] = normalizedValue.split("T");
  const [year, month, day] = datePart.split("-").map(Number);
  const [hour, minute, second] = timePart.split(":").map(Number);
  const nextDate = new Date(year, month - 1, day, hour, minute + offsetMinutes, second);
  return [
    nextDate.getFullYear(),
    padDatePart(nextDate.getMonth() + 1),
    padDatePart(nextDate.getDate()),
  ].join("-") + `T${padDatePart(nextDate.getHours())}:${padDatePart(nextDate.getMinutes())}:${padDatePart(nextDate.getSeconds())}`;
}

function padDatePart(value: number): string {
  return value.toString().padStart(2, "0");
}

async function sendJsonRequest<T>(url: string, options?: RequestInit, allowNotFound = false): Promise<T | null> {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
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

function downloadTextFile(filename: string, content: string, contentType: string) {
  const blob = new Blob([content], { type: contentType });
  downloadBlob(filename, blob);
}

function downloadBase64File(filename: string, content: string, contentType: string) {
  const binary = window.atob(content);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  downloadBlob(filename, new Blob([bytes], { type: contentType }));
}

function downloadBlob(filename: string, blob: Blob) {
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(objectUrl);
}

export function App() {
  const [selectedDate, setSelectedDate] = useState(DEFAULT_SELECTED_DATE);
  const [tasks, setTasks] = useState<ApiTask[]>([]);
  const [fixedEvents, setFixedEvents] = useState<ApiFixedEvent[]>([]);
  const [schedule, setSchedule] = useState<ApiScheduleResponse | null>(null);
  const [scheduleSource, setScheduleSource] = useState<ScheduleSource>("none");
  const [scheduleHistory, setScheduleHistory] = useState<ApiScheduleHistoryItem[]>([]);
  const [selectedScheduleRunId, setSelectedScheduleRunId] = useState<number | null>(null);
  const [editingScheduleRunId, setEditingScheduleRunId] = useState<number | null>(null);
  const [scheduleRunTitleDraft, setScheduleRunTitleDraft] = useState("");
  const [scheduleDiff, setScheduleDiff] = useState<ApiScheduleDiffResponse | null>(null);
  const [analytics, setAnalytics] = useState<ApiDailyAnalytics | null>(null);
  const [durationPredictions, setDurationPredictions] = useState<ApiDurationPredictionResponse | null>(null);
  const [query, setQuery] = useState("");
  const [taskStatusFilter, setTaskStatusFilter] = useState<TaskStatusFilter>("all");
  const [taskCategoryFilter, setTaskCategoryFilter] = useState("all");
  const [taskFocusFilter, setTaskFocusFilter] = useState<TaskFocusFilter>("all");
  const [taskSortMode, setTaskSortMode] = useState<TaskSortMode>("priority");
  const [isLoading, setIsLoading] = useState(true);
  const [isMutating, setIsMutating] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isComparing, setIsComparing] = useState(false);
  const [isExportingSchedule, setIsExportingSchedule] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isTaskFormOpen, setIsTaskFormOpen] = useState(false);
  const [isFixedEventFormOpen, setIsFixedEventFormOpen] = useState(false);
  const [taskForm, setTaskForm] = useState<TaskFormState>(emptyTaskForm);
  const [editingTaskId, setEditingTaskId] = useState<number | null>(null);
  const [editTaskForm, setEditTaskForm] = useState<TaskFormState>(emptyTaskForm);
  const [fixedEventForm, setFixedEventForm] = useState<FixedEventFormState>(emptyFixedEventForm);
  const [editingFixedEventId, setEditingFixedEventId] = useState<number | null>(null);
  const [editFixedEventForm, setEditFixedEventForm] = useState<FixedEventFormState>(emptyFixedEventForm);
  const [authToken, setAuthToken] = useState(() => localStorage.getItem(AUTH_TOKEN_STORAGE_KEY) ?? "");
  const [currentUser, setCurrentUser] = useState<ApiUser | null>(null);
  const [now, setNow] = useState(() => new Date());
  const [activeView, setActiveView] = useState<WorkspaceView>("today");
  const [authMode, setAuthMode] = useState<AuthMode>("login");
  const [authForm, setAuthForm] = useState<AuthFormState>(emptyAuthForm);
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [authStatus, setAuthStatus] = useState<string | null>(null);
  const [locale, setLocale] = useState<LocaleCode>(() => resolveLocale(localStorage.getItem(LOCALE_STORAGE_KEY)));
  const t = useMemo(() => (key: string) => translate(locale, key), [locale]);

  function changeLocale(nextLocale: LocaleCode) {
    setLocale(nextLocale);
    localStorage.setItem(LOCALE_STORAGE_KEY, nextLocale);
  }

  async function loadCurrentUser(token: string) {
    try {
      const user = await requestJson<ApiUser>(`${API_BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setCurrentUser(user);
      setAuthStatus(null);
    } catch {
      setAuthToken("");
      setCurrentUser(null);
      setAuthStatus(t("Session expired. Please sign in again."));
    }
  }

  async function submitAuthForm() {
    if (authForm.email.trim().length === 0 || authForm.password.length === 0) {
      setAuthStatus(t("Email and password are required."));
      return;
    }

    if (authMode === "register" && authForm.displayName.trim().length === 0) {
      setAuthStatus(t("Display name is required."));
      return;
    }

    setIsAuthenticating(true);
    setAuthStatus(null);

    try {
      const endpoint = authMode === "register" ? "register" : "login";
      const payload =
        authMode === "register"
          ? {
              email: authForm.email.trim(),
              display_name: authForm.displayName.trim(),
              password: authForm.password,
            }
          : {
              email: authForm.email.trim(),
              password: authForm.password,
            };
      const authPayload = await requestJson<ApiAuthToken>(`${API_BASE_URL}/auth/${endpoint}`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setAuthToken(authPayload.access_token);
      setCurrentUser(authPayload.user);
      setAuthStatus(authMode === "register" ? t("Account created.") : t("Signed in."));
    } catch (caughtError) {
      setAuthStatus(caughtError instanceof Error ? caughtError.message : t("Authentication failed."));
    } finally {
      setIsAuthenticating(false);
    }
  }

  async function loginDemoUser() {
    setAuthForm({
      email: DEMO_AUTH_EMAIL,
      displayName: "Demo User",
      password: DEMO_AUTH_PASSWORD,
    });
    setAuthMode("login");
    setIsAuthenticating(true);
    setAuthStatus(null);

    try {
      const authPayload = await requestJson<ApiAuthToken>(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        body: JSON.stringify({
          email: DEMO_AUTH_EMAIL,
          password: DEMO_AUTH_PASSWORD,
        }),
      });
      setAuthToken(authPayload.access_token);
      setCurrentUser(authPayload.user);
      setAuthStatus(t("Demo account signed in."));
    } catch (caughtError) {
      setAuthStatus(caughtError instanceof Error ? caughtError.message : t("Unable to sign in demo account."));
    } finally {
      setIsAuthenticating(false);
    }
  }

  function signOut() {
    setAuthToken("");
    setCurrentUser(null);
    setAuthStatus(t("Signed out."));
  }

  function buildAuthHeaders(): Record<string, string> {
    return authToken ? { Authorization: `Bearer ${authToken}` } : {};
  }

  async function loadDashboardData() {
    if (!authToken) {
      setTasks([]);
      setFixedEvents([]);
      setAnalytics(null);
      setDurationPredictions(null);
      setSchedule(null);
      setScheduleHistory([]);
      setSelectedScheduleRunId(null);
      setScheduleSource("none");
      setScheduleDiff(null);
      setIsLoading(false);
      setError(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const [
        nextTasks,
        nextFixedEvents,
        nextAnalytics,
        nextDurationPredictions,
        latestSchedule,
        nextScheduleHistory,
      ] = await Promise.all([
        requestJson<ApiTask[]>(
          `${API_BASE_URL}/tasks?target_date=${selectedDate}`,
          { headers: buildAuthHeaders() },
        ),
        requestJson<ApiFixedEvent[]>(
          `${API_BASE_URL}/fixed-events?target_date=${selectedDate}`,
          { headers: buildAuthHeaders() },
        ),
        requestJson<ApiDailyAnalytics>(
          `${API_BASE_URL}/analytics/daily?target_date=${selectedDate}`,
          { headers: buildAuthHeaders() },
        ),
        requestJson<ApiDurationPredictionResponse>(
          `${API_BASE_URL}/ml/duration-predictions?target_date=${selectedDate}`,
          { headers: buildAuthHeaders() },
        ),
        requestOptionalJson<ApiScheduleResponse>(
          `${API_BASE_URL}/schedules/latest?target_date=${selectedDate}`,
          { headers: buildAuthHeaders() },
        ),
        requestJson<ApiScheduleHistoryItem[]>(
          `${API_BASE_URL}/schedules/history?target_date=${selectedDate}&limit=5`,
          { headers: buildAuthHeaders() },
        ),
      ]);

      setTasks(nextTasks);
      setFixedEvents(nextFixedEvents);
      setAnalytics(nextAnalytics);
      setDurationPredictions(nextDurationPredictions);
      setSchedule(latestSchedule);
      setScheduleHistory(nextScheduleHistory);
      setSelectedScheduleRunId(latestSchedule ? nextScheduleHistory[0]?.id ?? null : null);
      setScheduleSource(latestSchedule ? "saved" : "none");
      setScheduleDiff(null);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : t("Unable to load dashboard data"));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadDashboardData();
  }, [authToken, selectedDate]);

  useEffect(() => {
    if (!authToken) {
      setCurrentUser(null);
      localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
      return;
    }

    localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, authToken);
    void loadCurrentUser(authToken);
  }, [authToken]);

  useEffect(() => {
    const tick = window.setInterval(() => setNow(new Date()), 60_000);
    return () => window.clearInterval(tick);
  }, []);

  // Re-registered every render so the handlers always see current state.
  useEffect(() => {
    function handleShortcut(event: KeyboardEvent) {
      if (!event.altKey || event.ctrlKey || event.metaKey) {
        return;
      }
      const target = event.target as HTMLElement | null;
      if (target && target.closest("input, textarea, select, [contenteditable=true]")) {
        return;
      }

      if (event.key === "ArrowLeft" && !isLoading) {
        event.preventDefault();
        changeSelectedDate(-1);
      } else if (event.key === "ArrowRight" && !isLoading) {
        event.preventDefault();
        changeSelectedDate(1);
      } else if ((event.key === "t" || event.key === "T") && !isLoading) {
        event.preventDefault();
        selectDate(todayDateString());
      } else if ((event.key === "g" || event.key === "G") && authToken && !isGenerating && !isLoading && !isMutating) {
        event.preventDefault();
        void generatePlan();
      }
    }

    window.addEventListener("keydown", handleShortcut);
    return () => window.removeEventListener("keydown", handleShortcut);
  });

  const filteredTasks = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    const matchesQuery = (task: ApiTask) => {
      if (normalizedQuery.length === 0) {
        return true;
      }

      return task.title.toLowerCase().includes(normalizedQuery) || task.category.toLowerCase().includes(normalizedQuery);
    };

    return tasks
      .filter((task) => matchesQuery(task))
      .filter((task) => taskStatusFilter === "all" || task.status === taskStatusFilter)
      .filter((task) => taskCategoryFilter === "all" || task.category === taskCategoryFilter)
      .filter((task) => {
        if (taskFocusFilter === "all") {
          return true;
        }

        return taskFocusFilter === "focus" ? task.requires_focus : !task.requires_focus;
      })
      .sort(compareTasks(taskSortMode));
  }, [query, taskCategoryFilter, taskFocusFilter, taskSortMode, taskStatusFilter, tasks]);

  const taskCategories = useMemo(() => {
    return Array.from(new Set(tasks.map((task) => task.category))).sort((left, right) => left.localeCompare(right));
  }, [tasks]);
  const activeTaskFilterCount = [
    query.trim().length > 0,
    taskStatusFilter !== "all",
    taskCategoryFilter !== "all",
    taskFocusFilter !== "all",
    taskSortMode !== "priority",
  ].filter(Boolean).length;
  const selectedScheduleHistoryIndex = scheduleHistory.findIndex((historyItem) => historyItem.id === selectedScheduleRunId);
  const previousScheduleHistoryItem =
    selectedScheduleHistoryIndex >= 0 ? scheduleHistory[selectedScheduleHistoryIndex + 1] ?? null : null;

  const timelineItems = useMemo(
    () =>
      schedule
        ? buildTimelineFromSchedule(schedule.items, locale, t)
        : buildTimeline(tasks, fixedEvents, selectedDate, locale, t),
    [fixedEvents, locale, schedule, selectedDate, t, tasks],
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
    scheduleSource === "saved"
      ? t("Saved schedule")
      : scheduleSource === "generated"
        ? t("Generated schedule")
        : scheduleSource === "history"
          ? t("Schedule history")
          : t("Today planner");
  const plannedTimeDetail =
    scheduleSource === "saved"
      ? t("from latest saved schedule")
      : scheduleSource === "generated"
        ? t("from generated schedule")
        : scheduleSource === "history"
          ? t("from selected history run")
          : t("from backend tasks");
  const scheduleCoverage =
    algorithmSummary && algorithmSummary.selected_task_count > 0
      ? Math.round((algorithmSummary.scheduled_task_count / algorithmSummary.selected_task_count) * 100)
      : null;
  const ringValue = scheduleCoverage ?? completionRate;
  const ringLabel = scheduleCoverage !== null ? t("Coverage") : t("Completion");
  const nextFixedEvent =
    [...fixedEvents]
      .sort((left, right) => left.start_time.localeCompare(right.start_time))
      .find((event) => new Date(event.end_time) > now) ?? null;

  const insights: InsightItem[] = algorithmSummary
    ? [
        {
          label: t("Scheduled tasks"),
          value: `${algorithmSummary.scheduled_task_count}/${algorithmSummary.selected_task_count}`,
          detail: `${algorithmSummary.skipped_task_count} ${t("skipped by capacity or dependencies")}`,
        },
        {
          label: t("Free capacity"),
          value: formatMinutes(algorithmSummary.available_minutes, locale),
          detail: `${algorithmSummary.applied_algorithms.length} ${t("scheduler algorithms applied")}`,
        },
        {
          label: t("Work selected"),
          value: formatMinutes(scheduledTaskMinutes, locale),
          detail: algorithmSummary.warnings[0] ?? t("No scheduler warnings"),
        },
      ]
    : [
        {
          label: t("Completion forecast"),
          value: `${Math.min(96, completionRate + 24)}%`,
          detail: t("Uses current queue and protected events"),
        },
        {
          label: t("Estimate drift"),
          value: formatSignedMinutes(estimateDeltaMinutes, locale),
          detail: t("Actual minus estimated work time"),
        },
        {
          label: t("Predicted workload"),
          value: formatMinutes(predictedMinutes, locale),
          detail: durationPredictions
            ? `${durationPredictions.model_name} ${durationPredictions.model_version}`
            : t("ML service not loaded"),
        },
      ];

  function closeDateScopedEditors() {
    setQuery("");
    setIsTaskFormOpen(false);
    setIsFixedEventFormOpen(false);
    cancelEditingTask();
    cancelEditingFixedEvent();
    cancelRenamingScheduleRun();
  }

  function selectDate(nextDate: string) {
    if (nextDate.length === 0) {
      return;
    }

    setSelectedDate(nextDate);
    closeDateScopedEditors();
  }

  function changeSelectedDate(days: number) {
    setSelectedDate((currentDate) => shiftDate(currentDate, days));
    closeDateScopedEditors();
  }

  function clearTaskFilters() {
    setQuery("");
    setTaskStatusFilter("all");
    setTaskCategoryFilter("all");
    setTaskFocusFilter("all");
    setTaskSortMode("priority");
  }

  function startEditingTask(task: ApiTask) {
    setError(null);
    setIsTaskFormOpen(false);
    setEditingTaskId(task.id);
    setEditTaskForm(taskFormFromTask(task));
  }

  function cancelEditingTask() {
    setEditingTaskId(null);
    setEditTaskForm(emptyTaskForm);
  }

  function startEditingFixedEvent(event: ApiFixedEvent) {
    setError(null);
    setIsFixedEventFormOpen(false);
    setEditingFixedEventId(event.id);
    setEditFixedEventForm(fixedEventFormFromEvent(event));
  }

  function cancelEditingFixedEvent() {
    setEditingFixedEventId(null);
    setEditFixedEventForm(emptyFixedEventForm);
  }

  function startRenamingScheduleRun(historyItem: ApiScheduleHistoryItem) {
    setError(null);
    setEditingScheduleRunId(historyItem.id);
    setScheduleRunTitleDraft(historyItem.title);
  }

  function cancelRenamingScheduleRun() {
    setEditingScheduleRunId(null);
    setScheduleRunTitleDraft("");
  }

  async function refreshScheduleHistory() {
    const nextScheduleHistory = await requestJson<ApiScheduleHistoryItem[]>(
      `${API_BASE_URL}/schedules/history?target_date=${selectedDate}&limit=5`,
      { headers: buildAuthHeaders() },
    );
    setScheduleHistory(nextScheduleHistory);
    return nextScheduleHistory;
  }

  function selectScheduleHistoryItem(historyItem: ApiScheduleHistoryItem) {
    setSchedule(historyItem.schedule);
    setScheduleSource("history");
    setSelectedScheduleRunId(historyItem.id);
    setScheduleDiff(null);
  }

  function applyUpdatedScheduleRun(updatedScheduleRun: ApiScheduleHistoryItem) {
    setScheduleHistory((currentHistory) =>
      currentHistory.map((historyItem) =>
        historyItem.id === updatedScheduleRun.id ? updatedScheduleRun : historyItem,
      ),
    );
    if (selectedScheduleRunId === updatedScheduleRun.id) {
      setSchedule(updatedScheduleRun.schedule);
      setScheduleSource("history");
    }
  }

  async function toggleScheduleItemLock(item: TimelineItem) {
    if (selectedScheduleRunId === null || !item.itemKey) {
      setError(t("Select a generated plan before editing schedule items"));
      return;
    }

    setError(null);
    try {
      const updatedScheduleRun = await requestJson<ApiScheduleHistoryItem>(
        `${API_BASE_URL}/schedules/history/${selectedScheduleRunId}/items/${encodeURIComponent(item.itemKey)}/lock`,
        {
          method: "PATCH",
          headers: buildAuthHeaders(),
          body: JSON.stringify({ locked: !item.locked }),
        },
      );
      applyUpdatedScheduleRun(updatedScheduleRun);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : t("Unable to update schedule item"));
    }
  }

  async function moveScheduleItem(item: TimelineItem, offsetMinutes: number) {
    if (selectedScheduleRunId === null || !item.itemKey || schedule === null) {
      setError(t("Select a generated plan before editing schedule items"));
      return;
    }

    const currentItem = schedule.items.find((scheduleItem) => scheduleItemKey(scheduleItem) === item.itemKey);
    if (!currentItem) {
      setError(t("Unable to update schedule item"));
      return;
    }

    setError(null);
    try {
      const updatedScheduleRun = await requestJson<ApiScheduleHistoryItem>(
        `${API_BASE_URL}/schedules/history/${selectedScheduleRunId}/items/${encodeURIComponent(item.itemKey)}/time`,
        {
          method: "PATCH",
          headers: buildAuthHeaders(),
          body: JSON.stringify({
            start_time: offsetDateTime(currentItem.start_time, offsetMinutes),
            end_time: offsetDateTime(currentItem.end_time, offsetMinutes),
          }),
        },
      );
      applyUpdatedScheduleRun(updatedScheduleRun);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : t("Unable to update schedule item"));
    }
  }

  async function compareScheduleWithPrevious() {
    if (selectedScheduleRunId === null || previousScheduleHistoryItem === null) {
      setError(t("Select a generated plan with an older run to compare"));
      return;
    }

    setIsComparing(true);
    setError(null);

    try {
      const nextScheduleDiff = await requestJson<ApiScheduleDiffResponse>(
        `${API_BASE_URL}/schedules/history/${selectedScheduleRunId}/diff?against_run_id=${previousScheduleHistoryItem.id}`,
        { headers: buildAuthHeaders() },
      );
      setScheduleDiff(nextScheduleDiff);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : t("Unable to compare schedules"));
    } finally {
      setIsComparing(false);
    }
  }

  async function exportSelectedSchedule(exportFormat: "markdown" | "csv" | "pdf") {
    if (selectedScheduleRunId === null) {
      setError(t("Select a generated plan before exporting"));
      return;
    }

    setIsExportingSchedule(true);
    setError(null);

    try {
      const exportedSchedule = await requestJson<ApiScheduleExportResponse>(
        `${API_BASE_URL}/schedules/history/${selectedScheduleRunId}/export?format=${exportFormat}`,
        { headers: buildAuthHeaders() },
      );
      if (exportedSchedule.encoding === "base64") {
        downloadBase64File(exportedSchedule.filename, exportedSchedule.content, exportedSchedule.content_type);
      } else {
        downloadTextFile(exportedSchedule.filename, exportedSchedule.content, exportedSchedule.content_type);
      }
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : t("Unable to export schedule"));
    } finally {
      setIsExportingSchedule(false);
    }
  }

  async function renameScheduleRun(scheduleRunId: number) {
    const title = scheduleRunTitleDraft.trim();
    if (title.length === 0) {
      setError(t("Schedule title is required"));
      return;
    }

    setIsMutating(true);
    setError(null);

    try {
      const updatedScheduleRun = await requestJson<ApiScheduleHistoryItem>(
        `${API_BASE_URL}/schedules/history/${scheduleRunId}`,
        {
          method: "PATCH",
          headers: buildAuthHeaders(),
          body: JSON.stringify({ title }),
        },
      );
      setScheduleHistory((currentHistory) =>
        currentHistory.map((historyItem) =>
          historyItem.id === updatedScheduleRun.id ? updatedScheduleRun : historyItem,
        ),
      );
      setScheduleDiff(null);
      cancelRenamingScheduleRun();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : t("Unable to rename schedule"));
    } finally {
      setIsMutating(false);
    }
  }

  async function deleteScheduleRun(scheduleRunId: number) {
    const shouldDelete = window.confirm(t("Remove this generated plan from schedule history?"));
    if (!shouldDelete) {
      return;
    }

    setIsMutating(true);
    setError(null);

    try {
      await requestJson<{ deleted: boolean }>(
        `${API_BASE_URL}/schedules/history/${scheduleRunId}`,
        { method: "DELETE", headers: buildAuthHeaders() },
      );
      const nextScheduleHistory = await refreshScheduleHistory();
      if (selectedScheduleRunId === scheduleRunId) {
        const nextSelectedRun = nextScheduleHistory[0] ?? null;
        setSchedule(nextSelectedRun?.schedule ?? null);
        setScheduleSource(nextSelectedRun ? "history" : "none");
        setSelectedScheduleRunId(nextSelectedRun?.id ?? null);
      }
      setScheduleDiff(null);
      if (editingScheduleRunId === scheduleRunId) {
        cancelRenamingScheduleRun();
      }
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : t("Unable to delete schedule"));
    } finally {
      setIsMutating(false);
    }
  }

  async function generatePlan() {
    setIsGenerating(true);
    setError(null);

    try {
      const nextSchedule = await requestJson<ApiScheduleResponse>(`${API_BASE_URL}/schedules/generate`, {
        method: "POST",
        headers: buildAuthHeaders(),
        body: JSON.stringify({
          target_date: selectedDate,
          planning_mode: "balanced",
          start_hour: 9,
          end_hour: 23,
          buffer_minutes: 10,
          include_fixed_events: true,
        }),
      });

      setSchedule(nextSchedule);
      setScheduleSource("generated");
      const nextScheduleHistory = await refreshScheduleHistory();
      setSelectedScheduleRunId(nextScheduleHistory[0]?.id ?? null);
      setScheduleDiff(null);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : t("Unable to generate plan"));
    } finally {
      setIsGenerating(false);
    }
  }

  async function createTask() {
    const formError = getTaskFormError(taskForm, t);
    if (formError) {
      setError(formError);
      return;
    }

    setIsMutating(true);
    setError(null);

    try {
      await requestJson<ApiTask>(`${API_BASE_URL}/tasks`, {
        method: "POST",
        headers: buildAuthHeaders(),
        body: JSON.stringify({
          description: "",
          ...buildTaskMutationPayload(taskForm, selectedDate),
          is_fixed: false,
          is_splittable: false,
          dependency_ids: [],
        }),
      });

      setTaskForm(emptyTaskForm);
      setIsTaskFormOpen(false);
      cancelEditingTask();
      await loadDashboardData();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : t("Unable to create task"));
    } finally {
      setIsMutating(false);
    }
  }

  async function updateTaskDetails(taskId: number) {
    const formError = getTaskFormError(editTaskForm, t);
    if (formError) {
      setError(formError);
      return;
    }

    setIsMutating(true);
    setError(null);

    try {
      await requestJson<ApiTask>(`${API_BASE_URL}/tasks/${taskId}`, {
        method: "PATCH",
        headers: buildAuthHeaders(),
        body: JSON.stringify(buildTaskMutationPayload(editTaskForm, selectedDate)),
      });

      cancelEditingTask();
      await loadDashboardData();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : t("Unable to update task"));
    } finally {
      setIsMutating(false);
    }
  }

  async function createFixedEvent() {
    const formError = getFixedEventFormError(fixedEventForm, t);
    if (formError) {
      setError(formError);
      return;
    }

    setIsMutating(true);
    setError(null);

    try {
      await requestJson<ApiFixedEvent>(`${API_BASE_URL}/fixed-events`, {
        method: "POST",
        headers: buildAuthHeaders(),
        body: JSON.stringify({
          ...buildFixedEventMutationPayload(fixedEventForm, selectedDate),
        }),
      });

      setFixedEventForm(emptyFixedEventForm);
      setIsFixedEventFormOpen(false);
      cancelEditingFixedEvent();
      await loadDashboardData();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : t("Unable to create fixed event"));
    } finally {
      setIsMutating(false);
    }
  }

  async function updateFixedEventDetails(fixedEventId: number) {
    const formError = getFixedEventFormError(editFixedEventForm, t);
    if (formError) {
      setError(formError);
      return;
    }

    setIsMutating(true);
    setError(null);

    try {
      await requestJson<ApiFixedEvent>(`${API_BASE_URL}/fixed-events/${fixedEventId}`, {
        method: "PATCH",
        headers: buildAuthHeaders(),
        body: JSON.stringify(buildFixedEventMutationPayload(editFixedEventForm, selectedDate)),
      });

      cancelEditingFixedEvent();
      await loadDashboardData();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : t("Unable to update fixed event"));
    } finally {
      setIsMutating(false);
    }
  }

  async function deleteFixedEvent(fixedEventId: number) {
    const shouldDelete = window.confirm(t("Delete this fixed event?"));
    if (!shouldDelete) {
      return;
    }

    setIsMutating(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/fixed-events/${fixedEventId}`, {
        method: "DELETE",
        headers: buildAuthHeaders(),
      });
      if (!response.ok) {
        throw new Error(`Delete failed with ${response.status}`);
      }

      await loadDashboardData();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : t("Unable to delete fixed event"));
    } finally {
      setIsMutating(false);
    }
  }

  async function resetDemoData() {
    const shouldReset = window.confirm(t("Reset demo data for user 1? This clears demo tasks, events, logs, and schedules."));
    if (!shouldReset) {
      return;
    }

    setIsMutating(true);
    setError(null);

    try {
      await requestJson(`${API_BASE_URL}/demo/reset?user_id=${DEMO_USER_ID}`, {
        method: "POST",
      });
      closeDateScopedEditors();
      if (selectedDate === DEFAULT_SELECTED_DATE) {
        await loadDashboardData();
      } else {
        setSelectedDate(DEFAULT_SELECTED_DATE);
      }
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : t("Unable to reset demo data"));
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
        headers: buildAuthHeaders(),
        body: JSON.stringify({}),
      });
      await loadDashboardData();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : t("Unable to record execution event"));
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
        headers: buildAuthHeaders(),
        body: status === "pending" ? undefined : JSON.stringify({ status }),
      });
      await loadDashboardData();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : t("Unable to update task"));
    } finally {
      setIsMutating(false);
    }
  }

  async function deleteTask(taskId: number) {
    const shouldDelete = window.confirm(t("Delete this task?"));
    if (!shouldDelete) {
      return;
    }

    setIsMutating(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
        method: "DELETE",
        headers: buildAuthHeaders(),
      });
      if (!response.ok) {
        throw new Error(`Delete failed with ${response.status}`);
      }

      await loadDashboardData();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : t("Unable to delete task"));
    } finally {
      setIsMutating(false);
    }
  }

  return (
    <div className="product-shell">
      <aside className="sidebar" aria-label={t("Workspace navigation")}>
        <div className="brand-lockup">
          <div className="brand-mark" aria-hidden="true">
            O
          </div>
          <div>
            <strong>OrdoStack</strong>
            <span>{t("Daily Planning OS")}</span>
          </div>
        </div>

        <nav className="sidebar-nav" aria-label={t("Primary")}>
          {navigationItems.map((item) => (
            <button
              key={item.view}
              className={activeView === item.view ? "nav-item active" : "nav-item"}
              type="button"
              aria-current={activeView === item.view ? "page" : undefined}
              onClick={() => setActiveView(item.view)}
            >
              <item.icon size={18} aria-hidden="true" />
              <span>{t(item.label)}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-status" aria-label={t("Service health")}>
          <div className="status-heading">
            <Activity size={16} aria-hidden="true" />
            <span>{t("System")}</span>
          </div>
          {serviceHealth.map((service) => (
            <div key={service} className="status-row">
              <span className="health-dot" aria-hidden="true" />
              <span>{service}</span>
              <strong>{t("ok")}</strong>
            </div>
          ))}
        </div>
      </aside>

      <main className="workspace" aria-labelledby="page-title">
        <header className="topbar">
          <div className="date-control" aria-label={t("Selected date")}>
            <button
              className="icon-button"
              type="button"
              aria-label={t("Previous day")}
              title={`${t("Previous day")} (Alt+←)`}
              aria-keyshortcuts="Alt+ArrowLeft"
              disabled={isLoading}
              onClick={() => changeSelectedDate(-1)}
            >
              <ChevronLeft size={18} aria-hidden="true" />
            </button>
            <div>
              <span>{formatWeekday(selectedDate, locale)}</span>
              <strong>{formatSelectedDate(selectedDate, locale)}</strong>
            </div>
            <label className="date-picker" aria-label={t("Choose date")}>
              <CalendarDays size={16} aria-hidden="true" />
              <input
                type="date"
                value={selectedDate}
                disabled={isLoading}
                onChange={(event) => selectDate(event.target.value)}
              />
            </label>
            <button
              className="icon-button"
              type="button"
              aria-label={t("Next day")}
              title={`${t("Next day")} (Alt+→)`}
              aria-keyshortcuts="Alt+ArrowRight"
              disabled={isLoading}
              onClick={() => changeSelectedDate(1)}
            >
              <ChevronRight size={18} aria-hidden="true" />
            </button>
            <button
              className="ghost-button text-button"
              type="button"
              title={`${t("Today")} (Alt+T)`}
              aria-keyshortcuts="Alt+T"
              disabled={isLoading || selectedDate === todayDateString()}
              onClick={() => selectDate(todayDateString())}
            >
              {t("Today")}
            </button>
          </div>

          <div className="topbar-actions">
            <section className="auth-panel" aria-label={t("Account")}>
              {currentUser ? (
                <div className="auth-summary">
                  <UserCircle size={18} aria-hidden="true" />
                  <div>
                    <strong>{currentUser.display_name}</strong>
                    <span>{currentUser.email}</span>
                  </div>
                  <button
                    className="ghost-button"
                    type="button"
                    aria-label={t("Sign out")}
                    disabled={isAuthenticating}
                    onClick={signOut}
                  >
                    <LogOut size={16} aria-hidden="true" />
                  </button>
                </div>
              ) : (
                <form
                  className="auth-form"
                  onSubmit={(event) => {
                    event.preventDefault();
                    void submitAuthForm();
                  }}
                >
                  <div className="auth-mode" role="tablist" aria-label={t("Authentication mode")}>
                    <button
                      className={authMode === "login" ? "active" : ""}
                      type="button"
                      role="tab"
                      aria-selected={authMode === "login"}
                      onClick={() => setAuthMode("login")}
                    >
                      {t("Login")}
                    </button>
                    <button
                      className={authMode === "register" ? "active" : ""}
                      type="button"
                      role="tab"
                      aria-selected={authMode === "register"}
                      onClick={() => setAuthMode("register")}
                    >
                      {t("Register")}
                    </button>
                  </div>
                  <label>
                    <span>{t("Email")}</span>
                    <input
                      type="email"
                      autoComplete="email"
                      value={authForm.email}
                      disabled={isAuthenticating}
                      onChange={(event) =>
                        setAuthForm((currentForm) => ({ ...currentForm, email: event.target.value }))
                      }
                    />
                  </label>
                  {authMode === "register" ? (
                    <label>
                      <span>{t("Name")}</span>
                      <input
                        autoComplete="name"
                        value={authForm.displayName}
                        disabled={isAuthenticating}
                        onChange={(event) =>
                          setAuthForm((currentForm) => ({ ...currentForm, displayName: event.target.value }))
                        }
                      />
                    </label>
                  ) : null}
                  <label>
                    <span>{t("Password")}</span>
                    <input
                      type="password"
                      autoComplete={authMode === "register" ? "new-password" : "current-password"}
                      value={authForm.password}
                      disabled={isAuthenticating}
                      onChange={(event) =>
                        setAuthForm((currentForm) => ({ ...currentForm, password: event.target.value }))
                      }
                    />
                  </label>
                  <button className="secondary-action" type="submit" disabled={isAuthenticating}>
                    <LogIn size={16} aria-hidden="true" />
                    <span>{authMode === "register" ? t("Create") : t("Login")}</span>
                  </button>
                  <button
                    className="ghost-button text-button"
                    type="button"
                    disabled={isAuthenticating}
                    onClick={() => void loginDemoUser()}
                  >
                    {t("Demo")}
                  </button>
                </form>
              )}
              {authStatus ? (
                <p className="auth-status" role="status" aria-live="polite">
                  {authStatus}
                </p>
              ) : null}
            </section>
            <label className="search-box" aria-label={t("Search tasks")}>
              <Search size={17} aria-hidden="true" />
              <input
                type="search"
                placeholder={t("Search tasks")}
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
            </label>
            <button
              className="primary-action"
              type="button"
              title={`${t("Generate Plan")} (Alt+G)`}
              aria-keyshortcuts="Alt+G"
              disabled={!authToken || isGenerating || isLoading || isMutating}
              onClick={() => void generatePlan()}
            >
              {isGenerating ? (
                <Loader2 className="spinning" size={18} aria-hidden="true" />
              ) : (
                <Sparkles size={18} aria-hidden="true" />
              )}
              <span>{isGenerating ? t("Generating") : t("Generate Plan")}</span>
            </button>
          </div>
        </header>

        {error ? (
          <div className="alert-banner" role="alert">
            <AlertCircle size={18} aria-hidden="true" />
            <span>{error}</span>
            <button className="ghost-button text-button" type="button" onClick={() => void loadDashboardData()}>
              {t("Retry")}
            </button>
          </div>
        ) : null}

        {isLoading ? (
          <section className="loading-panel" aria-label={t("Loading dashboard data")}>
            <Loader2 size={22} aria-hidden="true" />
            <span>{t("Loading task and fixed event data...")}</span>
          </section>
        ) : (
          <>
            {activeView === "today" || activeView === "analytics" ? (
            <section className="overview-strip" aria-label={t("Daily overview")}>
              <article>
                <span>{t("Completion")}</span>
                <strong>{completionRate}%</strong>
                <em>
                  {completedTasks} / {totalTasks} {t("tasks done")}
                </em>
              </article>
              <article>
                <span>{t("Planned time")}</span>
                <strong>{formatMinutes(scheduledTaskMinutes, locale)}</strong>
                <em>{plannedTimeDetail}</em>
              </article>
              <article>
                <span>{t("Protected events")}</span>
                <strong>{fixedEvents.length}</strong>
                <em>{t("fixed schedule blocks")}</em>
              </article>
              <article>
                <span>{t("Actual time")}</span>
                <strong>{formatMinutes(actualMinutes, locale)}</strong>
                <em>
                  {formatSignedMinutes(estimateDeltaMinutes, locale)} {t("estimate drift")}
                </em>
              </article>
            </section>
            ) : null}

            {activeView === "today" || activeView === "tasks" || activeView === "schedule" ? (
            <div
              className={
                activeView === "tasks"
                  ? "workspace-grid solo"
                  : activeView === "schedule"
                    ? "workspace-grid duo"
                    : "workspace-grid"
              }
            >
              {activeView === "today" || activeView === "schedule" ? (
              <section className="timeline-surface" aria-labelledby="page-title">
                <div className="section-header">
                  <div>
                    <p className="section-kicker">{scheduleKicker}</p>
                    <h1 id="page-title">{t("Focused schedule")}</h1>
                  </div>
                <button
                  className="secondary-action"
                  type="button"
                  disabled={!authToken || isMutating}
                  onClick={() => {
                    setIsTaskFormOpen((isOpen) => !isOpen);
                    cancelEditingTask();
                    }}
                  >
                    <Plus size={17} aria-hidden="true" />
                    <span>{t("Add task")}</span>
                  </button>
                </div>

                {!schedule && timelineItems.length > 0 ? (
                  <p className="preview-note">{t("Preview times. Generate a plan to schedule these tasks.")}</p>
                ) : null}

                {isTaskFormOpen ? (
                  <form
                    className="inline-form"
                    onSubmit={(event) => {
                      event.preventDefault();
                      void createTask();
                    }}
                  >
                    <TaskFormFields form={taskForm} onChange={setTaskForm} t={t} />
                    <button className="primary-action" type="submit" disabled={isMutating}>
                      <Plus size={17} aria-hidden="true" />
                      <span>{t("Create task")}</span>
                    </button>
                  </form>
                ) : null}

                {timelineItems.length > 0 ? (
                  <div className="timeline">
                    {timelineItems.map((item) => {
                      const isCurrent = isCurrentTimelineItem(item, now);
                      return (
                      <article
                        key={`${item.start}-${item.title}`}
                        className={`timeline-item ${item.type}${isCurrent ? " current" : ""}`}
                      >
                        <div className="time-range">
                          <strong>{item.start}</strong>
                          <span>{item.end}</span>
                          {isCurrent ? <em className="now-pill">{t("Now")}</em> : null}
                        </div>
                        <div className="timeline-block">
                          <div>
                            <h2>{item.title}</h2>
                            <p>{item.meta}</p>
                          </div>
                          {item.itemKey ? (
                            <div className="timeline-actions">
                              <button
                                className="ghost-button"
                                type="button"
                                aria-label={`${item.locked ? t("Unlock") : t("Lock")} ${item.title}`}
                                onClick={() => void toggleScheduleItemLock(item)}
                              >
                                {item.locked ? <Unlock size={17} /> : <Lock size={17} />}
                              </button>
                              <button
                                className="ghost-button"
                                type="button"
                                aria-label={`${t("Move earlier")} ${item.title}`}
                                onClick={() => void moveScheduleItem(item, -15)}
                              >
                                <ChevronLeft size={17} />
                              </button>
                              <button
                                className="ghost-button"
                                type="button"
                                aria-label={`${t("Move later")} ${item.title}`}
                                onClick={() => void moveScheduleItem(item, 15)}
                              >
                                <ChevronRight size={17} />
                              </button>
                            </div>
                          ) : null}
                        </div>
                      </article>
                      );
                    })}
                  </div>
                ) : (
                  <div className="empty-state tall-state">
                    <strong>{t("No schedule blocks")}</strong>
                    <span>{t("Add tasks or fixed events, then generate a plan.")}</span>
                  </div>
                )}

                <section className="schedule-history-panel" aria-label={t("Schedule history")}>
                  <div>
                    <p className="section-kicker">{t("Schedule history")}</p>
                    <h2>{t("Recent generated plans")}</h2>
                  </div>
                  {scheduleHistory.length > 0 ? (
                    <>
                      <div className="schedule-history-list">
                      {scheduleHistory.map((historyItem) => (
                        <article
                          key={historyItem.id}
                          className={
                            selectedScheduleRunId === historyItem.id
                              ? "schedule-history-row active"
                              : "schedule-history-row"
                          }
                        >
                          {editingScheduleRunId === historyItem.id ? (
                            <div className="schedule-history-editor">
                              <input
                                aria-label={`${t("Schedule title for")} ${historyItem.title}`}
                                value={scheduleRunTitleDraft}
                                maxLength={120}
                                onChange={(event) => setScheduleRunTitleDraft(event.target.value)}
                              />
                              <button
                                className="ghost-button"
                                type="button"
                                aria-label={`${t("Save")} ${historyItem.title}`}
                                disabled={isMutating}
                                onClick={() => void renameScheduleRun(historyItem.id)}
                              >
                                <CheckCircle2 size={17} />
                              </button>
                              <button
                                className="ghost-button text-button"
                                type="button"
                                disabled={isMutating}
                                onClick={cancelRenamingScheduleRun}
                              >
                                {t("Cancel")}
                              </button>
                            </div>
                          ) : (
                            <>
                              <button
                                className="schedule-history-main"
                                type="button"
                                onClick={() => selectScheduleHistoryItem(historyItem)}
                              >
                                <span>{formatTime(historyItem.created_at)}</span>
                                <strong>{historyItem.title}</strong>
                                <em>
                                  {historyItem.planning_mode} | {historyItem.scheduled_task_count} {t("Tasks")} |{" "}
                                  {historyItem.item_count} {t("blocks")}
                                </em>
                              </button>
                              <div className="schedule-history-actions">
                                <button
                                  className="ghost-button"
                                  type="button"
                                  aria-label={`${t("Rename")} ${historyItem.title}`}
                                  disabled={isMutating}
                                  onClick={() => startRenamingScheduleRun(historyItem)}
                                >
                                  <Pencil size={16} />
                                </button>
                                <button
                                  className="ghost-button danger"
                                  type="button"
                                  aria-label={`${t("Delete")} ${historyItem.title}`}
                                  disabled={isMutating}
                                  onClick={() => void deleteScheduleRun(historyItem.id)}
                                >
                                  <Trash2 size={16} />
                                </button>
                              </div>
                            </>
                          )}
                        </article>
                      ))}
                      </div>
                      <div className="schedule-compare-bar">
                        <button
                          className="secondary-action"
                          type="button"
                          disabled={!authToken || isComparing || previousScheduleHistoryItem === null}
                          onClick={() => void compareScheduleWithPrevious()}
                        >
                          {isComparing ? (
                            <Loader2 className="spinning" size={16} aria-hidden="true" />
                          ) : (
                            <Activity size={16} aria-hidden="true" />
                          )}
                          <span>{isComparing ? t("Comparing") : t("Compare previous")}</span>
                        </button>
                        <button
                          className="secondary-action"
                          type="button"
                          disabled={!authToken || isExportingSchedule || selectedScheduleRunId === null}
                          onClick={() => void exportSelectedSchedule("markdown")}
                        >
                          {isExportingSchedule ? (
                            <Loader2 className="spinning" size={16} aria-hidden="true" />
                          ) : (
                            <Download size={16} aria-hidden="true" />
                          )}
                          <span>{isExportingSchedule ? t("Exporting") : t("Export MD")}</span>
                        </button>
                        <button
                          className="secondary-action"
                          type="button"
                          disabled={!authToken || isExportingSchedule || selectedScheduleRunId === null}
                          onClick={() => void exportSelectedSchedule("pdf")}
                        >
                          {isExportingSchedule ? (
                            <Loader2 className="spinning" size={16} aria-hidden="true" />
                          ) : (
                            <Download size={16} aria-hidden="true" />
                          )}
                          <span>{isExportingSchedule ? t("Exporting") : t("Export PDF")}</span>
                        </button>
                      </div>
                      {scheduleDiff ? (
                        <section className="schedule-diff-panel" aria-label={t("Schedule diff")}>
                          <div className="diff-summary">
                            <span>+{scheduleDiff.added_count} {t("added")}</span>
                            <span>-{scheduleDiff.removed_count} {t("removed")}</span>
                            <span>{scheduleDiff.changed_count} {t("changed")}</span>
                            <span>{formatSignedMinutes(scheduleDiff.total_delta_minutes, locale)}</span>
                          </div>
                          {scheduleDiff.changes.length > 0 ? (
                            <div className="diff-list">
                              {scheduleDiff.changes.slice(0, 4).map((change) => (
                                <article key={change.item_key} className={`diff-row ${change.change_type}`}>
                                  <strong>{change.title}</strong>
                                  <span>
                                    {t(change.change_type)} |{" "}
                                    {change.previous_start_time ? formatTime(change.previous_start_time, locale) : t("new")}{" "}
                                    {t("to")}{" "}
                                    {change.next_start_time ? formatTime(change.next_start_time, locale) : t("removed")}
                                  </span>
                                </article>
                              ))}
                            </div>
                          ) : (
                            <div className="empty-state compact-state">{t("No schedule differences.")}</div>
                          )}
                        </section>
                      ) : null}
                    </>
                  ) : (
                    <div className="empty-state compact-state">{t("Generate a plan to create the first saved run.")}</div>
                  )}
                </section>
              </section>
              ) : null}

              {activeView === "today" || activeView === "tasks" ? (
              <section className="queue-surface" aria-labelledby="queue-title">
                <div className="section-header compact">
                  <div>
                    <p className="section-kicker">{t("Task queue")}</p>
                    <h2 id="queue-title">{t("Next candidates")}</h2>
                  </div>
                </div>

                <div className="task-toolbar" aria-label={t("Task filters and sorting")}>
                  <div className="task-toolbar-title">
                    <ListFilter size={16} aria-hidden="true" />
                    <span>
                      {activeTaskFilterCount === 0
                        ? t("All tasks")
                        : `${activeTaskFilterCount} ${t("filters active")}`}
                    </span>
                  </div>
                  <label className="filter-control">
                    <span>{t("Status")}</span>
                    <select
                      value={taskStatusFilter}
                      onChange={(event) => setTaskStatusFilter(event.target.value as TaskStatusFilter)}
                    >
                      <option value="all">{t("All")}</option>
                      <option value="pending">{t("Ready")}</option>
                      <option value="in_progress">{t("Doing")}</option>
                      <option value="completed">{t("Done")}</option>
                      <option value="skipped">{t("Skipped")}</option>
                    </select>
                  </label>
                  <label className="filter-control">
                    <span>{t("Category")}</span>
                    <select value={taskCategoryFilter} onChange={(event) => setTaskCategoryFilter(event.target.value)}>
                      <option value="all">{t("All")}</option>
                      {taskCategories.map((category) => (
                        <option key={category} value={category}>
                          {category}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="filter-control">
                    <span>{t("Focus")}</span>
                    <select
                      value={taskFocusFilter}
                      onChange={(event) => setTaskFocusFilter(event.target.value as TaskFocusFilter)}
                    >
                      <option value="all">{t("All")}</option>
                      <option value="focus">{t("Focus")}</option>
                      <option value="non_focus">{t("Flexible")}</option>
                    </select>
                  </label>
                  <label className="filter-control">
                    <span>{t("Sort")}</span>
                    <select value={taskSortMode} onChange={(event) => setTaskSortMode(event.target.value as TaskSortMode)}>
                      <option value="priority">{t("Priority")}</option>
                      <option value="deadline">{t("DeadlineOption")}</option>
                      <option value="estimate">{t("Estimate")}</option>
                      <option value="status">{t("Status")}</option>
                    </select>
                  </label>
                  <button
                    className="ghost-button text-button"
                    type="button"
                    disabled={activeTaskFilterCount === 0}
                    onClick={clearTaskFilters}
                  >
                    {t("Reset")}
                  </button>
                </div>

                <div className="task-list">
                  {filteredTasks.length === 0 ? (
                    <div className="empty-state">{t("No matching tasks.")}</div>
                  ) : (
                    filteredTasks.map((task) => {
                      const taskExecutionSummary = analyticsByTask.get(task.id);
                      const taskPrediction = predictionsByTask.get(task.id);
                      return (
                        <div key={task.id} className="task-stack">
                          <article className="task-row">
                            <button
                              className="task-check"
                              type="button"
                              aria-label={`${t("Mark")} ${task.title} ${t("completed")}`}
                              disabled={isMutating || task.status === "completed" || task.status === "skipped"}
                              onClick={() => void recordExecutionEvent(task.id, "complete")}
                            >
                              <CheckCircle2 size={18} />
                            </button>
                            <div className="task-copy">
                              <h3>{task.title}</h3>
                              <p>
                                {task.category} | {t("estimate")} {formatMinutes(task.estimated_minutes, locale)} |{" "}
                                {t("predicted")}{" "}
                                {formatMinutes(
                                  taskPrediction?.predicted_minutes ??
                                    task.predicted_minutes ??
                                    task.estimated_minutes,
                                  locale,
                                )}{" "}
                                | {t("actual")} {formatMinutes(taskExecutionSummary?.actual_minutes ?? 0, locale)}
                              </p>
                            </div>
                            <div className="task-meta">
                              <span className={`priority ${priorityClass(task.priority)}`}>
                                {priorityLabel(task.priority)}
                              </span>
                              <strong>{taskStateLabel(task.status, t)}</strong>
                            </div>
                            <div className="row-actions">
                              <button
                                className="ghost-button"
                                type="button"
                                aria-label={`${t("Edit")} ${task.title}`}
                                disabled={isMutating}
                                onClick={() => startEditingTask(task)}
                              >
                                <Pencil size={17} />
                              </button>
                              {task.status === "pending" ? (
                                <button
                                  className="ghost-button"
                                  type="button"
                                  aria-label={`${t("Start")} ${task.title}`}
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
                                  aria-label={`${t("Pause")} ${task.title}`}
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
                                  aria-label={`${t("Skip")} ${task.title}`}
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
                                  aria-label={`${t("Reopen")} ${task.title}`}
                                  disabled={isMutating}
                                  onClick={() => void updateTaskStatus(task.id, "pending")}
                                >
                                  <RotateCcw size={17} />
                                </button>
                              ) : null}
                              <button
                                className="ghost-button danger"
                                type="button"
                                aria-label={`${t("Delete")} ${task.title}`}
                                disabled={isMutating}
                                onClick={() => void deleteTask(task.id)}
                              >
                                <Trash2 size={17} />
                              </button>
                            </div>
                          </article>

                          {editingTaskId === task.id ? (
                            <form
                              className="inline-form task-edit-form"
                              aria-label={`${t("Edit")} ${task.title}`}
                              onSubmit={(event) => {
                                event.preventDefault();
                                void updateTaskDetails(task.id);
                              }}
                            >
                              <TaskFormFields form={editTaskForm} onChange={setEditTaskForm} t={t} />
                              <div className="form-actions">
                                <button className="primary-action" type="submit" disabled={isMutating}>
                                  <CheckCircle2 size={17} aria-hidden="true" />
                                  <span>{t("Save changes")}</span>
                                </button>
                                <button
                                  className="ghost-button text-button"
                                  type="button"
                                  disabled={isMutating}
                                  onClick={cancelEditingTask}
                                >
                                  {t("Cancel")}
                                </button>
                              </div>
                            </form>
                          ) : null}
                        </div>
                      );
                    })
                  )}
                </div>

                <div className="fixed-events-panel">
                  <div className="section-header compact">
                    <div>
                      <p className="section-kicker">{t("Fixed events")}</p>
                      <h2>{t("Protected time")}</h2>
                    </div>
                    <button
                      className="secondary-action"
                      type="button"
                      disabled={!authToken || isMutating}
                      onClick={() => {
                        setIsFixedEventFormOpen((isOpen) => !isOpen);
                        cancelEditingFixedEvent();
                      }}
                    >
                      <Plus size={16} aria-hidden="true" />
                      <span>{t("Add")}</span>
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
                      <FixedEventFormFields form={fixedEventForm} onChange={setFixedEventForm} t={t} />
                      <button className="primary-action" type="submit" disabled={isMutating}>
                        <Plus size={16} aria-hidden="true" />
                        <span>{t("Create event")}</span>
                      </button>
                    </form>
                  ) : null}

                  {fixedEvents.length > 0 ? (
                    <div className="fixed-event-list">
                      {fixedEvents.map((event) => (
                        <div key={event.id} className="fixed-event-stack">
                          <article className="fixed-event-row">
                            <CalendarDays size={17} aria-hidden="true" />
                            <div>
                              <strong>{event.title}</strong>
                              <span>
                                {formatTime(event.start_time, locale)} - {formatTime(event.end_time, locale)}
                              </span>
                            </div>
                            <div className="row-actions">
                              <button
                                className="ghost-button"
                                type="button"
                                aria-label={`${t("Edit")} ${event.title}`}
                                disabled={isMutating}
                                onClick={() => startEditingFixedEvent(event)}
                              >
                                <Pencil size={16} />
                              </button>
                              <button
                                className="ghost-button danger"
                                type="button"
                                aria-label={`${t("Delete")} ${event.title}`}
                                disabled={isMutating}
                                onClick={() => void deleteFixedEvent(event.id)}
                              >
                                <Trash2 size={16} />
                              </button>
                            </div>
                          </article>

                          {editingFixedEventId === event.id ? (
                            <form
                              className="inline-form compact-form fixed-event-edit-form"
                              aria-label={`${t("Edit")} ${event.title}`}
                              onSubmit={(formEvent) => {
                                formEvent.preventDefault();
                                void updateFixedEventDetails(event.id);
                              }}
                            >
                              <FixedEventFormFields form={editFixedEventForm} onChange={setEditFixedEventForm} t={t} />
                              <div className="form-actions">
                                <button className="primary-action" type="submit" disabled={isMutating}>
                                  <CheckCircle2 size={16} aria-hidden="true" />
                                  <span>{t("Save event")}</span>
                                </button>
                                <button
                                  className="ghost-button text-button"
                                  type="button"
                                  disabled={isMutating}
                                  onClick={cancelEditingFixedEvent}
                                >
                                  {t("Cancel")}
                                </button>
                              </div>
                            </form>
                          ) : null}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-state compact-state">{t("No fixed events on this date.")}</div>
                  )}
                </div>
              </section>
              ) : null}

              {activeView === "today" || activeView === "schedule" ? (
              <aside className="insight-surface" aria-labelledby="insight-title">
                <div className="section-header compact">
                  <div>
                    <p className="section-kicker">{t("Plan review")}</p>
                    <h2 id="insight-title">{t("Plan quality")}</h2>
                  </div>
                  <Target size={19} aria-hidden="true" />
                </div>

                <div className="score-ring" aria-label={`${ringLabel} ${ringValue}%`}>
                  <span>{ringValue}%</span>
                  <strong>{ringLabel}</strong>
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
                        ? `${scheduleSource === "saved" ? t("saved ") : ""}${
                            schedule.algorithm_summary.applied_algorithms.length
                          } ${t("scheduler algorithms")} + ${durationPredictions?.model_name ?? t("estimate-fallback")}`
                        : durationPredictions?.model_name ?? t("duration-baseline")}
                    </span>
                  </div>
                  <strong>{durationPredictions?.model_version ?? "-"}</strong>
                </div>
              </aside>
              ) : null}
            </div>
            ) : null}

            {activeView === "today" ? (
            <section className="bottom-rail" aria-label={t("Execution state")}>
              <div>
                <Timer size={18} aria-hidden="true" />
                <span>{t("Current focus")}</span>
                <strong>
                  {tasks.find((task) => task.status === "in_progress")?.title ??
                    tasks.find((task) => task.requires_focus && task.status === "pending")?.title ??
                    t("No focus task")}
                </strong>
              </div>
              <div>
                <Clock3 size={18} aria-hidden="true" />
                <span>{t("Next fixed event")}</span>
                <strong>
                  {nextFixedEvent
                    ? `${nextFixedEvent.title} · ${formatTime(nextFixedEvent.start_time, locale)}`
                    : t("No fixed event")}
                </strong>
              </div>
              <div>
                <Brain size={18} aria-hidden="true" />
                <span>{t("Prediction model")}</span>
                <strong>{durationPredictions?.model_name ?? t("estimate-fallback")}</strong>
              </div>
            </section>
            ) : null}

            {activeView === "analytics" ? (
            <section className="view-panel" aria-labelledby="analytics-title">
              <div className="section-header">
                <div>
                  <p className="section-kicker">{t("Analytics")}</p>
                  <h1 id="analytics-title">{t("Daily analytics")}</h1>
                </div>
              </div>
              {tasks.length > 0 ? (
                <table className="data-table">
                  <thead>
                    <tr>
                      <th scope="col">{t("Task")}</th>
                      <th scope="col">{t("Estimate")}</th>
                      <th scope="col">{t("Predicted")}</th>
                      <th scope="col">{t("Actual")}</th>
                      <th scope="col">{t("Delta")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tasks.map((task) => {
                      const taskActualMinutes = analyticsByTask.get(task.id)?.actual_minutes ?? 0;
                      return (
                        <tr key={task.id}>
                          <td>
                            <strong>{task.title}</strong>
                            <span>{task.category}</span>
                          </td>
                          <td>{formatMinutes(task.estimated_minutes, locale)}</td>
                          <td>
                            {formatMinutes(
                              predictionsByTask.get(task.id)?.predicted_minutes ??
                                task.predicted_minutes ??
                                task.estimated_minutes,
                              locale,
                            )}
                          </td>
                          <td>{taskActualMinutes > 0 ? formatMinutes(taskActualMinutes, locale) : "-"}</td>
                          <td>
                            {taskActualMinutes > 0
                              ? formatSignedMinutes(taskActualMinutes - task.estimated_minutes, locale)
                              : "-"}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              ) : (
                <div className="empty-state">{t("No matching tasks.")}</div>
              )}
            </section>
            ) : null}

            {activeView === "mlops" ? (
            <section className="view-panel" aria-labelledby="mlops-title">
              <div className="section-header">
                <div>
                  <p className="section-kicker">{t("MLOps")}</p>
                  <h1 id="mlops-title">{t("Duration predictions")}</h1>
                </div>
                <div className="model-badge">
                  <Brain size={16} aria-hidden="true" />
                  <span>
                    {durationPredictions?.model_name ?? t("estimate-fallback")}{" "}
                    {durationPredictions?.model_version ?? ""}
                  </span>
                </div>
              </div>
              <p className="view-note">
                {t(
                  "Predictions come from the local ml-service. Without a trained artifact it falls back to a deterministic heuristic, and to raw estimates when the service is unreachable.",
                )}
              </p>
              {durationPredictions && durationPredictions.predictions.length > 0 ? (
                <table className="data-table">
                  <thead>
                    <tr>
                      <th scope="col">{t("Task")}</th>
                      <th scope="col">{t("Estimate")}</th>
                      <th scope="col">{t("Predicted")}</th>
                      <th scope="col">{t("Confidence")}</th>
                      <th scope="col">{t("Reason")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {durationPredictions.predictions.map((prediction) => {
                      const predictionTask = tasks.find((task) => task.id === prediction.task_id);
                      return (
                        <tr key={prediction.task_id}>
                          <td>
                            <strong>{predictionTask?.title ?? `#${prediction.task_id}`}</strong>
                            <span>{predictionTask?.category ?? ""}</span>
                          </td>
                          <td>
                            {predictionTask ? formatMinutes(predictionTask.estimated_minutes, locale) : "-"}
                          </td>
                          <td>{formatMinutes(prediction.predicted_minutes, locale)}</td>
                          <td>{Math.round(prediction.confidence * 100)}%</td>
                          <td className="muted-cell">{prediction.reason}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              ) : (
                <div className="empty-state">{t("No predictions for this date.")}</div>
              )}
            </section>
            ) : null}

            {activeView === "settings" ? (
            <section className="view-panel" aria-labelledby="settings-title">
              <div className="section-header">
                <div>
                  <p className="section-kicker">{t("Workspace")}</p>
                  <h1 id="settings-title">{t("Settings")}</h1>
                </div>
              </div>
              <div className="settings-grid">
                <article className="settings-card">
                  <h2>{t("Account")}</h2>
                  {currentUser ? (
                    <p>
                      <strong>{currentUser.display_name}</strong>
                      <span>{currentUser.email}</span>
                    </p>
                  ) : (
                    <p>
                      <span>{t("Not signed in. Use the top bar to sign in.")}</span>
                    </p>
                  )}
                </article>
                <article className="settings-card">
                  <h2>{t("Language")}</h2>
                  <label className="language-switcher" aria-label={t("Language")}>
                    <span>{t("Interface language")}</span>
                    <select value={locale} onChange={(event) => changeLocale(resolveLocale(event.target.value))}>
                      {localeOptions.map((option) => (
                        <option key={option.code} value={option.code}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </label>
                </article>
                <article className="settings-card">
                  <h2>{t("Keyboard shortcuts")}</h2>
                  <ul className="shortcut-list">
                    <li>
                      <span>{t("Previous or next day")}</span>
                      <kbd>Alt + ← / →</kbd>
                    </li>
                    <li>
                      <span>{t("Jump to today")}</span>
                      <kbd>Alt + T</kbd>
                    </li>
                    <li>
                      <span>{t("Generate Plan")}</span>
                      <kbd>Alt + G</kbd>
                    </li>
                  </ul>
                </article>
                <article className="settings-card">
                  <h2>{t("Demo data")}</h2>
                  <p>
                    <span>{t("Restore the bundled demo dataset.")}</span>
                  </p>
                  <button
                    className="secondary-action"
                    type="button"
                    disabled={isMutating || isLoading}
                    onClick={() => void resetDemoData()}
                  >
                    <RotateCcw size={15} aria-hidden="true" />
                    <span>{t("Reset demo")}</span>
                  </button>
                </article>
              </div>
            </section>
            ) : null}
          </>
        )}
      </main>
    </div>
  );
}
