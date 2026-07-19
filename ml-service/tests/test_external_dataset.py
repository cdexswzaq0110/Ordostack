"""Conversion of the external SiP dataset into the contract schema."""

import importlib.util
import sys
from pathlib import Path


def load_prepare_module():
    script_path = Path(__file__).resolve().parents[1] / "training" / "prepare_external_dataset.py"
    spec = importlib.util.spec_from_file_location("prepare_external_dataset_under_test", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load prepare_external_dataset module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RAW_HEADER = (
    "TaskNumber,Summary,Priority,RaisedByID,AssignedToID,AuthorisedByID,StatusCode,"
    "ProjectCode,ProjectBreakdownCode,Category,SubCategory,HoursEstimate,HoursActual,"
    "DeveloperID,DeveloperHoursActual,TaskPerformance,DeveloperPerformance"
)


def write_raw(tmp_path: Path, data_rows: list[str]) -> Path:
    raw_path = tmp_path / "Sip-task-info.csv"
    raw_path.write_text("\n".join([RAW_HEADER, *data_rows]) + "\n", encoding="utf-8")
    return raw_path


def test_priority_maps_from_ten_scale_to_contract_five_scale() -> None:
    prepare = load_prepare_module()
    assert [prepare.map_priority(str(p)) for p in range(1, 11)] == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
    assert prepare.map_priority("not-a-number") == 3


def test_conversion_filters_and_maps_to_contract_schema(tmp_path) -> None:
    prepare = load_prepare_module()
    raw_path = write_raw(
        tmp_path,
        [
            # kept: finished, 2h est / 3h actual, priority 4 -> 2
            '1,"A",4,1,1,1,"FINISHED","PC1","PBC1","Development","Enhancement",2,3,1,3,1,1',
            # dropped: not finished
            '2,"B",1,1,1,1,"CANCELLED","PC1","PBC1","Development","Enhancement",2,3,1,3,1,1',
            # dropped: actual above the 1440-minute contract bound (30h)
            '3,"C",1,1,1,1,"FINISHED","PC1","PBC1","Operational","Task",2,30,1,30,1,1',
            # kept: management category normalizes to lowercase
            '4,"D",10,1,1,1,"FINISHED","PC1","PBC1","Management","Meeting",1,0.5,1,0.5,1,1',
        ],
    )

    rows, summary = prepare.convert_rows(raw_path)

    assert summary["raw_rows"] == 4
    assert summary["converted_rows"] == 2
    assert summary["dropped"] == {"not_finished": 1, "missing_effort": 0, "out_of_bounds": 1}
    first, second = rows
    assert first == {
        "category": "development",
        "estimated_minutes": 120,
        "priority": 2,
        "difficulty": 3,
        "requires_focus": False,
        "actual_minutes": 180,
    }
    assert second["category"] == "management"
    assert second["priority"] == 5
    assert second["actual_minutes"] == 30


def test_converted_output_passes_the_data_contract(tmp_path) -> None:
    prepare = load_prepare_module()
    raw_path = write_raw(
        tmp_path,
        ['1,"A",1,1,1,1,"FINISHED","PC1","PBC1","Development","Enhancement",2,3,1,3,1,1'],
    )
    output_path = tmp_path / "out.csv"

    rows, _ = prepare.convert_rows(raw_path)
    prepare.write_contract_csv(rows, output_path)

    content = output_path.read_text(encoding="utf-8").splitlines()
    assert content[0] == "category,estimated_minutes,priority,difficulty,requires_focus,actual_minutes"
    assert content[1] == "development,120,1,3,false,180"
