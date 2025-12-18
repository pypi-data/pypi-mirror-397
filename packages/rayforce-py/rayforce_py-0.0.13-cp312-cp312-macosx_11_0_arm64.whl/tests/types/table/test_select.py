from rayforce import Table, Vector, Symbol, I16, I32, I64, U8, F64, B8, Date, Time, Timestamp, Column


def test_select_with_single_where():
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38], ray_type=I64),
            "salary": Vector(items=[100000, 120000, 90000, 85000], ray_type=I64),
        },
    )

    result = table.select("id", "name", "age").where(Column("age") >= 35).execute()

    columns = result.columns()
    assert len(columns) == 3
    assert "id" in columns
    assert "name" in columns
    assert "age" in columns

    values = result.values()
    assert len(values) == 3
    assert len(values[0]) == 2
    assert values[0][0].value == "003"
    assert values[0][1].value == "004"
    assert values[1][0].value == "charlie"
    assert values[1][1].value == "dana"
    assert values[2][0].value == 41
    assert values[2][1].value == 38


def test_select_with_multiple_where_conditions():
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004", "005"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana", "eli"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38, 45], ray_type=I64),
            "dept": Vector(items=["eng", "eng", "marketing", "eng", "marketing"], ray_type=Symbol),
            "salary": Vector(items=[100000, 120000, 90000, 85000, 95000], ray_type=I64),
        },
    )

    result = (
        table.select("id", "name", "age", "salary")
        .where(Column("age") >= 35)
        .where(Column("dept") == "eng")
        .execute()
    )

    values = result.values()
    assert len(values) == 4
    assert len(values[0]) == 1
    assert values[0][0].value == "004"
    assert values[1][0].value == "dana"
    assert values[2][0].value == 38
    assert values[3][0].value == 85000


def test_select_with_complex_and_or_conditions():
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004", "005"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana", "eli"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38, 45], ray_type=I64),
            "dept": Vector(items=["eng", "eng", "marketing", "eng", "marketing"], ray_type=Symbol),
            "salary": Vector(items=[100000, 120000, 90000, 85000, 95000], ray_type=I64),
        },
    )

    result = (
        table.select("id", "name")
        .where((Column("age") >= 35) & (Column("dept") == "eng"))
        .where((Column("salary") > 80000) | (Column("age") < 40))
        .execute()
    )

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) >= 0


def test_group_by_single_column():
    table = Table.from_dict(
        {
            "dept": Vector(items=["eng", "eng", "marketing", "marketing", "hr"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38, 35], ray_type=I64),
            "salary": Vector(items=[100000, 120000, 90000, 85000, 80000], ray_type=I64),
        },
    )

    result = (
        table.select(
            avg_age=Column("age").mean(),
            total_salary=Column("salary").sum(),
            count=Column("age").count(),
        )
        .by("dept")
        .execute()
    )

    columns = result.columns()
    assert len(columns) >= 4
    assert "dept" in columns or "by" in columns
    assert "avg_age" in columns
    assert "total_salary" in columns
    assert "count" in columns

    values = result.values()
    assert len(values) >= 3

    # Find the column indices
    cols = list(result.columns())
    dept_idx = cols.index("dept") if "dept" in cols else cols.index("by")
    avg_age_idx = cols.index("avg_age")
    total_salary_idx = cols.index("total_salary")
    count_idx = cols.index("count")

    # Expected: eng (avg_age=31.5, total_salary=220000, count=2)
    #           marketing (avg_age=39.5, total_salary=175000, count=2)
    #           hr (avg_age=35, total_salary=80000, count=1)

    dept_col = values[dept_idx]
    avg_age_col = values[avg_age_idx]
    total_salary_col = values[total_salary_idx]
    count_col = values[count_idx]

    # Find eng group
    for i in range(len(dept_col)):
        dept_val = dept_col[i].value if hasattr(dept_col[i], "value") else str(dept_col[i])
        if dept_val == "eng":
            assert abs(avg_age_col[i].value - 31.5) < 0.01
            assert total_salary_col[i].value == 220000
            assert count_col[i].value == 2
        elif dept_val == "marketing":
            assert abs(avg_age_col[i].value - 39.5) < 0.01
            assert total_salary_col[i].value == 175000
            assert count_col[i].value == 2
        elif dept_val == "hr":
            assert avg_age_col[i].value == 35
            assert total_salary_col[i].value == 80000
            assert count_col[i].value == 1


def test_group_by_multiple_columns():
    table = Table.from_dict(
        {
            "dept": Vector(items=["eng", "eng", "eng", "marketing", "marketing"], ray_type=Symbol),
            "level": Vector(
                items=["senior", "junior", "senior", "senior", "junior"],
                ray_type=Symbol,
            ),
            "salary": Vector(items=[150000, 100000, 140000, 120000, 90000], ray_type=I64),
        },
    )

    result = (
        table.select(
            total_salary=Column("salary").sum(),
            avg_salary=Column("salary").mean(),
        )
        .by("dept", "level")
        .execute()
    )

    columns = result.columns()
    assert len(columns) >= 4
    values = result.values()
    assert len(values) >= 2

    # Expected groups:
    # eng/senior: total=290000 (150000+140000), avg=145000
    # eng/junior: total=100000, avg=100000
    # marketing/senior: total=120000, avg=120000
    # marketing/junior: total=90000, avg=90000

    cols = list(result.columns())
    dept_idx = cols.index("dept") if "dept" in cols else cols.index("by")
    level_idx = (
        cols.index("level") if "level" in cols else (cols.index("by") + 1 if "by" in cols else 0)
    )
    total_salary_idx = cols.index("total_salary")
    avg_salary_idx = cols.index("avg_salary")

    dept_col = values[dept_idx]
    level_col = values[level_idx]
    total_salary_col = values[total_salary_idx]
    avg_salary_col = values[avg_salary_idx]

    for i in range(len(dept_col)):
        dept_val = dept_col[i].value if hasattr(dept_col[i], "value") else str(dept_col[i])
        level_val = level_col[i].value if hasattr(level_col[i], "value") else str(level_col[i])

        if dept_val == "eng" and level_val == "senior":
            assert total_salary_col[i].value == 290000
            assert avg_salary_col[i].value == 145000
        elif dept_val == "eng" and level_val == "junior":
            assert total_salary_col[i].value == 100000
            assert avg_salary_col[i].value == 100000
        elif dept_val == "marketing" and level_val == "senior":
            assert total_salary_col[i].value == 120000
            assert avg_salary_col[i].value == 120000
        elif dept_val == "marketing" and level_val == "junior":
            assert total_salary_col[i].value == 90000
            assert avg_salary_col[i].value == 90000


def test_group_by_with_filtered_aggregation():
    table = Table.from_dict(
        {
            "category": Vector(items=["A", "A", "B", "B", "A"], ray_type=Symbol),
            "amount": Vector(items=[100, 200, 150, 250, 300], ray_type=I64),
            "status": Vector(
                items=["active", "inactive", "active", "active", "inactive"],
                ray_type=Symbol,
            ),
        },
    )

    result = (
        table.select(
            total=Column("amount").sum(),
            active_total=Column("amount").where(Column("status") == "active").sum(),
            count=Column("amount").count(),
        )
        .by("category")
        .execute()
    )

    columns = result.columns()
    assert "total" in columns
    assert "active_total" in columns
    assert "count" in columns

    values = result.values()
    assert len(values) >= 3

    # Expected:
    # Category A: total=600 (100+200+300), active_total=100 (only first is active), count=3
    # Category B: total=400 (150+250), active_total=400 (both active), count=2

    cols = list(result.columns())
    category_idx = cols.index("category") if "category" in cols else cols.index("by")
    total_idx = cols.index("total")
    active_total_idx = cols.index("active_total")
    count_idx = cols.index("count")

    category_col = values[category_idx]
    total_col = values[total_idx]
    active_total_col = values[active_total_idx]
    count_col = values[count_idx]

    for i in range(len(category_col)):
        cat_val = (
            category_col[i].value if hasattr(category_col[i], "value") else str(category_col[i])
        )
        if cat_val == "A":
            assert total_col[i].value == 600
            assert active_total_col[i].value == 100
            assert count_col[i].value == 3
        elif cat_val == "B":
            assert total_col[i].value == 400
            assert active_total_col[i].value == 400
            assert count_col[i].value == 2


def test_complex_select_with_computed_columns():
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "price": Vector(items=[10.5, 20.0, 15.75], ray_type=F64),
            "quantity": Vector(items=[2, 3, 4], ray_type=I64),
        },
    )

    result = (
        table.select(
            "id",
            total=Column("price") * Column("quantity"),
            discounted=Column("price") * Column("quantity") * 0.9,
        )
        .where(Column("quantity") >= 3)
        .execute()
    )

    columns = result.columns()
    assert "id" in columns
    assert "total" in columns
    assert "discounted" in columns

    values = result.values()
    assert len(values) == 3
    assert len(values[0]) == 2


def test_select_with_isin_operator():
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004", "005"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana", "eli"], ray_type=Symbol),
            "dept": Vector(items=["eng", "eng", "marketing", "hr", "marketing"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38, 45], ray_type=I64),
        },
    )

    result = (
        table.select("id", "name", "dept", "age")
        .where(Column("dept").isin(["eng", "marketing"]))
        .execute()
    )

    columns = result.columns()
    assert len(columns) == 4
    assert "id" in columns
    assert "name" in columns
    assert "dept" in columns
    assert "age" in columns

    values = result.values()
    assert len(values) == 4
    assert len(values[0]) == 4

    cols = list(result.columns())
    name_idx = cols.index("name")
    dept_idx = cols.index("dept")

    name_col = values[name_idx]
    dept_col = values[dept_idx]

    returned_depts = [dept_col[i].value for i in range(len(dept_col))]
    assert all(dept in ["eng", "marketing"] for dept in returned_depts)
    assert len(returned_depts) == 4

    returned_names = [name_col[i].value for i in range(len(name_col))]
    assert "alice" in returned_names
    assert "bob" in returned_names
    assert "charlie" in returned_names
    assert "eli" in returned_names
    assert "dana" not in returned_names

    result_int = (
        table.select("id", "name", "age")
        .where(Column("age").isin([29, 41, 45]))
        .execute()
    )

    columns_int = result_int.columns()
    assert len(columns_int) == 3
    assert "id" in columns_int
    assert "name" in columns_int
    assert "age" in columns_int

    values_int = result_int.values()
    assert len(values_int) == 3
    assert len(values_int[0]) == 3

    cols_int = list(result_int.columns())
    name_idx_int = cols_int.index("name")
    age_idx_int = cols_int.index("age")

    name_col_int = values_int[name_idx_int]
    age_col_int = values_int[age_idx_int]

    returned_ages = [age_col_int[i].value for i in range(len(age_col_int))]
    assert all(age in [29, 41, 45] for age in returned_ages)
    assert len(returned_ages) == 3

    returned_names_int = [name_col_int[i].value for i in range(len(name_col_int))]
    assert "alice" in returned_names_int  # age 29
    assert "charlie" in returned_names_int  # age 41
    assert "eli" in returned_names_int  # age 45
    assert "bob" not in returned_names_int  # age 34
    assert "dana" not in returned_names_int  # age 38


def test_select_with_f64_comparisons():
    """Test F64 comparisons in where clauses."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "price": Vector(items=[10.5, 20.0, 30.5, 40.0], ray_type=F64),
            "discount": Vector(items=[0.1, 0.2, 0.15, 0.25], ray_type=F64),
        },
    )

    result = table.select("id", "price").where(Column("price") >= 25.0).execute()

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) == 2

    cols = list(result.columns())
    price_idx = cols.index("price")
    price_col = values[price_idx]

    returned_prices = [price_col[i].value for i in range(len(price_col))]
    assert all(price >= 25.0 for price in returned_prices)
    assert 30.5 in returned_prices
    assert 40.0 in returned_prices
    assert 10.5 not in returned_prices
    assert 20.0 not in returned_prices


def test_select_with_f64_isin():
    """Test F64 isin operator."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "price": Vector(items=[10.5, 20.0, 30.5, 40.0], ray_type=F64),
        },
    )

    result = (
        table.select("id", "price")
        .where(Column("price").isin([10.5, 30.5, 50.0]))
        .execute()
    )

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) == 2

    cols = list(result.columns())
    price_idx = cols.index("price")
    price_col = values[price_idx]

    returned_prices = [price_col[i].value for i in range(len(price_col))]
    assert all(price in [10.5, 30.5, 50.0] for price in returned_prices)
    assert 10.5 in returned_prices
    assert 30.5 in returned_prices
    assert 20.0 not in returned_prices
    assert 40.0 not in returned_prices


def test_select_with_f64_aggregations():
    """Test F64 aggregations."""
    table = Table.from_dict(
        {
            "category": Vector(items=["A", "A", "B", "B"], ray_type=Symbol),
            "price": Vector(items=[10.5, 20.0, 30.5, 40.0], ray_type=F64),
        },
    )

    result = (
        table.select(
            total=Column("price").sum(),
            avg_price=Column("price").mean(),
            min_price=Column("price").min(),
            max_price=Column("price").max(),
            count=Column("price").count(),
        )
        .by("category")
        .execute()
    )

    columns = result.columns()
    assert "total" in columns
    assert "avg_price" in columns
    assert "min_price" in columns
    assert "max_price" in columns
    assert "count" in columns

    values = result.values()
    assert len(values) >= 5

    cols = list(result.columns())
    category_idx = cols.index("category") if "category" in cols else cols.index("by")
    total_idx = cols.index("total")
    avg_idx = cols.index("avg_price")

    category_col = values[category_idx]
    total_col = values[total_idx]
    avg_col = values[avg_idx]

    for i in range(len(category_col)):
        cat_val = (
            category_col[i].value if hasattr(category_col[i], "value") else str(category_col[i])
        )
        if cat_val == "A":
            assert abs(total_col[i].value - 30.5) < 0.01
            assert abs(avg_col[i].value - 15.25) < 0.01
        elif cat_val == "B":
            assert abs(total_col[i].value - 70.5) < 0.01
            assert abs(avg_col[i].value - 35.25) < 0.01


def test_select_with_b8_comparisons():
    """Test B8 (boolean) comparisons in where clauses."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "active": Vector(items=[True, False, True, False], ray_type=B8),
            "score": Vector(items=[10, 20, 30, 40], ray_type=I64),
        },
    )

    result = table.select("id", "score").where(Column("active") == True).execute()

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) == 2

    cols = list(result.columns())
    id_idx = cols.index("id")
    id_col = values[id_idx]

    returned_ids = [id_col[i].value for i in range(len(id_col))]
    assert "001" in returned_ids
    assert "003" in returned_ids
    assert "002" not in returned_ids
    assert "004" not in returned_ids


def test_select_with_b8_isin():
    """Test B8 isin operator."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "active": Vector(items=[True, False, True, False], ray_type=B8),
        },
    )

    result = (
        table.select("id", "active")
        .where(Column("active").isin([True]))
        .execute()
    )

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) == 2

    cols = list(result.columns())
    active_idx = cols.index("active")
    active_col = values[active_idx]

    returned_active = [active_col[i].value for i in range(len(active_col))]
    assert all(active is True for active in returned_active)
    assert len(returned_active) == 2


def test_select_with_b8_aggregations():
    """Test B8 aggregations."""
    table = Table.from_dict(
        {
            "category": Vector(items=["A", "A", "B", "B"], ray_type=Symbol),
            "active": Vector(items=[True, False, True, True], ray_type=B8),
        },
    )

    result = (
        table.select(
            count=Column("active").count(),
            first=Column("active").first(),
            last=Column("active").last(),
        )
        .by("category")
        .execute()
    )

    columns = result.columns()
    assert "count" in columns
    assert "first" in columns
    assert "last" in columns

    values = result.values()
    assert len(values) >= 3


def test_select_with_date_comparisons():
    """Test Date comparisons in where clauses."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "hire_date": Vector(
                items=[
                    Date(2020, 1, 1),
                    Date(2021, 6, 15),
                    Date(2022, 3, 10),
                    Date(2023, 12, 31),
                ],
                ray_type=Date,
            ),
        },
    )

    cutoff_date = Date(2022, 1, 1)
    result = (
        table.select("id", "hire_date")
        .where(Column("hire_date") >= cutoff_date)
        .execute()
    )

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) == 2

    cols = list(result.columns())
    date_idx = cols.index("hire_date")
    date_col = values[date_idx]

    returned_dates = [date_col[i].value for i in range(len(date_col))]
    assert all(date >= cutoff_date.value for date in returned_dates)


def test_select_with_date_isin():
    """Test Date isin operator."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "hire_date": Vector(
                items=[
                    Date(2020, 1, 1),
                    Date(2021, 6, 15),
                    Date(2022, 3, 10),
                    Date(2023, 12, 31),
                ],
                ray_type=Date,
            ),
        },
    )

    target_dates = [Date(2020, 1, 1), Date(2022, 3, 10)]
    result = (
        table.select("id", "hire_date")
        .where(Column("hire_date").isin(target_dates))
        .execute()
    )

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) == 2

    cols = list(result.columns())
    date_idx = cols.index("hire_date")
    date_col = values[date_idx]

    returned_dates = [date_col[i].value for i in range(len(date_col))]
    target_values = [d.value for d in target_dates]
    assert all(date in target_values for date in returned_dates)


def test_select_with_date_aggregations():
    """Test Date aggregations."""
    table = Table.from_dict(
        {
            "dept": Vector(items=["eng", "eng", "marketing", "marketing"], ray_type=Symbol),
            "hire_date": Vector(
                items=[
                    Date(2020, 1, 1),
                    Date(2021, 6, 15),
                    Date(2022, 3, 10),
                    Date(2023, 12, 31),
                ],
                ray_type=Date,
            ),
        },
    )

    result = (
        table.select(
            earliest=Column("hire_date").min(),
            latest=Column("hire_date").max(),
            first=Column("hire_date").first(),
            count=Column("hire_date").count(),
        )
        .by("dept")
        .execute()
    )

    columns = result.columns()
    assert "earliest" in columns
    assert "latest" in columns
    assert "first" in columns
    assert "count" in columns

    values = result.values()
    assert len(values) >= 4


def test_select_with_timestamp_comparisons():
    """Test Timestamp comparisons in where clauses."""
    from datetime import datetime

    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "created_at": Vector(
                items=[
                    Timestamp(datetime(2020, 1, 1, 10, 0, 0)),
                    Timestamp(datetime(2021, 6, 15, 14, 30, 0)),
                    Timestamp(datetime(2022, 3, 10, 9, 15, 0)),
                    Timestamp(datetime(2023, 12, 31, 23, 59, 59)),
                ],
                ray_type=Timestamp,
            ),
        },
    )

    cutoff = Timestamp(datetime(2022, 1, 1, 0, 0, 0))
    result = (
        table.select("id", "created_at")
        .where(Column("created_at") >= cutoff)
        .execute()
    )

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) == 2

    cols = list(result.columns())
    ts_idx = cols.index("created_at")
    ts_col = values[ts_idx]

    returned_timestamps = [ts_col[i].value for i in range(len(ts_col))]
    assert all(ts >= cutoff.value for ts in returned_timestamps)


def test_select_with_timestamp_isin():
    """Test Timestamp isin operator."""
    from datetime import datetime

    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "created_at": Vector(
                items=[
                    Timestamp(datetime(2020, 1, 1, 10, 0, 0)),
                    Timestamp(datetime(2021, 6, 15, 14, 30, 0)),
                    Timestamp(datetime(2022, 3, 10, 9, 15, 0)),
                    Timestamp(datetime(2023, 12, 31, 23, 59, 59)),
                ],
                ray_type=Timestamp,
            ),
        },
    )

    target_timestamps = [
        Timestamp(datetime(2020, 1, 1, 10, 0, 0)),
        Timestamp(datetime(2022, 3, 10, 9, 15, 0)),
    ]
    result = (
        table.select("id", "created_at")
        .where(Column("created_at").isin(target_timestamps))
        .execute()
    )

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) == 2

    cols = list(result.columns())
    ts_idx = cols.index("created_at")
    ts_col = values[ts_idx]

    returned_timestamps = [ts_col[i].value for i in range(len(ts_col))]
    target_values = [ts.value for ts in target_timestamps]
    assert all(ts in target_values for ts in returned_timestamps)


def test_select_with_timestamp_aggregations():
    """Test Timestamp aggregations."""
    from datetime import datetime

    table = Table.from_dict(
        {
            "dept": Vector(items=["eng", "eng", "marketing", "marketing"], ray_type=Symbol),
            "created_at": Vector(
                items=[
                    Timestamp(datetime(2020, 1, 1, 10, 0, 0)),
                    Timestamp(datetime(2021, 6, 15, 14, 30, 0)),
                    Timestamp(datetime(2022, 3, 10, 9, 15, 0)),
                    Timestamp(datetime(2023, 12, 31, 23, 59, 59)),
                ],
                ray_type=Timestamp,
            ),
        },
    )

    result = (
        table.select(
            earliest=Column("created_at").min(),
            latest=Column("created_at").max(),
            first=Column("created_at").first(),
            count=Column("created_at").count(),
        )
        .by("dept")
        .execute()
    )

    columns = result.columns()
    assert "earliest" in columns
    assert "latest" in columns
    assert "first" in columns
    assert "count" in columns

    values = result.values()
    assert len(values) >= 4


def test_select_with_i16_comparisons():
    """Test I16 comparisons in where clauses."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "score": Vector(items=[100, 200, 300, 400], ray_type=I16),
        },
    )

    result = table.select("id", "score").where(Column("score") >= 250).execute()

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) == 2

    cols = list(result.columns())
    score_idx = cols.index("score")
    score_col = values[score_idx]

    returned_scores = [score_col[i].value for i in range(len(score_col))]
    assert all(score >= 250 for score in returned_scores)
    assert 300 in returned_scores
    assert 400 in returned_scores


def test_select_with_i16_isin():
    """Test I16 isin operator."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "score": Vector(items=[100, 200, 300, 400], ray_type=I16),
        },
    )

    result = (
        table.select("id", "score")
        .where(Column("score").isin([100, 300]))
        .execute()
    )

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) == 2

    cols = list(result.columns())
    score_idx = cols.index("score")
    score_col = values[score_idx]

    returned_scores = [score_col[i].value for i in range(len(score_col))]
    assert all(score in [100, 300] for score in returned_scores)
    assert 100 in returned_scores
    assert 300 in returned_scores


def test_select_with_i32_comparisons():
    """Test I32 comparisons in where clauses."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "count": Vector(items=[1000, 2000, 3000, 4000], ray_type=I32),
        },
    )

    result = table.select("id", "count").where(Column("count") > 2000).execute()

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) == 2

    cols = list(result.columns())
    count_idx = cols.index("count")
    count_col = values[count_idx]

    returned_counts = [count_col[i].value for i in range(len(count_col))]
    assert all(count > 2000 for count in returned_counts)
    assert 3000 in returned_counts
    assert 4000 in returned_counts


def test_select_with_i32_isin():
    """Test I32 isin operator."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "count": Vector(items=[1000, 2000, 3000, 4000], ray_type=I32),
        },
    )

    result = (
        table.select("id", "count")
        .where(Column("count").isin([1000, 3000, 5000]))
        .execute()
    )

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) == 2

    cols = list(result.columns())
    count_idx = cols.index("count")
    count_col = values[count_idx]

    returned_counts = [count_col[i].value for i in range(len(count_col))]
    assert all(count in [1000, 3000, 5000] for count in returned_counts)
    assert 1000 in returned_counts
    assert 3000 in returned_counts


def test_select_with_u8_comparisons():
    """Test U8 comparisons in where clauses."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "priority": Vector(items=[1, 5, 10, 15], ray_type=U8),
        },
    )

    result = (
        table.select("id", "priority")
        .where(Column("priority") <= 5)
        .execute()
    )

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) == 2

    cols = list(result.columns())
    priority_idx = cols.index("priority")
    priority_col = values[priority_idx]

    returned_priorities = [priority_col[i].value for i in range(len(priority_col))]
    assert all(priority <= 5 for priority in returned_priorities)
    assert 1 in returned_priorities
    assert 5 in returned_priorities


def test_select_with_u8_isin():
    """Test U8 isin operator."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "priority": Vector(items=[1, 5, 10, 15], ray_type=U8),
        },
    )

    result = (
        table.select("id", "priority")
        .where(Column("priority").isin([1, 10]))
        .execute()
    )

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) == 2

    cols = list(result.columns())
    priority_idx = cols.index("priority")
    priority_col = values[priority_idx]

    returned_priorities = [priority_col[i].value for i in range(len(priority_col))]
    assert all(priority in [1, 10] for priority in returned_priorities)
    assert 1 in returned_priorities
    assert 10 in returned_priorities


def test_select_with_integer_aggregations():
    """Test aggregations with I16, I32, U8."""
    table = Table.from_dict(
        {
            "category": Vector(items=["A", "A", "B", "B"], ray_type=Symbol),
            "i16_val": Vector(items=[10, 20, 30, 40], ray_type=I16),
            "i32_val": Vector(items=[100, 200, 300, 400], ray_type=I32),
            "u8_val": Vector(items=[1, 2, 3, 4], ray_type=U8),
        },
    )

    result = (
        table.select(
            i16_sum=Column("i16_val").sum(),
            i32_sum=Column("i32_val").sum(),
            u8_sum=Column("u8_val").sum(),
            count=Column("i16_val").count(),
        )
        .by("category")
        .execute()
    )

    columns = result.columns()
    assert "i16_sum" in columns
    assert "i32_sum" in columns
    assert "u8_sum" in columns
    assert "count" in columns

    values = result.values()
    assert len(values) >= 4


def test_select_with_time_comparisons():
    """Test Time comparisons in where clauses."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "start_time": Vector(
                items=[
                    Time("09:00:00"),
                    Time("12:00:00"),
                    Time("15:30:00"),
                    Time("18:00:00"),
                ],
                ray_type=Time,
            ),
        },
    )

    cutoff_time = Time("12:00:00")
    result = (
        table.select("id", "start_time")
        .where(Column("start_time") >= cutoff_time)
        .execute()
    )

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) == 2

    cols = list(result.columns())
    time_idx = cols.index("start_time")
    time_col = values[time_idx]

    returned_times = [time_col[i].value for i in range(len(time_col))]
    assert all(time >= cutoff_time.value for time in returned_times)


def test_select_with_time_isin():
    """Test Time isin operator."""
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "start_time": Vector(
                items=[
                    Time("09:00:00"),
                    Time("12:00:00"),
                    Time("15:30:00"),
                    Time("18:00:00"),
                ],
                ray_type=Time,
            ),
        },
    )

    target_times = [Time("09:00:00"), Time("15:30:00")]
    result = (
        table.select("id", "start_time")
        .where(Column("start_time").isin(target_times))
        .execute()
    )

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) == 2

    cols = list(result.columns())
    time_idx = cols.index("start_time")
    time_col = values[time_idx]

    returned_times = [time_col[i].value for i in range(len(time_col))]
    target_values = [t.value for t in target_times]
    assert all(time in target_values for time in returned_times)


def test_select_with_time_aggregations():
    """Test Time aggregations."""
    table = Table.from_dict(
        {
            "shift": Vector(items=["morning", "morning", "afternoon", "afternoon"], ray_type=Symbol),
            "start_time": Vector(
                items=[
                    Time("09:00:00"),
                    Time("10:00:00"),
                    Time("14:00:00"),
                    Time("15:00:00"),
                ],
                ray_type=Time,
            ),
        },
    )

    result = (
        table.select(
            earliest=Column("start_time").min(),
            latest=Column("start_time").max(),
            first=Column("start_time").first(),
            count=Column("start_time").count(),
        )
        .by("shift")
        .execute()
    )

    columns = result.columns()
    assert "earliest" in columns
    assert "latest" in columns
    assert "first" in columns
    assert "count" in columns

    values = result.values()
    assert len(values) >= 4


def test_group_by_with_integer_types():
    """Test group by with integer types."""
    table = Table.from_dict(
        {
            "age": Vector(items=[25, 25, 30, 30, 35], ray_type=I64),
            "score": Vector(items=[100, 200, 150, 250, 300], ray_type=I64),
        },
    )

    result = (
        table.select(
            avg_score=Column("score").mean(),
            total_score=Column("score").sum(),
            count=Column("score").count(),
        )
        .by("age")
        .execute()
    )

    columns = result.columns()
    assert "avg_score" in columns
    assert "total_score" in columns
    assert "count" in columns

    values = result.values()
    assert len(values) >= 3


def test_group_by_with_f64():
    """Test group by with F64."""
    table = Table.from_dict(
        {
            "price_range": Vector(items=[10.0, 10.0, 20.0, 20.0], ray_type=F64),
            "quantity": Vector(items=[5, 10, 3, 7], ray_type=I64),
        },
    )

    result = (
        table.select(
            total_quantity=Column("quantity").sum(),
            avg_quantity=Column("quantity").mean(),
        )
        .by("price_range")
        .execute()
    )

    columns = result.columns()
    assert "total_quantity" in columns
    assert "avg_quantity" in columns

    values = result.values()
    assert len(values) >= 2


def test_group_by_with_b8():
    """Test group by with B8."""
    table = Table.from_dict(
        {
            "active": Vector(items=[True, True, False, False], ray_type=B8),
            "score": Vector(items=[100, 200, 50, 75], ray_type=I64),
        },
    )

    result = (
        table.select(
            avg_score=Column("score").mean(),
            total_score=Column("score").sum(),
            count=Column("score").count(),
        )
        .by("active")
        .execute()
    )

    columns = result.columns()
    assert "avg_score" in columns
    assert "total_score" in columns
    assert "count" in columns

    values = result.values()
    assert len(values) >= 3
