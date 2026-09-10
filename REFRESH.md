# Weekly homework refresh

The instructions Claude follows to update `week.json`. Kick it off with:

> Refresh Cruz's homework from the Diamond Team calendar. Follow REFRESH.md.

Nothing here touches `index.html`. If a refresh ever wants to change the
layout, the styling, or the packing list, that's a bug — stop and say so.

---

## 1. Find this week's deck

**Every week has its own separate Google Slides deck.** They're all listed in
the team's archive doc. Read it with the Google Drive connector:

- `read_file_content` on fileId `1smWbYjBZx9auMdju2WeKwZ0Fy4kii8adl2c0ox9x1L4`
- *"Diamond Homework Calendar Archive 2026-2027"*, owned by christine_zeiner@whps.org

It has rows like *"Diamond HW Calendar, Week of 9/14"*, each with a
presentation link. Work out the Monday of the week you need, pick the matching
row, then read that presentation.

**Never reuse a deck id from a previous run — it changes every week.**

If there is no row for that week, the archive hasn't been extended (it ran
through the week of 10/26 as of Sep 2026). Change nothing; say the archive
stops at the last week listed.

## 2. What a date means

**Each weekday slide is the homework given that day, to do that night.** The
Wednesday slide's Science row says *"due Friday"*; the Thursday slide's says
*"due tomorrow"*. So `date` is **the night Cruz does the work**. Record the
deadline itself as an absolute `dueDate`, not as the deck's relative wording.

Getting this backwards is how the first version lost a whole night of math.
Read every weekday slide, and put each row on the day whose slide it came from.

## 3. Pull from the deck

- Homework per weekday, by class.
  **Cruz is in 6H math.** Ms. Rivera's rows list 6S, 6H and 7H — only 6H is
  his. Ignore 6S and 7H everywhere, including on the assessment calendar (a
  "7H Quick Quiz" is not his).
- Stated due dates ("due Thursday", "due by Sunday pm").
- Items that run all week rather than sitting on one night → `running`.
- Anything needing a parent or caregiver → set `"adult": true`.
- The monthly assessment calendar and the "Important dates" note on slide 1.
- No-school days and holidays.

It is **normal** for homework rows to be empty before or early in the week —
teachers fill them in as it goes. Write what's there and say the homework isn't
filled in yet, rather than reporting a free week.

Teachers: Ms. Metsack (ELA, P7), Ms. Rivera (math, P4), Mrs. Vocke (science,
P2), Mr. Fleming (social studies, P5), Profe Zeiner (Spanish, P1 — she also
owns the calendar).

## 4. Cross-check the assessments

Each deck carries its own copy of the month's assessment calendar, and they
drift. **Read the previous week's deck too and compare.** Where they disagree,
keep the entry and add a `note` saying the decks disagree. Never silently pick
one.

## 5. Write week.json

Edit **only** `week.json`. Set `updated` to today and `weekOf` to the Monday of
the week being published.

```jsonc
{
  "updated": "2026-09-13",        // today, YYYY-MM-DD
  "weekOf":  "2026-09-14",        // Monday of the published week
  "deck":    "https://docs.google.com/presentation/d/<this week's deck>/edit",
  "archive": "https://docs.google.com/document/d/1smWbYjBZx9auMdju2WeKwZ0Fy4kii8adl2c0ox9x1L4/edit",

  "items": [                       // one entry per class, per night
    {
      "id":      "math6h-p20",     // stable slug; the SAME id on every day the
                                   // same assignment appears, so ticking it
                                   // once ticks it everywhere
      "date":    "2026-09-15",     // the night it belongs to
      "cls":     "Math 6H",
      "teacher": "Ms. Rivera",     // or null
      "period":  4,                // or null
      "text":    "Math book p.20 #1–6",
      "dueDate": "2026-09-17",     // optional; the real deadline, absolute
      "adult":   true,             // optional, flags 'needs a grown-up'
      "note":    "…",              // optional italic line
      "submit":  "https://…",      // optional; makes the title a link
      "link":    "https://…"       // optional; used if there's no submit
    }
  ],

  "quizzes":  [ { "date": "2026-09-16", "text": "Spanish — greetings quiz", "note": "optional" } ],
  "running":  [ { "id": "…", "cls": "…", "teacher": "…", "period": 7,
                  "text": "…", "due": "finish by Sunday night",  // free text: no single date
                  "weekOf": "2026-09-14" } ],   // must be a Monday
  "noSchool": { "2026-09-21": "Yom Kippur" },
  "open":     [ ],                 // no deadline given; keep entries until done
  "sources":  [ ]                  // class links; rarely changes
}
```

Rules that matter:

- **Write deadlines as `dueDate`, never as words.** The page turns one date
  into "due Thu 9/17", "DUE TODAY" or "was due Thu 9/17" depending on when the
  card is read, so it stays right in every view. Writing `"due": "due
  tomorrow"` breaks the moment that card is seen on another day. Use the
  free-text `due` only where the deck gives no single date, like "finish by
  Sunday night". An item with neither is labelled with the night it was set —
  don't invent a deadline the deck doesn't state.
- **Reuse ids across days.** The same assignment on Mon/Tue/Wed is three
  entries sharing one `id` and one `dueDate`, differing only in `date`. That's how ticking
  it once marks it done everywhere and how overdue detection works.
- **Keep future weeks.** Don't delete entries for later weeks just because
  they're outside the current one — the "Later on" column reads them.
- **Keep `open` entries** until they're actually done.
- Dates are `YYYY-MM-DD`. `running[].weekOf` and `weekOf` must be Mondays.
- **Walk every weekday slide and every class row before you finish.** Five
  slides x five classes. An empty row is fine; a row you never looked at is
  how homework goes missing. Science and Social Studies rows also carry
  starred "last call" notes and checks that are real homework.

## 6. Validate, then show the diff

```bash
python3 validate.py
git diff week.json
```

Fix anything the validator flags. Do **not** push without showing the diff
first.

## 7. Publish

```bash
git add week.json && git commit -m "Homework, week of <date>" && git push
```

GitHub Pages picks it up within a minute. Cruz's phone gets it the next time he
opens the app with any signal.

## 8. Report back

Short and scannable:

- homework night by night
- assessments coming up
- anything needing a grown-up
- anything the decks disagreed about

---

**Background.** Cruz is a 6th grader on the Diamond Team at WHPS. These decks
are the real homework source — Google Classroom misses most of it and its class
pages are unreliable, so don't depend on them.
