import base64
from datetime import date, datetime
from typing import Any

import httpx
from fastapi import HTTPException, status

from app.config import load_runtime_config
from app.repositories.store import get_store
from app.schemas.schedules import (
    ScheduleGenerateRequest,
    ScheduleGenerateResponse,
    ScheduleDiffItem,
    ScheduleDiffResponse,
    ScheduleExportResponse,
    ScheduleHistoryDeleteResponse,
    ScheduleHistoryItem,
    ScheduleHistoryUpdate,
    ScheduleItemLockUpdate,
    ScheduleItemTimeUpdate,
)
from app.services import fixed_events as fixed_event_service
from app.services import predictions as prediction_service
from app.services import tasks as task_service

SCHEDULER_TIMEOUT_SECONDS = 8.0


def generate_schedule(payload: ScheduleGenerateRequest) -> ScheduleGenerateResponse:
    tasks = task_service.list_tasks(
        user_id=payload.user_id,
        target_date=payload.target_date,
    )
    fixed_events = fixed_event_service.list_fixed_events(
        user_id=payload.user_id,
        target_date=payload.target_date,
    )

    duration_predictions = prediction_service.predict_for_tasks(
        user_id=payload.user_id,
        target_date=payload.target_date,
        tasks=tasks,
    )
    predicted_minutes_by_task = {
        prediction.task_id: prediction.predicted_minutes
        for prediction in duration_predictions.predictions
    }

    scheduler_payload: dict[str, Any] = payload.model_dump(mode="json")
    scheduler_payload["tasks"] = [
        {
            **task.model_dump(mode="json"),
            "predicted_minutes": predicted_minutes_by_task.get(task.id),
        }
        for task in tasks
    ]
    scheduler_payload["fixed_events"] = [event.model_dump(mode="json") for event in fixed_events]
    scheduler_payload["locked_items"] = list_locked_schedule_items(
        user_id=payload.user_id,
        target_date=payload.target_date,
    )

    scheduler_url = load_runtime_config().scheduler_service_url
    try:
        response = httpx.post(
            f"{scheduler_url}/schedule/generate",
            json=scheduler_payload,
            timeout=SCHEDULER_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=error.response.status_code,
            detail=extract_scheduler_error(error.response),
        ) from error
    except httpx.RequestError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="scheduler-service is unavailable",
        ) from error

    schedule_response = response.json()
    get_store().save_generated_schedule(
        user_id=payload.user_id,
        target_date=payload.target_date,
        request_payload=payload.model_dump(mode="json"),
        schedule=schedule_response,
    )
    return schedule_response


def get_latest_schedule(user_id: int, target_date: date) -> ScheduleGenerateResponse:
    schedule = get_store().get_latest_generated_schedule(user_id=user_id, target_date=target_date)
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generated schedule not found")
    return schedule


def list_schedule_history(user_id: int, target_date: date, limit: int = 5) -> list[ScheduleHistoryItem]:
    schedules = get_store().list_generated_schedules(user_id=user_id, target_date=target_date, limit=limit)
    return [ScheduleHistoryItem.model_validate(schedule) for schedule in schedules]


def update_schedule_history_title(
    user_id: int,
    schedule_run_id: int,
    payload: ScheduleHistoryUpdate,
) -> ScheduleHistoryItem:
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Title is required")

    schedule = get_store().update_generated_schedule_title(
        user_id=user_id,
        schedule_run_id=schedule_run_id,
        title=title,
    )
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generated schedule not found")
    return ScheduleHistoryItem.model_validate(schedule)


def update_schedule_item_lock(
    user_id: int,
    schedule_run_id: int,
    item_key: str,
    payload: ScheduleItemLockUpdate,
) -> ScheduleHistoryItem:
    schedule = get_store().update_generated_schedule_item(
        user_id=user_id,
        schedule_run_id=schedule_run_id,
        item_key=item_key,
        payload={"locked": payload.locked},
    )
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule item not found")
    return ScheduleHistoryItem.model_validate(schedule)


def update_schedule_item_time(
    user_id: int,
    schedule_run_id: int,
    item_key: str,
    payload: ScheduleItemTimeUpdate,
) -> ScheduleHistoryItem:
    schedule_run = get_store().get_generated_schedule_history_item(user_id=user_id, schedule_run_id=schedule_run_id)
    if schedule_run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generated schedule not found")

    current_item = find_schedule_item(schedule_run["schedule"].get("items", []), item_key)
    if current_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule item not found")

    fixed_event_items = [
        {
            "type": "fixed_event",
            "fixed_event_id": event.id,
            "title": event.title,
            "start_time": event.start_time,
            "end_time": event.end_time,
        }
        for event in fixed_event_service.list_fixed_events(
            user_id=user_id,
            target_date=date.fromisoformat(str(schedule_run["schedule"].get("schedule_date"))),
        )
    ]
    validate_fixed_event_conflicts(
        items=[*schedule_run["schedule"].get("items", []), *fixed_event_items],
        item_key=item_key,
        next_start_time=payload.start_time,
        next_end_time=payload.end_time,
    )

    schedule = get_store().update_generated_schedule_item(
        user_id=user_id,
        schedule_run_id=schedule_run_id,
        item_key=item_key,
        payload={
            "start_time": payload.start_time.isoformat(),
            "end_time": payload.end_time.isoformat(),
            "planned_minutes": minutes_between(payload.start_time, payload.end_time),
            "locked": True,
            "manual_override": True,
        },
    )
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule item not found")
    return ScheduleHistoryItem.model_validate(schedule)


def delete_schedule_history_item(user_id: int, schedule_run_id: int) -> ScheduleHistoryDeleteResponse:
    deleted = get_store().soft_delete_generated_schedule(user_id=user_id, schedule_run_id=schedule_run_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generated schedule not found")
    return ScheduleHistoryDeleteResponse(deleted=True)


def get_schedule_history_diff(user_id: int, compare_run_id: int, base_run_id: int) -> ScheduleDiffResponse:
    base_run = get_store().get_generated_schedule_history_item(user_id=user_id, schedule_run_id=base_run_id)
    compare_run = get_store().get_generated_schedule_history_item(user_id=user_id, schedule_run_id=compare_run_id)

    if base_run is None or compare_run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generated schedule not found")

    return build_schedule_diff(base_run=base_run, compare_run=compare_run)


def export_schedule_history_item(user_id: int, schedule_run_id: int, export_format: str) -> ScheduleExportResponse:
    schedule_run = get_store().get_generated_schedule_history_item(user_id=user_id, schedule_run_id=schedule_run_id)
    if schedule_run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generated schedule not found")

    if export_format == "csv":
        return ScheduleExportResponse(
            filename=f"ordostack-schedule-{schedule_run_id}.csv",
            format="csv",
            content_type="text/csv",
            content=build_schedule_csv(schedule_run),
        )
    if export_format == "pdf":
        return ScheduleExportResponse(
            filename=f"ordostack-schedule-{schedule_run_id}.pdf",
            format="pdf",
            content_type="application/pdf",
            content=base64.b64encode(build_schedule_pdf(schedule_run)).decode("ascii"),
            encoding="base64",
        )

    return ScheduleExportResponse(
        filename=f"ordostack-schedule-{schedule_run_id}.md",
        format="markdown",
        content_type="text/markdown",
        content=build_schedule_markdown(schedule_run),
    )


def build_schedule_diff(base_run: dict[str, Any], compare_run: dict[str, Any]) -> ScheduleDiffResponse:
    base_items = {schedule_item_key(item): item for item in base_run["schedule"].get("items", [])}
    compare_items = {schedule_item_key(item): item for item in compare_run["schedule"].get("items", [])}
    item_keys = sorted(base_items.keys() | compare_items.keys())
    changes: list[ScheduleDiffItem] = []
    unchanged_count = 0

    for item_key in item_keys:
        base_item = base_items.get(item_key)
        compare_item = compare_items.get(item_key)

        if base_item is None and compare_item is not None:
            changes.append(build_diff_item(item_key=item_key, change_type="added", base_item=None, compare_item=compare_item))
            continue

        if base_item is not None and compare_item is None:
            changes.append(build_diff_item(item_key=item_key, change_type="removed", base_item=base_item, compare_item=None))
            continue

        if base_item is None or compare_item is None:
            continue

        if schedule_item_changed(base_item, compare_item):
            changes.append(
                build_diff_item(item_key=item_key, change_type="changed", base_item=base_item, compare_item=compare_item),
            )
        else:
            unchanged_count += 1

    total_delta_minutes = schedule_minutes(compare_items.values()) - schedule_minutes(base_items.values())
    return ScheduleDiffResponse(
        base_run_id=base_run["id"],
        compare_run_id=compare_run["id"],
        added_count=sum(1 for change in changes if change.change_type == "added"),
        removed_count=sum(1 for change in changes if change.change_type == "removed"),
        changed_count=sum(1 for change in changes if change.change_type == "changed"),
        unchanged_count=unchanged_count,
        total_delta_minutes=total_delta_minutes,
        changes=changes,
    )


def schedule_item_key(item: dict[str, Any]) -> str:
    if item.get("type") == "task" and item.get("task_id") is not None:
        return f"task:{item['task_id']}"
    if item.get("type") == "fixed_event" and item.get("fixed_event_id") is not None:
        return f"fixed_event:{item['fixed_event_id']}"
    return f"{item.get('type', 'item')}:{item.get('title', '')}:{item.get('order_index', 0)}"


def list_locked_schedule_items(user_id: int, target_date: date) -> list[dict[str, Any]]:
    latest_schedule = get_store().get_latest_generated_schedule(user_id=user_id, target_date=target_date)
    if latest_schedule is None:
        return []

    return [
        item
        for item in latest_schedule.get("items", [])
        if item.get("locked") is True
    ]


def find_schedule_item(items: list[dict[str, Any]], item_key: str) -> dict[str, Any] | None:
    for item in items:
        if schedule_item_key(item) == item_key:
            return item
    return None


def validate_fixed_event_conflicts(
    items: list[dict[str, Any]],
    item_key: str,
    next_start_time: datetime,
    next_end_time: datetime,
) -> None:
    for item in items:
        if schedule_item_key(item) == item_key or item.get("type") != "fixed_event":
            continue

        fixed_start = parse_datetime(item.get("start_time"))
        fixed_end = parse_datetime(item.get("end_time"))
        if ranges_overlap(next_start_time, next_end_time, fixed_start, fixed_end):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Schedule item conflicts with fixed event: {item.get('title', 'Untitled')}",
            )


def ranges_overlap(
    first_start: datetime,
    first_end: datetime,
    second_start: datetime,
    second_end: datetime,
) -> bool:
    return first_start.replace(tzinfo=None) < second_end.replace(tzinfo=None) and second_start.replace(
        tzinfo=None,
    ) < first_end.replace(tzinfo=None)


def parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))


def minutes_between(start_time: datetime, end_time: datetime) -> int:
    return max(0, int((end_time.replace(tzinfo=None) - start_time.replace(tzinfo=None)).total_seconds() // 60))


def schedule_item_changed(base_item: dict[str, Any], compare_item: dict[str, Any]) -> bool:
    fields = ("title", "start_time", "end_time", "planned_minutes", "order_index")
    return any(base_item.get(field) != compare_item.get(field) for field in fields)


def build_diff_item(
    item_key: str,
    change_type: str,
    base_item: dict[str, Any] | None,
    compare_item: dict[str, Any] | None,
) -> ScheduleDiffItem:
    item = compare_item or base_item or {}
    return ScheduleDiffItem(
        item_key=item_key,
        change_type=change_type,
        title=str(item.get("title", "Untitled")),
        previous_start_time=base_item.get("start_time") if base_item else None,
        next_start_time=compare_item.get("start_time") if compare_item else None,
        previous_planned_minutes=base_item.get("planned_minutes") if base_item else None,
        next_planned_minutes=compare_item.get("planned_minutes") if compare_item else None,
    )


def schedule_minutes(items: Any) -> int:
    return sum(int(item.get("planned_minutes", 0)) for item in items if item.get("type") == "task")


def build_schedule_markdown(schedule_run: dict[str, Any]) -> str:
    schedule = schedule_run["schedule"]
    lines = [
        f"# {schedule_run['title']}",
        "",
        f"- Date: {schedule.get('schedule_date')}",
        f"- Planning mode: {schedule.get('planning_mode')}",
        f"- Generated at: {schedule_run['created_at']}",
        "",
        "| Start | End | Type | Title | Minutes |",
        "| --- | --- | --- | --- | ---: |",
    ]
    for item in schedule.get("items", []):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(item.get("start_time", "")),
                    str(item.get("end_time", "")),
                    str(item.get("type", "")),
                    escape_markdown_cell(str(item.get("title", ""))),
                    str(item.get("planned_minutes", "")),
                ],
            )
            + " |",
        )
    return "\n".join(lines) + "\n"


def build_schedule_csv(schedule_run: dict[str, Any]) -> str:
    rows = [["start_time", "end_time", "type", "title", "planned_minutes", "category"]]
    for item in schedule_run["schedule"].get("items", []):
        rows.append(
            [
                str(item.get("start_time", "")),
                str(item.get("end_time", "")),
                str(item.get("type", "")),
                str(item.get("title", "")),
                str(item.get("planned_minutes", "")),
                str(item.get("category", "")),
            ],
        )
    return "\n".join(",".join(csv_escape(value) for value in row) for row in rows) + "\n"


def build_schedule_pdf(schedule_run: dict[str, Any]) -> bytes:
    schedule = schedule_run["schedule"]
    text_lines = [
        schedule_run["title"],
        f"Date: {schedule.get('schedule_date')}",
        f"Planning mode: {schedule.get('planning_mode')}",
        "",
    ]
    for item in schedule.get("items", []):
        text_lines.append(
            f"{item.get('start_time', '')} - {item.get('end_time', '')} | "
            f"{item.get('type', '')} | {item.get('title', '')} | {item.get('planned_minutes', '')} min",
        )

    stream_lines = ["BT", "/F1 11 Tf", "50 780 Td"]
    for index, line in enumerate(text_lines[:42]):
        if index > 0:
            stream_lines.append("0 -16 Td")
        stream_lines.append(f"({pdf_escape(line)}) Tj")
    stream_lines.append("ET")
    content_stream = "\n".join(stream_lines).encode("latin-1", errors="replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content_stream)).encode("ascii") + b" >>\nstream\n" + content_stream + b"\nendstream",
    ]
    return assemble_pdf(objects)


def assemble_pdf(objects: list[bytes]) -> bytes:
    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, payload in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode("ascii"))
        output.extend(payload)
        output.extend(b"\nendobj\n")

    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii"),
    )
    return bytes(output)


def pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def csv_escape(value: str) -> str:
    if any(character in value for character in [",", "\"", "\n", "\r"]):
        return '"' + value.replace('"', '""') + '"'
    return value


def escape_markdown_cell(value: str) -> str:
    return value.replace("|", "\\|")


def extract_scheduler_error(response: httpx.Response) -> Any:
    try:
        payload = response.json()
    except ValueError:
        return response.text

    return payload.get("detail", payload)
