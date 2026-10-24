# Tasks

## 1. Schedule and documentation

- [x] 1.1 Move the application workflow schedule to Monday while keeping push, pull request and manual dispatch triggers.
- [x] 1.2 Update the repository, application and project documentation from daily to weekly application resolution without changing the runtime schedule.
- [x] 1.3 Keep the changed-input rule explicit: a date or unrelated repository change still produces no new image.

## 2. Checks

- [x] 2.1 Documentation rules and strict OpenSpec validation pass in the development container.
- [x] 2.2 The triggered application run (`40126966154`) passed resolution, build, final-image, vulnerability and SBOM checks for the changed recipe.

## 3. Delivery

- [x] 3.1 The workflow schedule is `30 3 * * 1`, the next scheduled application run is Monday 03:30 UTC, and the push run passed.
