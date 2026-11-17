# Lab queue

Run the supplied tests without Docker:

```sh
cd part2
python -m pip install -r requirements-dev.txt
pytest
```

The runtime uses only Python 3.12's standard library. Responses are plain
UTF-8 text with Content-Length. POST /join takes a JSON object with a name;
GET /health returns ok and POST /next removes the first person.

```sh
cp .env.example .env
# First stage: one app, host port taken from APP_PORT.
docker compose -f compose.single.yaml up -d --build
# Stop containers, keeping the named volume before changing topology.
docker compose -f compose.single.yaml down
# Final stage: shared queue, three apps, proxy publishes APP_PORT.
docker compose up -d --build --scale app=3
# nginx resolves app at startup. Restart after recreating/scaling app.
docker compose restart proxy
```

Import postman/lab-queue.postman_collection.json into Postman; update its
baseUrl if APP_PORT differs from 8000. Run health, join, invalid join, next,
then next empty. Do not run concurrent experiments on a queue with real data.

On a separate empty experimental queue:

```sh
python tools/concurrent_join.py --url http://localhost:8000 --drain
```

The queue volume and lock file must be shared by all replicas. Do not remove
queue.lock while apps are running. Container deletion preserves the volume;
`docker compose down -v` deletes it and its queue. Never retry a timed-out
mutation automatically: its result may already have been committed.

The unsafe implementation is retained in Git history for comparison. The
final implementation locks the entire read/change/write/result operation.

CI checks all branches and main pull requests. Only a push to main publishes
images and Pages and creates an annotated release tag. The build artifact
is transferred to the push job, so no second image build occurs. A release
name uses the UTC commit timestamp and 12-character SHA. Reruns reuse the
same name; existing tags must resolve to the same commit. Tag pushes are
excluded by the branch-only event filter, including when using a PAT.

Configure GitHub Pages source as GitHub Actions. Images are published to
`ghcr.io/<owner>/lab-queue`; make the package public after its first push.
The separate manual workflow accepts an existing Git tag, validates it,
and publishes that tag's sentence and version without making a commit.
Both Pages jobs share the pages-publication concurrency group. They cannot
deploy simultaneously; the last completed deployment controls the one site.
GitHub concurrency is not a FIFO queue and may replace pending runs.
