**As the system**,
I want a persistent /data directory,
So that imported files survive container restarts.

**Acceptance criteria**
- /data mounted as volume 
- App can read/write test files there
- Path configurable via env (DATA_DIR)
