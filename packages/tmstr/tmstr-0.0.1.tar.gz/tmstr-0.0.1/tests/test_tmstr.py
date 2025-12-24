# test_tmstr.py

import pytest
from datetime import datetime, timedelta

from tmstr import Date, Range, parse
from tmstr.text2num import text2num


def assert_dt_parts(
    d,
    *,
    year=None,
    month=None,
    day=None,
    hour=None,
    minute=None,
    second=None,
    weekday=None,
):
    if year is not None:
        assert d.year == year
    if month is not None:
        assert d.month == month
    if day is not None:
        assert d.day == day
    if hour is not None:
        assert d.hour == hour
    if minute is not None:
        assert d.minute == minute
    if second is not None:
        assert d.second == second
    if weekday is not None:
        assert d.weekday == weekday


def test_fullstring():
    now = datetime.now()

    # DATE
    d = Date("01/10/2015 at 7:30pm")
    assert_dt_parts(d, year=2015, month=1, day=10, hour=19, minute=30)

    d = Date("may 23rd, 1988 at 6:24 am")
    assert_dt_parts(d, year=1988, month=5, day=23, hour=6, minute=24)

    # RANGE
    r = Range("From 04/17/13 04:18:00 to 05/01/13 17:01:00", tz="US/Central")
    assert_dt_parts(r.start, year=2013, month=4, day=17, hour=4, minute=18)
    assert_dt_parts(r.end, year=2013, month=5, day=1, hour=17, minute=1)

    r = Range("between january 15th at 3 am and august 5th 5pm")
    assert_dt_parts(r[0], year=now.year, month=1, day=15, hour=3)
    assert_dt_parts(r[1], year=now.year, month=8, day=5, hour=17)

    r = Range("2012 feb 2 1:13PM to 6:41 am on sept 8 2012")
    assert_dt_parts(r[0], year=2012, month=2, day=2, hour=13, minute=13)
    assert_dt_parts(r[1], year=2012, month=9, day=8, hour=6, minute=41)

    d = Date("2013-09-10T10:45:50")
    assert_dt_parts(d, year=2013, month=9, day=10, hour=10, minute=45, second=50)

    r = Range("tomorrow 10am to 5pm")
    tomorrow = now + timedelta(days=1)
    assert r.start.year == tomorrow.year
    assert r.end.year == tomorrow.year
    assert r.start.month == tomorrow.month
    assert r.end.month == tomorrow.month
    assert r.start.day == tomorrow.day
    assert r.end.day == tomorrow.day
    assert r.start.hour == 10
    assert r.end.hour == 17


def test_dates():
    d = Date("August 25th, 2014 12:30 PM")
    assert_dt_parts(d, year=2014, month=8, day=25, hour=12, minute=30, second=0)

    d = Date("may 23, 2018 1 pm")
    assert_dt_parts(d, year=2018, month=5, day=23, hour=13, minute=0, second=0)

    d = Date("1-2-13 2 am")
    assert_dt_parts(d, year=2013, month=1, day=2, hour=2, minute=0, second=0)

    d = Date("dec 15th '01 at 6:25:01 am")
    assert_dt_parts(d, year=2001, month=12, day=15, hour=6, minute=25, second=1)


def test_singles():
    now = datetime.now()

    # Single check
    assert Date("2012").year == 2012
    assert Date("January 2013").month == 1
    assert Date("feb 2011").month == 2
    assert Date("05/23/2012").month == 5
    assert Date("01/10/2015 at 7:30pm").month == 1
    assert Date("today").day == now.day

    r = Range("january")
    assert_dt_parts(r[0], month=1, day=1, hour=0)
    assert_dt_parts(r[1], month=2, day=1, hour=0)

    r = Range("2010")
    assert_dt_parts(r[0], year=2010, month=1, day=1, hour=0)
    assert_dt_parts(r[1], year=2011, month=1, day=1, hour=0)

    r = Range("january 2011")
    assert_dt_parts(r[0], year=2011, month=1, day=1, hour=0)
    assert_dt_parts(r[1], year=2011, month=2, day=1, hour=0)

    assert_dt_parts(Date(1374681560), year=2013, month=7, day=24)
    assert_dt_parts(Date(str(1374681560)), year=2013, month=7, day=24)

    r = Range(1374681560)
    assert r.start.day == 24
    assert r.end.day == 25

    # offset timezones
    assert Date("2014-03-06 15:33:43.764419-05").hour == 20


def test_this():
    now = datetime.now()

    # this year
    year = Range("this year")
    assert_dt_parts(year.start, year=now.year, month=1, day=1, hour=0, minute=0)
    assert_dt_parts(year.end, year=now.year + 1, month=1, day=1, hour=0, minute=0)

    # 1 year (from now)
    # Original test uses (now + 1 day) as a "stabilizer" near midnight.
    anchor = now + timedelta(days=1)
    year = Range("1 year")
    assert_dt_parts(year.start, year=anchor.year - 1, month=anchor.month, day=anchor.day, hour=0, minute=0)
    assert_dt_parts(year.end, year=anchor.year, month=anchor.month, day=anchor.day, hour=0, minute=0)

    # this month
    month = Range("this month")
    assert_dt_parts(month.start, year=now.year, month=now.month, day=1, hour=0, minute=0)

    expected_end_year = month.start.year + (1 if month.start.month + 1 == 13 else 0)
    expected_end_month = (month.start.month + 1) if month.start.month + 1 < 13 else 1
    assert_dt_parts(month.end, year=expected_end_year, month=expected_end_month, day=1, hour=0, minute=0)

    # this month w/ offset
    mo = Range("this month", offset=dict(hour=6))
    assert_dt_parts(mo.start, year=now.year, month=now.month, day=1, hour=6, minute=0)

    expected_end_year = mo.start.year + (1 if mo.start.month + 1 == 13 else 0)
    expected_end_month = (mo.start.month + 1) if mo.start.month + 1 < 13 else 1
    assert_dt_parts(mo.end, year=expected_end_year, month=expected_end_month, day=1, hour=6, minute=0)

    assert len(Range("6d")) == 518400
    assert len(Range("6 d")) == 518400
    assert len(Range("6 days")) == 518400
    assert len(Range("12h")) == 43200
    assert len(Range("6 h")) == 21600
    assert len(Range("10m")) == 600
    assert len(Range("10 m")) == 600
    assert len(Range("10 s")) == 10
    assert len(Range("10s")) == 10


def test_dow():
    for x, day in enumerate(("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")):
        d = Date(day)
        r = Range(day)

        assert d.hour == 0
        assert d.weekday == 1 + x

        # length is 1 day in seconds
        assert len(r) == 86400
        assert r.start.hour == 0
        assert r.end.hour == 0
        assert r.end.weekday == (1 if x + 1 == 7 else (2 + x))


def test_offset():
    now = datetime.now()

    assert Date("today", offset=dict(hour=6)).hour == 6
    assert Date("today", offset=dict(hour=6)).day == now.day

    assert Range("this week", offset=dict(hour=10)).start.hour == 10
    assert Date("yesterday", offset=dict(hour=10)).hour == 10

    # keep original expectation: offset doesn't clobber explicit time
    assert Date("august 25th 7:30am", offset=dict(hour=10)).hour == 7


def test_lengths():
    assert len(Range("next 10 weeks")) == 5443200
    assert len(Range("this week")) == 604800
    assert len(Range("3 weeks")) == 1814400
    assert len(Range("yesterday")) == 86400


def test_in():
    assert Date("yesterday") in Range("last 7 days")
    assert Date("today") in Range("this month")
    assert Date("today") in Range("this month")
    assert Range("this month") in Range("this year")
    assert Range("this day") in Range("this week")


def test_tz():
    assert Date("today", tz="US/Central").tz.zone == "US/Central"


def test_cut():
    assert Range("from january 10th 2010 to february 2nd 2010").cut("10 days") == Range(
        "from january 10th 2010 to jan 20th 2010"
    )
    assert Date("jan 10") + "1 day" == Date("jan 11")
    assert Date("jan 10") - "5 day" == Date("jan 5")


def test_compare():
    assert (Range("10 days") == Date("yestserday")) is False
    assert Date("yestserday") in Range("10 days")
    assert Range("10 days") in Range("100 days")
    assert Range("next 2 weeks") > Range("1 year")
    assert Range("yesterday") < Range("now")


def test_last():
    now = datetime.now()

    year = Range("last year")
    assert_dt_parts(year.start, year=now.year - 1, month=now.month, day=now.day, hour=0, minute=0)
    assert_dt_parts(year.end, year=now.year, month=now.month, day=now.day, hour=0, minute=0)
    assert Date("today") in year

    assert Date("last tuesday") in Range("8 days")
    assert Date("monday") in Range("8 days")
    assert Date("last fri") in Range("8 days")
    assert Range("1 year ago") == Range("last year")
    assert Range("year ago") == Range("last year")


def test_psql_infinity():
    d = Date("infinity")
    assert d > "now"
    assert d > "today"
    assert d > "next week"

    assert (d in Range("this year")) is False
    assert (d in Range("next 5 years")) is False

    assert Range("month") < d

    r = Range("today", "infinity")
    assert "next 5 years" in r
    assert Date("today") in r
    assert d in r
    assert (d > r) is False
    assert (r > d) is False

    r = Range('["2013-12-09 06:57:46.54502-05",infinity)')
    assert r.end == "infinity"
    assert "next 5 years" in r
    assert Date("today") in r
    assert d in r
    assert (d > r) is False
    assert (r > d) is False

    # -05 => +5 hours UTC, so 06:57 local becomes 11:57 UTC
    assert_dt_parts(r.start, year=2013, month=12, day=9, hour=11, minute=57, second=46)


def test_date_adjustment():
    d = Date("Jan 1st 2014 at 10 am")
    assert_dt_parts(d, year=2014, month=1, day=1, hour=10, minute=0, second=0)

    d.hour = 5
    d.day = 15
    d.month = 4
    d.year = 2013
    d.minute = 40
    d.second = 14

    assert_dt_parts(d, year=2013, month=4, day=15, hour=5, minute=40, second=14)
    assert str(d.date) == "2013-04-15 05:40:14"


def test_parse():
    assert parse("tuesday at 10pm")["hour"] == 22
    assert parse("tuesday at 10pm")["weekday"] == 2
    assert parse("may of 2014")["year"] == 2014


@pytest.mark.parametrize(
    "equals,string",
    [
        (1, "one"),
        (12, "twelve"),
        (72, "seventy two"),
        (300, "three hundred"),
        (1200, "twelve hundred"),
        (12304, "twelve thousand three hundred four"),
        (6000000, "six million"),
        (6400005, "six million four hundred thousand five"),
        (123456789012, "one hundred twenty three billion four hundred fifty six million seven hundred eighty nine thousand twelve"),
        (4000000000000000000000000000000000, "four decillion"),
    ],
)
def test_string_to_number(equals, string):
    assert text2num(string) == equals
    # six.u(...) was basically "ensure unicode"; in py3 str is unicode already.
    assert text2num(str(string)) == equals


def test_plus():
    date1 = Date("october 18, 2013 10:04:32 PM")
    date2 = date1 + "10 seconds"
    assert date2.second == date1.second + 10

