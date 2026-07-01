# Docker Debug Log — FastAPI-CRUD-Todo

> **Evaluated by:** An Ho
> **Date:** 2026-07-01
> **Purpose:** Document environment debugging judgment — distinguishing code bugs vs config bugs vs dependency bugs vs environment bugs

---

## Scenario 1: Named volume mounted onto /app — old code persists

**What I did:**
In `docker-compose.yml`, mounted a named volume `sqlite_data:/app` with the intent to persist the database. First run was fine. Then I edited the code, rebuilt the image, and ran it again.

**Error:**
No error message. The app ran normally — but code changes had no effect. Edits were completely ignored.

**First impression:**
Thought `docker build` wasn't running correctly, or was using an old cache. Tried `--no-cache` — still no change.

**What was actually happening:**
The volume mount `sqlite_data:/app` covered the entire folder containing the code, not just the database. On the first run, Docker copied the code into the volume. On subsequent rebuilds, the image had new code — but the OLD volume still held the OLD code, overriding the new code in the image. The app ran the old code from the volume, ignoring the new image entirely.

**Bug type:** Config — volume mount with incorrect scope

**Fix:**
Remove the volume mount on `/app`. If data persistence is needed, only mount the specific data file/folder, not the folder containing the code.

```yaml
# Wrong — mounts the entire code directory
volumes:
  - sqlite_data:/app

# Correct — only mounts data (if needed)
volumes:
  - ./todo.db:/app/todo.db

# Or no mount at all (sufficient for evaluation)
```

**Lesson:**
Code goes into the image (`COPY`). Data goes into a volume (`mount`). Mixing the two = code updates have no effect, with no error message to warn you. This is the most dangerous type of bug — a silent failure where the app runs normally but behaves incorrectly.

---

## Scenario 2: Bind mounting a file that doesn't exist — Docker creates a directory

**What I did:**
In `docker-compose.yml`, bind mounted `./todo.db:/app/todo.db` to persist the database. But `todo.db` did not yet exist on the host machine when `docker-compose up` was run.

**Error:**
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) unable to open database file
```

**First impression:**
Thought SQLite didn't have permission to create a file inside the container, or that the path in the code was wrong.

**What was actually happening:**
Docker behavior: when the bind mount source (host path) doesn't exist, Docker automatically creates a **directory** with that name, not a file. `./todo.db` on the host became a directory. Mounted into the container, `/app/todo.db` was a directory. SQLite tried to open a directory as a database → crash.

Verified with `ls -la` inside the container:
```
drwxrwxrwx 1 root root 4096 Jul  1 01:52 todo.db
```
The `d` at the start = directory, not a file.

**Bug type:** Config — bind mount behavior not working as expected

**Fix:**
Two options:
1. Run `touch todo.db` on the host before starting (creates an empty file → Docker mounts it correctly as a file)
2. Remove the volume mount entirely — the app will create `todo.db` inside the container on its own

**Lesson:**
Bind mounting a non-existent file → Docker always creates a directory, never a file. Docker has no way of knowing whether you want a file or a directory. Before bind mounting, verify that the source exists AND is the correct type (file vs directory).

---

## Scenario 3: Directory artifact from Scenario 2 gets baked into the image

**What I did:**
After Scenario 2, removed the volume mount from `docker-compose.yml`. Deleted the `todo.db` directory on the host with `rm -rf`. Rebuilt the image with `--no-cache`. Ran it again. Still crashed with the same error.

**Error:**
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) unable to open database file
```

**First impression:**
Thought it was fully fixed — removed the mount, deleted the directory, rebuilt. Couldn't understand why the error was identical.

**What was actually happening:**
The `todo.db` directory had already been baked into the image by `COPY . .` in the Dockerfile from a previous build. Even after deleting it on the host and removing the mount, the old image (or a cached layer) still contained that directory. A `docker system prune -f` was needed to remove all cached images before a clean rebuild.

Additionally, `.dockerignore` didn't list `todo.db` — so every build, if `todo.db` existed on the host (whether file or directory), it would be `COPY`'d into the image.

**Bug type:** Config — leftover artifact from a previous attempt + missing `.dockerignore` rule

**Fix:**
1. `docker-compose down -v && docker system prune -f` — clean everything out
2. `rm -rf todo.db` on the host — remove the artifact
3. Add `todo.db` to `.dockerignore` — prevent recurrence
4. Rebuild: `docker-compose build --no-cache && docker-compose up`

**Lesson:**
1. Artifacts from previous attempts can get baked into the image via `COPY . .`
2. `.dockerignore` is the line of defense — without it, any file/directory on the host can leak into the image
3. `--no-cache` rebuilds layers but does not remove old images. `docker system prune` is what actually cleans up.
4. When debugging "file not found" or "unable to open" → verify it's actually a real file (`ls -la`), don't just check that it exists.

---

## Key Takeaways

1. **Silent failures are more dangerous than crashes.** Scenario 1 had no error message — the app ran normally with old code. Scenarios 2–3 crashed visibly and were easier to debug. Guard against silent failures by verifying behavior, not just verifying "it runs."

2. **Docker exposes pre-existing problems; it doesn't create new ones.** The hardcoded database path (ISS-006) was not a Docker bug — Docker just made it obvious: the app wasn't portable. The missing `.dockerignore` rule (ISS-007) also wasn't Docker's fault — it revealed that the build process wasn't defensive.

3. **Every attempt leaves artifacts.** A failed bind mount creates a directory. A failed build creates a cached image. Debugging Docker means tracking artifacts from each previous attempt — not just looking at the current state.