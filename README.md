# Cruz's School Day

A standalone web app: today's homework, and what goes in the bag. Built for a
6th grader with ADD to run himself, on a phone with almost no internet.

It is a folder of static files. No build step, no framework, no server, no
accounts, no npm install. Open `index.html` and it works.

---

## Why it's built this way

Three constraints drove every decision:

**His phone may be locked to an allow-list of websites.** The phone is the
family's, not the school's — he has no school-issued devices at all — but
under iOS Screen Time's *Allowed Websites Only*, anything not on the list is
blocked, including a Google Fonts stylesheet. So the page makes **zero
external requests**. System fonts, hand-generated icons, everything
self-contained. One URL on the allow-list is enough.

**He often has no signal.** A service worker (`sw.js`) caches the whole app.
After the first visit it opens instantly with the plane in airplane mode, and
still shows the right week. When a refresh has landed it picks that up; when
there's nothing to reach it shows the last saved copy and says so.

**Updates land by themselves.** The worker serves the cached app instantly,
which is the point on a phone with no signal — but it used to mean a new
version of the app only appeared on the *second* open, because the first
merely fetched it into the cache. The page now reloads once when a new worker
takes over, so one open is enough. Homework and events were never affected:
`week.json` is fetched fresh every time.

**It has to survive without Claude running.** The page is plain files on a
plain host. The weekly homework update writes one data file. If nobody updates
it for two weeks, the page says "last updated 16 days ago — check with a
grown-up" rather than quietly showing a stale week as though it were current.

## The files

| File | What it is |
|---|---|
| `index.html` | The whole app — markup, styles, logic. Layout and behaviour live here. |
| `week.json` | **The only file the weekly refresh touches.** Homework, assessments, days off. |
| `sw.js` | Offline caching. |
| `manifest.webmanifest` | Makes it install to the home screen as an app. |
| `icon-*.png` | Home screen icon. |
| `make-icons.py` | Regenerates the icons from scratch. Only if you want a different one. |
| `validate.py` | Checks `week.json` is sane before it goes live. |

The split matters: **a bad homework update can't break the page**, because the
update never touches the code.

## Deploying

It's static files, so anything that serves a folder works — GitHub Pages,
Netlify, Cloudflare Pages, a school web folder.

On GitHub Pages, a push to `main` publishes within a minute:

```bash
git add -A && git commit -m "Update homework for the week" && git push
```

To run it locally while making changes:

```bash
python3 -m http.server 8123 --directory ~/Projects/cruz-school-day
```

Then open <http://localhost:8123>. A service worker needs `localhost` or
HTTPS — opening the file directly with `file://` will not work.

## Putting it on Cruz's iPhone

1. If his phone is on an allow-list: **Settings → Screen Time → Content &
   Privacy Restrictions → Content Restrictions → Web Content → Allowed
   Websites Only** → add the site URL.
2. Open the URL in **Safari** (not Chrome — only Safari can install to the
   home screen on iOS).
3. **Share → Add to Home Screen.**

It launches full screen with no address bar, and looks and behaves like an app.

**Reminders.** The web can't reliably push notifications to an iPhone home
screen app, so the app doesn't pretend to. Set two repeating alarms in his
Clock app instead — one after school, one at bedtime — and let the app be what
he opens when they go off.

## The weekly homework refresh

Sunday evening, in Claude Code, from this folder:

> Refresh Cruz's homework from the Diamond Team calendar. Follow REFRESH.md.

That reads the week's slide deck from Google Drive, rewrites `week.json`, runs
the validator, and shows you the diff before anything is pushed. The full
instructions — including which class is his and how to handle the decks
disagreeing — are in [REFRESH.md](REFRESH.md).

To automate it, ask Claude to schedule that same prompt for Sunday 7pm and
Monday 6am Eastern.

After any manual edit to `week.json`:

```bash
python3 validate.py
```

## Things that will bite you

- **There are three sources.** Homework from the Diamond deck, Spanish from the
  World Language calendar, after-school activities from the family Google
  Calendar. Each is easy to forget, and forgetting one loses a whole category
  of Cruz's day silently.
- **The deck and the World Language calendar are separate.** The Diamond deck carries ELA, math,
  science and social studies. **Spanish is not on it** — the slides link out to
  a separate World Language calendar, which the refresh must read as well. A
  whole class was missing from this app until Sep 9 because of that.
- **Both sources list sections that aren't his.** 6H not 6S or 7H in math;
  Profe Zeiner, not Luzusky, in Spanish. `validate.py` flags the others.
- **Google Classroom is not the source.** Its to-do view showed no math at all
  in a week Cruz had math homework every night. The weekly deck is the truth.
- **Future decks exist but are empty.** All the term's decks were created up
  front, so a future week shows only its assessment calendar and days off.
  That's normal, not a free week.
- **Assessment dates drift between decks.** The 9/7 deck lists a science lab
  safety quiz that the 9/14 deck doesn't. Flag conflicts in a `note`, never
  silently pick one.
- **The archive doc stops at the week of 10/26.** When it runs out, someone has
  to point Claude at the extended list.
- **The "see the deck" links need docs.google.com reachable.** If the phone is
  on a Screen Time allow-list, add `docs.google.com` (and
  `classroom.google.com` for the submit links) alongside the site itself, or
  the links go nowhere.
- **Nothing here is school-issued.** Cruz has no school tablet, phone or
  laptop; every device is the family's. That's why there's no Chromebook on
  the packing list, and why "submit on Google Classroom" means doing it at
  home.
- **Ticks don't sync.** Each device keeps its own, in that browser's storage.
  They're gone if he clears site data. This was a deliberate choice: the app is
  his to manage, not a monitor. The consequence is that **a phone that didn't
  do the ticking shows everything as untouched** — a parent's device can't tell
  you what he's done, only what was set.
- **A red edge means one specific thing:** unticked work whose last listed day
  has passed — exactly what the catch-up line at the foot of "Just today"
  counts. Tapping that line opens the week those items are in, which may not
  be this week. Work that's still listed today shows its own "was due"
  label but is not red and is not counted; it's current, not missed.
- **There is no overdue banner.** Unfinished work stays in its own day column
  in the week view, marked with a red edge and a "was due" label, rather than
  being piled at the top of the page. So `week.json` must keep recent past
  weeks — see REFRESH.md.
- **The bag changes through the day.** It shows today's list until school ends
  at 3pm, then switches to the next school day. Between 8am and 3pm it
  collapses to one line, because a list he can't act on is just something to
  scroll past.
- **Activity kit is not in the school bag.** Cruz comes home before squash and
  pickleball, so the racquet, goggles and paddle are picked up on the way back
  out. They're tick-off items on the activity's own card, from `gear` in
  `week.json`, and they're keyed by the activity's date so they don't move
  when the bag rolls over at 3pm.
- **The packing list lives in `index.html`, not `week.json`** — deliberately,
  so a homework refresh can never wipe the list Cruz has customised. He edits
  it in the page itself under *Edit list*.

## Privacy

The repo is public so GitHub Pages can serve it for free. It carries a first
name, a school team, teachers' names, and homework. `robots.txt` and a
`noindex` tag keep it out of search engines, but a public repo is public —
anyone with the URL can read it. Nothing here is a password, an address, or a
full name. If that trade stops feeling right, move the hosting to Netlify or
Cloudflare Pages, both of which serve a private repo on their free tier.
