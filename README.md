# Cloud Computing HW2

Part 1 contains the four-line program, full/slim Dockerfiles, the original
Dockerfile for comparison, and fake-secret layer inspection tools. Run
builds from part1; run the secret experiment from part1/secrets. The secret
is deliberately fake and must never be replaced by a real credential.

Part 2 contains the lab queue. See part2/README.md for tests, single-replica
Compose, the final three-replica proxy topology, and concurrency tools.
Only the final app/ implementation is included in the runtime image.

The unsafe queue used in the race experiment is preserved at commit
1834e85 and as part2/experiments/queue_unsafe.py so it can also be inspected
in a source archive without Git history. The corrected code uses a shared
stable lock file and atomic replacement. The supplied tests are unchanged.

The workflows in .github/workflows are prepared and validated locally.
Public GitHub/Pages/GHCR runs have not been performed. Publishing is a
separate step; the current code contains no account tokens or passwords.
The report records actual local experiments and identifies pending public
release evidence explicitly. The two optional bonus sections are omitted.
