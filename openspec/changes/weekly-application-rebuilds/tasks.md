# Tasks

## 1. Schedule and documentation

- [x] 1.1 Move the application workflow schedule to Monday while keeping push, pull request and manual dispatch triggers.
- [x] 1.2 Update the repository, application and project documentation from daily to weekly application resolution without changing the runtime schedule.
- [x] 1.3 Keep the changed-input rule explicit: a date or unrelated repository change still produces no new image.

## 2. Checks

- [x] 2.1 Documentation rules and strict OpenSpec validation pass in the development container.
- [ ] 2.2 The triggered application run passes resolution, build, final-image, vulnerability and SBOM checks for a changed recipe.

## 3. Delivery

- [ ] 3.1 Confirm the weekly schedule is visible in the workflow and the next scheduled run is Monday UTC.
