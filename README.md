# OrdoStack Draft Edition

> Draft Edition of an AI-powered daily planning system.

OrdoStack is planned as an algorithm-driven personal planning system that helps users convert messy learning tasks into a focused daily plan.

This repository is currently the **Draft Edition**. The current implementation is a static mobile-first web MVP built with HTML, CSS, and JavaScript. It is not yet the full backend, mobile app, machine learning, ClearML, Docker, or AWS version described in the long-term roadmap.

---

## Current Draft Scope

The current app supports:

- Create learning goals.
- Add tasks under each goal.
- Set estimated minutes and priority for each task.
- Mark tasks as complete or restore them.
- Delete goals and tasks.
- Generate a daily recommended task list.
- View weekly progress by goal.
- Store data locally in the browser.
- Run without a backend, database, account system, API key, or package installation.

Current entry point:

```text
app/index.html
```

---

## Long-Term Product Vision

The planned full version of OrdoStack is not just a to-do list app. It is intended to become a scheduling and productivity system that can optimize daily plans based on:

- Task priority
- Deadline
- Available time
- Task difficulty
- Focus requirement
- Historical completion behavior
- Predicted task duration
- Fixed events such as classes, meetings, meals, or sleep time

Planned user capabilities:

- Create daily tasks.
- Add fixed events.
- Generate an optimized daily schedule.
- Track task start time, completion time, and actual duration.
- Compare estimated time and actual time.
- Predict actual task duration with machine learning.
- Predict daily completion rate or focus score with deep learning.
- Visualize productivity data through a dashboard.
- Manage ML/DL experiments with ClearML.
- Run services with Docker Compose.
- Deploy to AWS EC2.

---

## Current Repository Structure

```text
ordostack-draft-edition/
├── README.md
├── .gitignore
├── app/
│   ├── index.html
│   ├── styles.css
│   ├── core.js
│   ├── browser.js
│   ├── manifest.webmanifest
│   └── service-worker.js
├── docs/
│   ├── product-spec.md
│   ├── release-checklist.md
│   └── decisions.md
├── tests/
│   └── core.test.js
├── memory-bank/
├── codex-workflows/
├── AGENTS.md
├── COMMAND_TEMPLATE.md
└── LICENSE
```

---

## How to Run the Draft App

Open the app directly in a browser:

```text
app/index.html
```

On Windows, the local file URL may look like:

```text
file:///C:/Users/student/Desktop/OrdoStack_Draft_Edition/app/index.html
```

No server is required for the current draft.

---

## How to Use

1. Create a learning goal.
2. Add tasks under the goal.
3. Set estimated minutes and priority.
4. Review the recommended daily tasks.
5. Mark tasks complete after finishing them.
6. Check weekly progress.

---

## Running Tests

If Node.js is available:

```bash
node tests/core.test.js
```

Note: in the current Codex desktop environment, the system `node.exe` may be blocked by WindowsApps permissions. Core logic has been verified through the Node REPL MCP runtime.

---

## Planned Full System Architecture

The future full-stack version is planned as:

```text
React Native Mobile App
        ↓
FastAPI Backend API
        ↓
MySQL Database
        ↓
Scheduler Service
        ↓
ML Service / DL Service
        ↓
ClearML MLOps
        ↓
AWS EC2 Deployment
```

This architecture is a roadmap target. It is **not implemented in the current draft**.

---

## Planned Tech Stack

### Mobile

- React Native
- Expo
- TypeScript
- Axios
- React Navigation

### Frontend Dashboard

- React
- Vite
- TypeScript
- Chart.js or Recharts
- Tailwind CSS

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- MySQL

### Scheduling Algorithms

- Priority score calculation
- Priority Queue scheduling
- Greedy scheduling
- 0/1 Knapsack dynamic programming
- Weighted Interval Scheduling
- Topological Sort for task dependencies
- Rescheduling algorithm for unfinished tasks

### Machine Learning

Planned ML module: predict actual task duration.

Possible models:

- Linear Regression baseline
- Random Forest Regressor
- XGBoost / LightGBM optional

Metrics:

- MAE
- RMSE
- Prediction error trend

### Deep Learning

Planned DL module: predict daily completion rate or focus score.

Possible models:

- MLP baseline
- LSTM optional
- GRU optional

Example planned output:

```json
{
  "focus_score": 0.78,
  "predicted_completion_rate": 0.72,
  "recommended_workload": "medium"
}
```

### MLOps

Planned ClearML usage:

- Experiment tracking
- Hyperparameter logging
- Metric tracking
- Model artifact management
- Dataset version tracking
- Training task management
- Model version management
- ClearML Agent workflow

---

## Planned API Endpoints

These endpoints are planned for the future backend version. They do not exist in the current static draft.

### Health Check

```text
GET /api/health
```

### Tasks

```text
POST   /api/tasks
GET    /api/tasks
PATCH  /api/tasks/{task_id}
DELETE /api/tasks/{task_id}
```

### Fixed Events

```text
POST /api/fixed-events
GET  /api/fixed-events
```

### Schedule

```text
POST /api/schedules/generate
GET  /api/schedules/today
POST /api/schedules/{schedule_id}/reschedule
```

### Task Execution

```text
POST /api/tasks/{task_id}/start
POST /api/tasks/{task_id}/pause
POST /api/tasks/{task_id}/complete
POST /api/tasks/{task_id}/skip
```

### Analytics

```text
GET /api/analytics/daily
GET /api/analytics/weekly
GET /api/analytics/model
```

### ML Prediction

```text
POST /api/ml/predict-duration
POST /api/dl/predict-completion-rate
```

---

## Planned Development Roadmap

### Phase 1: Draft MVP

- Static web prototype
- Goal and task management
- Priority and estimated minutes
- Daily recommendation list
- Weekly progress summary

### Phase 2: Project Foundation

- Full repository structure
- Backend health check
- Scheduler service health check
- Database schema draft
- Docker Compose skeleton

### Phase 3: Task Management Backend

- Tasks CRUD
- Fixed events CRUD
- Task execution logs
- MySQL persistence
- API validation

### Phase 4: Scheduling Algorithms

- Priority score
- Priority Queue
- Greedy scheduling
- Knapsack DP
- Fixed event conflict detection
- Topological Sort

### Phase 5: ML / DL

- Seed dataset
- Duration prediction model
- Completion rate prediction model
- ClearML tracking
- Model artifact logging

### Phase 6: Dashboard and Deployment

- Analytics dashboard
- GitHub Actions CI
- AWS EC2 deployment
- Docker Compose production setup

---

## Privacy and Secrets

The current draft does not use:

- External APIs
- API keys
- Passwords
- Cloud storage
- Authentication tokens
- Server-side databases

User data is stored locally in the browser through `localStorage`.

The `.gitignore` file excludes common private and local-only files, including:

- `.env`
- `.env.*`
- key files
- token files
- credential files
- logs
- cache folders
- `node_modules`
- local Codex/codegraph state

Do not commit real API keys, tokens, passwords, credentials, or private user data.

---

## Future Work

- Google Calendar integration
- Push notifications
- Authentication with JWT
- Multi-user support
- ClearML Serving
- AWS ECS + RDS + ECR
- Offline mobile mode
- Reinforcement learning based scheduling
- Habit recommendation system

---

## License

This project is planned for educational and portfolio purposes.

License: MIT
