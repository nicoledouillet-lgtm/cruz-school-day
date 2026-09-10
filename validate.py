#!/usr/bin/env python3
"""Sanity-checks week.json before it goes live.

A refresh that writes a malformed file would leave Cruz staring at "Can't
load" on a school morning, so run this after every update:

    python3 validate.py
"""
import json, sys, datetime, re

REQUIRED_ITEM = ("id", "date", "cls", "text")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
problems, warnings = [], []


def check_date(value, where):
    if not DATE.match(str(value)):
        problems.append(f"{where}: date {value!r} is not YYYY-MM-DD")
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        problems.append(f"{where}: {value!r} is not a real date")
        return None


try:
    data = json.load(open("week.json"))
except Exception as e:                                    # noqa: BLE001
    sys.exit(f"week.json is not valid JSON: {e}")

updated = check_date(data.get("updated", ""), "updated")
if updated:
    age = (datetime.date.today() - updated).days
    if age < 0:
        warnings.append(f"'updated' is {-age} days in the future")
    elif age >= 8:
        warnings.append(f"'updated' is {age} days old — the page will show a stale warning")

for n, it in enumerate(data.get("items", [])):
    where = f"items[{n}]"
    for field in REQUIRED_ITEM:
        if not it.get(field):
            problems.append(f"{where}: missing {field}")
    if it.get("date"):
        check_date(it["date"], where)
    if it.get("period") is not None and not isinstance(it["period"], int):
        problems.append(f"{where}: period should be a number or null")
    if it.get("due") and it.get("dueDate"):
        problems.append(f"{where}: has both 'due' and 'dueDate' — dueDate wins, so drop 'due'")
    if it.get("dueDate"):
        due = check_date(it["dueDate"], f"{where}.dueDate")
        set_on = datetime.date.fromisoformat(it["date"]) if DATE.match(str(it.get("date", ""))) else None
        if due and set_on and due < set_on:
            problems.append(f"{where}: due {it['dueDate']} is before it was set on {it['date']}")
    # A relative word in a hand-written 'due' can't stay true across days.
    if it.get("due") and re.search(r"\b(today|tomorrow|tonight)\b", it["due"], re.I):
        warnings.append(f"{where}: 'due' says {it['due']!r} — use dueDate so the label stays right")

for n, q in enumerate(data.get("quizzes", [])):
    where = f"quizzes[{n}]"
    if not q.get("text"):
        problems.append(f"{where}: missing text")
    check_date(q.get("date", ""), where)

for n, r in enumerate(data.get("running", [])):
    where = f"running[{n}]"
    if not r.get("id") or not r.get("text"):
        problems.append(f"{where}: needs both id and text")
    monday = check_date(r.get("weekOf", ""), f"{where}.weekOf")
    if monday and monday.weekday() != 0:
        problems.append(f"{where}: weekOf {r['weekOf']} is a {monday:%A}, not a Monday")

for dk in data.get("noSchool", {}):
    check_date(dk, "noSchool")

# Both sources list several sections and only one is Cruz's. Picking up a
# neighbouring column is the likeliest way a refresh goes wrong: Ms. Rivera's
# rows carry 6S/6H/7H, and the World Language calendar has six teachers.
NOT_HIS = ("6S", "7H", "Luzusky", "Gallagher", "Yao", "Li", "French", "Chinese")
for it in data.get("items", []) + data.get("running", []):
    blob = f"{it.get('cls','')} {it.get('teacher','')} {it.get('text','')}"
    for wrong in NOT_HIS:
        if re.search(rf"\b{re.escape(wrong)}\b", blob):
            warnings.append(
                f"item {it.get('id')}: mentions {wrong} — Cruz is 6H math and Spanish with Profe Zeiner")

# Spanish only ever comes from the World Language calendar, so a week with
# none at all usually means that second document went unread.
week_of = data.get("weekOf")
if week_of and DATE.match(str(week_of)):
    monday = datetime.date.fromisoformat(week_of)
    this_week = [i for i in data.get("items", [])
                 if DATE.match(str(i.get("date", "")))
                 and 0 <= (datetime.date.fromisoformat(i["date"]) - monday).days <= 4]
    if this_week and not any("spanish" in str(i.get("cls", "")).lower() for i in this_week):
        warnings.append(
            "no Spanish anywhere in the published week — did the World Language "
            "calendar get read? (REFRESH.md step 2)")

# Same id on the same day twice would render a duplicate card.
seen = set()
for it in data.get("items", []):
    k = (it.get("id"), it.get("date"))
    if k in seen:
        problems.append(f"duplicate: {it.get('id')} appears twice on {it.get('date')}")
    seen.add(k)

for w in warnings:
    print(f"warning  {w}")
for p in problems:
    print(f"PROBLEM  {p}")

if problems:
    sys.exit(f"\n{len(problems)} problem(s) — do not deploy this.")
counts = {k: len(data.get(k, [])) for k in ("items", "quizzes", "running", "open")}
print(f"\nweek.json is good. {counts}, updated {data.get('updated')}")
