import pytest
from rayforce import Table, Vector, Symbol, I16, I32, I64, U8, F64, B8, Date, Time, Timestamp, Column


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_desc(is_inplace):
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38], ray_type=I64),
        },
    )

    if is_inplace:
        result = table.xdesc(Column("age"))
    else:
        table.save("test_order_desc")
        result = Table.from_name("test_order_desc").xdesc(Column("age"))

    assert isinstance(result, Table)
    values = result.values()

    # Verify descending order: 41 > 38 > 34 > 29
    assert values[2][0].value == 41
    assert values[2][1].value == 38
    assert values[2][2].value == 34
    assert values[2][3].value == 29

    # Verify all ages are present (no data loss)
    ages = [values[2][i].value for i in range(4)]
    assert set(ages) == {29, 34, 38, 41}

    # Verify other columns are reordered correctly with age
    # Row with age=41 should have id="003", name="charlie"
    age_41_idx = ages.index(41)
    assert values[0][age_41_idx].value == "003"
    assert values[1][age_41_idx].value == "charlie"


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_asc(is_inplace):
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38], ray_type=I64),
        },
    )

    if is_inplace:
        result = table.xasc(Column("age"))
    else:
        table.save("test_order_asc")
        result = Table.from_name("test_order_asc").xasc(Column("age"))

    assert isinstance(result, Table)
    values = result.values()

    # Verify ascending order: 29 < 34 < 38 < 41
    assert values[2][0].value == 29  # First row should be lowest age
    assert values[2][1].value == 34
    assert values[2][2].value == 38
    assert values[2][3].value == 41  # Last row should be highest age

    # Verify all ages are present (no data loss)
    ages = [values[2][i].value for i in range(4)]
    assert set(ages) == {29, 34, 38, 41}

    # Verify other columns are reordered correctly with age
    # Row with age=29 should have id="001", name="alice"
    age_29_idx = ages.index(29)
    assert values[0][age_29_idx].value == "001"
    assert values[1][age_29_idx].value == "alice"


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_multiple_columns(is_inplace):
    """Test ordering by multiple columns."""
    table = Table.from_dict(
        {
            "dept": Vector(items=["eng", "eng", "marketing", "marketing"], ray_type=Symbol),
            "salary": Vector(items=[100000, 120000, 90000, 110000], ray_type=I64),
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
        },
    )

    if is_inplace:
        result = table.xasc(Column("dept"), Column("salary"))
    else:
        table.save("test_order_multi")
        result = Table.from_name("test_order_multi").xasc(Column("dept"), Column("salary"))

    assert isinstance(result, Table)
    values = result.values()

    # Verify ordering: first by dept (asc), then by salary (asc)
    # Expected order:
    # 1. eng, 100000 (alice)
    # 2. eng, 120000 (bob)
    # 3. marketing, 90000 (charlie)
    # 4. marketing, 110000 (dana)

    assert values[0][0].value == "eng"
    assert values[1][0].value == 100000
    assert values[2][0].value == "alice"

    assert values[0][1].value == "eng"
    assert values[1][1].value == 120000
    assert values[2][1].value == "bob"

    assert values[0][2].value == "marketing"
    assert values[1][2].value == 90000
    assert values[2][2].value == "charlie"

    assert values[0][3].value == "marketing"
    assert values[1][3].value == 110000
    assert values[2][3].value == "dana"


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_string_column(is_inplace):
    """Test ordering by string column."""
    table = Table.from_dict(
        {
            "id": Vector(items=["003", "001", "004", "002"], ray_type=Symbol),
            "name": Vector(items=["charlie", "alice", "dana", "bob"], ray_type=Symbol),
        },
    )

    if is_inplace:
        result = table.xasc(Column("name"))
    else:
        table.save("test_order_string")
        result = Table.from_name("test_order_string").xasc(Column("name"))

    assert isinstance(result, Table)
    values = result.values()

    # Verify alphabetical order: alice < bob < charlie < dana
    assert values[1][0].value == "alice"
    assert values[1][1].value == "bob"
    assert values[1][2].value == "charlie"
    assert values[1][3].value == "dana"

    # Verify ids are reordered correctly with names
    assert values[0][0].value == "001"  # alice's id
    assert values[0][1].value == "002"  # bob's id
    assert values[0][2].value == "003"  # charlie's id
    assert values[0][3].value == "004"  # dana's id


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_preserves_all_rows(is_inplace):
    """Test that ordering preserves all rows and columns."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "value": Vector(items=[3, 1, 2], ray_type=I64),
        },
    )

    if is_inplace:
        result = table.xasc(Column("value"))
    else:
        table.save("test_order_preserve")
        result = Table.from_name("test_order_preserve").xasc(Column("value"))

    assert isinstance(result, Table)

    # Verify table structure preserved
    columns = result.columns()
    assert len(columns) == 2
    assert "id" in columns
    assert "value" in columns

    # Verify all rows present
    values = result.values()
    assert len(values[0]) == 3  # Still 3 rows

    # Verify all values present (just reordered)
    all_values = [values[1][i].value for i in range(3)]
    assert set(all_values) == {1, 2, 3}


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_f64(is_inplace):
    """Test ordering by F64 column."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "price": Vector(items=[10.5, 20.0, 15.75, 5.25], ray_type=F64),
        },
    )

    if is_inplace:
        result = table.xasc(Column("price"))
    else:
        table.save("test_order_f64")
        result = Table.from_name("test_order_f64").xasc(Column("price"))

    assert isinstance(result, Table)
    values = result.values()

    # Verify ascending order: 5.25 < 10.5 < 15.75 < 20.0
    price_col = values[1]
    assert abs(price_col[0].value - 5.25) < 0.01
    assert abs(price_col[1].value - 10.5) < 0.01
    assert abs(price_col[2].value - 15.75) < 0.01
    assert abs(price_col[3].value - 20.0) < 0.01


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_date(is_inplace):
    """Test ordering by Date column."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "hire_date": Vector(
                items=[
                    Date(2022, 3, 10),
                    Date(2020, 1, 1),
                    Date(2023, 12, 31),
                    Date(2021, 6, 15),
                ],
                ray_type=Date,
            ),
        },
    )

    if is_inplace:
        result = table.xasc(Column("hire_date"))
    else:
        table.save("test_order_date")
        result = Table.from_name("test_order_date").xasc(Column("hire_date"))

    assert isinstance(result, Table)
    values = result.values()

    # Verify ascending order by date
    date_col = values[1]
    assert date_col[0].value == Date(2020, 1, 1).value
    assert date_col[1].value == Date(2021, 6, 15).value
    assert date_col[2].value == Date(2022, 3, 10).value
    assert date_col[3].value == Date(2023, 12, 31).value


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_timestamp(is_inplace):
    """Test ordering by Timestamp column."""
    from datetime import datetime

    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "created_at": Vector(
                items=[
                    Timestamp(datetime(2022, 3, 10, 9, 15, 0)),
                    Timestamp(datetime(2020, 1, 1, 10, 0, 0)),
                    Timestamp(datetime(2023, 12, 31, 23, 59, 59)),
                    Timestamp(datetime(2021, 6, 15, 14, 30, 0)),
                ],
                ray_type=Timestamp,
            ),
        },
    )

    if is_inplace:
        result = table.xasc(Column("created_at"))
    else:
        table.save("test_order_timestamp")
        result = Table.from_name("test_order_timestamp").xasc(Column("created_at"))

    assert isinstance(result, Table)
    values = result.values()

    # Verify ascending order by timestamp
    ts_col = values[1]
    assert ts_col[0].value == Timestamp(datetime(2020, 1, 1, 10, 0, 0)).value
    assert ts_col[1].value == Timestamp(datetime(2021, 6, 15, 14, 30, 0)).value
    assert ts_col[2].value == Timestamp(datetime(2022, 3, 10, 9, 15, 0)).value
    assert ts_col[3].value == Timestamp(datetime(2023, 12, 31, 23, 59, 59)).value


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_b8(is_inplace):
    """Test ordering by B8 (boolean) column."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "active": Vector(items=[True, False, True, False], ray_type=B8),
        },
    )

    if is_inplace:
        result = table.xasc(Column("active"))
    else:
        table.save("test_order_b8")
        result = Table.from_name("test_order_b8").xasc(Column("active"))

    assert isinstance(result, Table)
    values = result.values()

    # Verify ordering: False < True
    active_col = values[1]
    # First two should be False, last two should be True
    assert active_col[0].value is False
    assert active_col[1].value is False
    assert active_col[2].value is True
    assert active_col[3].value is True


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_i16(is_inplace):
    """Test ordering by I16 column."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "score": Vector(items=[300, 100, 400, 200], ray_type=I16),
        },
    )

    if is_inplace:
        result = table.xasc(Column("score"))
    else:
        table.save("test_order_i16")
        result = Table.from_name("test_order_i16").xasc(Column("score"))

    assert isinstance(result, Table)
    values = result.values()

    score_col = values[1]
    assert score_col[0].value == 100
    assert score_col[1].value == 200
    assert score_col[2].value == 300
    assert score_col[3].value == 400


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_i32(is_inplace):
    """Test ordering by I32 column."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "count": Vector(items=[3000, 1000, 4000, 2000], ray_type=I32),
        },
    )

    if is_inplace:
        result = table.xasc(Column("count"))
    else:
        table.save("test_order_i32")
        result = Table.from_name("test_order_i32").xasc(Column("count"))

    assert isinstance(result, Table)
    values = result.values()

    count_col = values[1]
    assert count_col[0].value == 1000
    assert count_col[1].value == 2000
    assert count_col[2].value == 3000
    assert count_col[3].value == 4000


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_u8(is_inplace):
    """Test ordering by U8 column."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "priority": Vector(items=[10, 1, 15, 5], ray_type=U8),
        },
    )

    if is_inplace:
        result = table.xasc(Column("priority"))
    else:
        table.save("test_order_u8")
        result = Table.from_name("test_order_u8").xasc(Column("priority"))

    assert isinstance(result, Table)
    values = result.values()

    priority_col = values[1]
    assert priority_col[0].value == 1
    assert priority_col[1].value == 5
    assert priority_col[2].value == 10
    assert priority_col[3].value == 15


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_time(is_inplace):
    """Test ordering by Time column."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "start_time": Vector(
                items=[
                    Time("14:30:00"),
                    Time("09:00:00"),
                    Time("23:59:59"),
                    Time("12:00:00"),
                ],
                ray_type=Time,
            ),
        },
    )

    if is_inplace:
        result = table.xasc(Column("start_time"))
    else:
        table.save("test_order_time")
        result = Table.from_name("test_order_time").xasc(Column("start_time"))

    assert isinstance(result, Table)
    values = result.values()

    time_col = values[1]
    assert time_col[0].value == Time("09:00:00").value
    assert time_col[1].value == Time("12:00:00").value
    assert time_col[2].value == Time("14:30:00").value
    assert time_col[3].value == Time("23:59:59").value
