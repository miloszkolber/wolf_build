# Weekly application rebuilds

## Why

The Steam and Heroic images are immutable inputs with independent identities. A daily scheduled resolution of distribution packages and the Heroic release produces new application images on ordinary package churn, while the applications, their recipes and their base digests change far less often. Weekly resolution keeps security and release discovery without the extra build and publication churn.

## What changes

- Run the application workflow weekly on Monday at the existing UTC time instead of daily. Source changes, pull requests and manual dispatch still trigger it immediately.
- Keep the runtime workflow daily; runtime sources, the Intel media stack and the streaming payload have a different change cadence.
- Keep the existing selection rule: only changed base, recipe, application release or resolved package closure produces a new image; unchanged inputs reuse and rescan the existing immutable image.

## Capabilities

Modified capability: `application-images`.

## Status and authority

Implementation and repository checks are authorized. Publication is automatic through the existing application workflow; deployment remains separate.

## Consequential unknowns

A retired distribution package version can now be noticed up to a week later by scheduled discovery. Source changes and manual dispatch still resolve immediately, and assembly continues to fail rather than float to an unrecorded version.
