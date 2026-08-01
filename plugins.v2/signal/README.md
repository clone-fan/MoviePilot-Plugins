# Signal Plugin

This directory is the editable MoviePilot plugin source. It is published only through the project build and artifact workflow; `dist`, dependencies, staging payloads, and reports do not belong here.

Use the project atlas before changing source:

- Configuration center: `docs/ai/project-atlas.json` route `frontend-config`
- Dashboard: route `frontend-dashboard`
- MoviePilot host contract: route `backend-contract` or `plugin-contract`
- Build and publish: routes `build`, `publish`, and `preflight`

The component composition root is `__init__.py`; frontend federation entry is `src/main.js`; Vite contract is `vite.config.js`.
