# Phase 5 verification

Recorded on 9 November 2026 using Windows 11 x64 build 26200 and Python 3.12.14.

| Check | Result |
| --- | --- |
| Tokelo PR 2 before integration | 13 tests passed; merged as e1f3b27 |
| Final SQLite suite | 50 tests passed in 24.153 seconds |
| Final PostgreSQL 16.15 suite | 50 tests passed in 26.497 seconds |
| Fresh compiled EXE setup | Passed in a separate local data folder |
| Packaged HTTP login, lists, assets and searched CSV | Passed |
| Packaged SQLite backup/restore and restart | Passed |
| Upgrade from original 0001 and PR 0004 | Passed on SQLite; existing IDs and values retained |
| Two concurrent PostgreSQL lead conversions | Passed; one linked deal |
| PostgreSQL backup restored to separate database | Passed; company count and conversion retained |
| 500 fictional records, three route checks | All measured server-side responses below two seconds |
| Docker Desktop / Compose installation | Not run in this environment |
| Independent second Windows PC | Pending Ryan and Logan's evidence |
| Visual browser check at 1366 x 768 | Pending |
| Wi-Fi disconnected on a fresh PC | Pending; bundled assets verified locally |

The performance measurements use Django's test client, so they exclude browser
rendering and real network latency. The portable application was checked through
real HTTP requests to the compiled server. A clean Windows VM was not available.

Changes from Phase 4: optional SQLite portable mode, locally bundled Bootstrap,
Django 5.2 LTS, Waitress startup, backup/restore commands and data preflight. The
PostgreSQL source option and core CRM scope remain. No result here establishes a
public-production security or universal compatibility claim.

Packaging defects found and fixed: missing WhiteNoise middleware in the first build;
Windows database restore held an open SQLite connection. Both were corrected and
the compiled package was retested. Staff admin also uses the normal LeadForm so it
cannot manually bypass conversion by selecting Converted on a new lead.

Member draft inputs informed the corresponding designs. Tokelo's PR is preserved
in Git history. AI assisted integration and local execution. A design assignment
does not establish that a member wrote every related line or executed a test.
