CREATE TABLE IF NOT EXISTS tasks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  category VARCHAR(50) NOT NULL,
  estimated_minutes INT NOT NULL,
  predicted_minutes INT NULL,
  priority INT NOT NULL,
  difficulty INT NOT NULL,
  deadline DATETIME(6) NULL,
  requires_focus BOOLEAN NOT NULL,
  is_fixed BOOLEAN NOT NULL,
  is_splittable BOOLEAN NOT NULL,
  dependency_ids JSON NOT NULL,
  status VARCHAR(20) NOT NULL,
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NULL,
  deleted_at DATETIME(6) NULL,
  INDEX idx_tasks_user_status (user_id, status),
  INDEX idx_tasks_deadline (deadline)
);

CREATE TABLE IF NOT EXISTS fixed_events (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(255) NOT NULL,
  start_time DATETIME(6) NOT NULL,
  end_time DATETIME(6) NOT NULL,
  event_type VARCHAR(50) NULL,
  recurrence_id VARCHAR(64) NULL,
  recurrence_rule VARCHAR(255) NULL,
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NULL,
  deleted_at DATETIME(6) NULL,
  INDEX idx_fixed_events_user_start (user_id, start_time)
);

CREATE TABLE IF NOT EXISTS execution_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  task_id INT NOT NULL,
  event_type VARCHAR(20) NOT NULL,
  occurred_at DATETIME(6) NOT NULL,
  created_at DATETIME(6) NOT NULL,
  INDEX idx_execution_logs_user_time (user_id, occurred_at),
  INDEX idx_execution_logs_task (task_id)
);

CREATE TABLE IF NOT EXISTS schedule_runs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(120) NOT NULL,
  schedule_date DATE NOT NULL,
  planning_mode VARCHAR(50) NOT NULL,
  request_start_hour INT NULL,
  request_end_hour INT NULL,
  request_buffer_minutes INT NULL,
  include_fixed_events BOOLEAN NOT NULL,
  algorithm_summary JSON NOT NULL,
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NULL,
  deleted_at DATETIME(6) NULL,
  INDEX idx_schedule_runs_user_date (user_id, schedule_date, id),
  INDEX idx_schedule_runs_user_date_active (user_id, schedule_date, deleted_at, id)
);

CREATE TABLE IF NOT EXISTS schedule_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  schedule_run_id INT NOT NULL,
  item_type VARCHAR(20) NOT NULL,
  task_id INT NULL,
  fixed_event_id INT NULL,
  title VARCHAR(255) NOT NULL,
  start_time DATETIME(6) NOT NULL,
  end_time DATETIME(6) NOT NULL,
  planned_minutes INT NOT NULL,
  order_index INT NOT NULL,
  category VARCHAR(50) NULL,
  requires_focus BOOLEAN NOT NULL,
  score DOUBLE NULL,
  locked BOOLEAN NOT NULL DEFAULT FALSE,
  manual_override BOOLEAN NOT NULL DEFAULT FALSE,
  INDEX idx_schedule_items_run_order (schedule_run_id, order_index),
  CONSTRAINT fk_schedule_items_run
    FOREIGN KEY (schedule_run_id) REFERENCES schedule_runs(id)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS schedule_templates (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  name VARCHAR(120) NOT NULL,
  planning_mode VARCHAR(50) NOT NULL,
  start_hour INT NOT NULL,
  end_hour INT NOT NULL,
  buffer_minutes INT NOT NULL,
  include_fixed_events BOOLEAN NOT NULL,
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NULL,
  deleted_at DATETIME(6) NULL,
  INDEX idx_schedule_templates_user_active (user_id, deleted_at, name)
);

CREATE TABLE IF NOT EXISTS prediction_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  task_id INT NOT NULL,
  target_date DATE NOT NULL,
  model_name VARCHAR(120) NOT NULL,
  model_version VARCHAR(40) NOT NULL,
  predicted_minutes INT NOT NULL,
  estimated_minutes INT NOT NULL,
  actual_minutes INT NULL,
  actual_recorded_at DATETIME(6) NULL,
  created_at DATETIME(6) NOT NULL,
  INDEX idx_prediction_logs_user_date (user_id, target_date),
  INDEX idx_prediction_logs_unpaired (user_id, task_id, actual_minutes)
);
