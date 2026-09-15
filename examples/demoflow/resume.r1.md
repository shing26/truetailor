# Dana Whitfield - Backend Engineer (Pittsburgh)

Fictional résumé written for this repo's demo. Every name, company and
number below is invented; any resemblance to a real person is accidental.

## Contact
- dana.whitfield@example.com | github.com/example/dana-w

## Skills
- Python, FastAPI, PostgreSQL, Redis, Docker
- Load testing with Locust wired into CI on GitHub Actions, so capacity regressions surface before a release instead of after it.
- Structured logging, alerting on-call rotation

## Experience
### Northwind Freight - Backend Engineer (2022–2025)
- Own the shipment tracking service end to end (FastAPI + PostgreSQL): 4,000 dispatchers a day, intake through incident and on-call.
- Cut p95 tracking lookup from 780 ms to 210 ms with a Redis read cache and a rewritten PostgreSQL query plan, then held that SLO through the on-call rotation.
- Carried 6 services through the on-call rotation and rewrote 11 runbooks into the paths the team actually follows at 3 a.m.
- Shipped a rate limiter that kept the intake API alive through a 3x traffic spike during a regional storm.

### Bluefin Health - Junior Developer (2020–2022)
- Built ETL jobs that moved 2 million claim rows per night into the analytics warehouse.
- Wrote the appointment reminder service in Python; 98% delivery rate on a 350k monthly volume.

## Projects
- **pause-review**: CLI that buffers code-review notes and re-surfaces them after a merge conflict; 240 GitHub stars.

## Education
- B.S. Computer Science, University of Pittsburgh, 2020
