from datetime import datetime
from unittest.mock import MagicMock
from uuid import UUID

from hypothesis import given, strategies as st

from outflux.outflux import Outflux, ZONE_INFO


@given(db=st.text(), measurement=st.text(), start=st.datetimes(), end=st.datetimes())
def test_init(db: str, measurement: str, start: datetime, end: datetime) -> None:
    url = "http://influxdb-unittest:8086"
    outflux = Outflux(url, db, measurement, start, end)

    assert outflux.url == url
    assert outflux.db == db
    assert outflux.measurement == measurement

    assert datetime.fromisoformat(outflux.start) == start.astimezone(ZONE_INFO)
    assert datetime.fromisoformat(outflux.end) == end.astimezone(ZONE_INFO)


@given(uuid=st.uuids(), start=st.datetimes(), end=st.datetimes())
def test_execute(uuid: UUID, start: datetime, end: datetime) -> None:
    url = "http://influxdb-unittest:8086"
    db = "testdb"
    measurement = "unittests"
    outflux = Outflux(url, db, measurement, start, end)

    session = MagicMock()
    response = MagicMock()
    session.post.return_value = response

    query = outflux.query_select(uuid)
    outflux.execute(session, query)

    assert session.post.called
    args, kwargs = session.post.call_args
    assert args[0] == url
    assert kwargs["params"]["db"] == db
    assert kwargs["params"]["q"] == query


@given(uuid=st.uuids(), start=st.datetimes(), end=st.datetimes())
def test_query_select(uuid: UUID, start: datetime, end: datetime) -> None:
    url = "http://influxdb-unittest:8086"
    db = "testdb"
    measurement = "unittests"
    outflux = Outflux(url, db, measurement, start, end)
    query = outflux.query_select(uuid)

    assert query.lower().startswith("select")
    assert measurement in query

    assert f"'{start.astimezone(ZONE_INFO).isoformat()}'" in query
    assert f"'{end.astimezone(ZONE_INFO).isoformat()}'" in query

    assert f"'{uuid}'" in query


@given(uuid=st.uuids(), start=st.datetimes(), end=st.datetimes())
def test_query_delete(uuid: UUID, start: datetime, end: datetime) -> None:
    url = "http://influxdb-unittest:8086"
    db = "testdb"
    measurement = "unittests"
    outflux = Outflux(url, db, measurement, start, end)
    query = outflux.query_delete(uuid)

    assert query.lower().startswith("delete")
    assert measurement in query

    assert f"'{start.astimezone(ZONE_INFO).isoformat()}'" in query
    assert f"'{end.astimezone(ZONE_INFO).isoformat()}'" in query

    assert f"'{uuid}'" in query
