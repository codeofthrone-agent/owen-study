# Repository Guidelines

## Project Structure & Module Organization
Configuration helpers live in `config/`, domain libraries in `libraries/`, and Robot suites in `tests/` using the same folder names. Shared keywords go in `resources/`, cross-suite data in `variables/`, and provisioning or calibration utilities in `scripts/`. Keep diagrams, troubleshooting guides, and specs inside `docs/` or `spec.md`, and co-locate each feature’s code, suite, docs, and configuration assets.

## Build, Test, and Development Commands
- `uv pip install -r requirements.txt` — install or update dependencies with the preferred resolver.
- `uv run robot tests/<suite_folder>/ --include smoke` — execute suites or targeted tag sets.
- `uv run pytest tests/` — run Python unit tests; add `--cov=libraries/<module>` when touching helper code.
- `uv run python scripts/quick_ipcam_test.py` — spot-check RTSP pipelines after detection changes.
- `uv run python libraries/switchbot_smartplug_control/plug_control.py status` — verify SwitchBot connectivity before merging.
`uv run` already manages virtualenvs; use `uv venv` only when CI requires explicit paths.

## Coding Style & Naming Conventions
Follow PEP 8 (4-space indents, docstrings on public APIs) and add typing hints to new or refactored modules. Robot keywords stay Title Case while suite filenames remain snake_case. Keep configuration keys lowercase_with_underscores, store hardware secrets only in `.env` templates or sanitized YAML, use `loguru` for structured logs, and extract shared constants into a local `constants.py` instead of duplicating values.

## Testing Guidelines
Each feature needs at least one Robot suite under the matching `tests/<domain>/` folder plus supporting keywords/resources. Add pytest coverage for new Python helpers or simulators and keep touched modules at ≥80%. Name suites `<area>_test.robot` or `_test.py`, document hardware dependencies in `Suite Setup`, and use `uv run robot --include smoke` for quick checks before running the entire directory ahead of releases.

## Commit & Pull Request Guidelines
Use the repo’s Conventional Commit flavor (`feat(robot-arm): ...`, `fix(ipcam): ...`) with imperative, ≤72-character subjects. Summarize calibration steps, scripts touched, and hardware requirements in the body plus any config migrations. Pull requests must link to issues/TestLink cases, list commands executed, and attach screenshots or logs for hardware features. Include doc or spec updates whenever behavior or wiring changed.

## Security & Configuration Tips
Keep RTSP credentials, SwitchBot tokens, and UART secrets inside `.env` files or sanitized YAML templates; redact values from logs. Run `uv run python scripts/validate_remote_uart_config.py` after touching serial settings and record IP/port changes in `config/migration_report.md`. Strip hostnames or macOS paths from shared artifacts and rotate device tokens used in demos.

## Subagents Tool Usage Priority
- **優先使用 Subagents 工具**：在執行複雜的文件處理、腳本編寫或系統操作時，應優先考慮使用 `shell`, `fs`, `scripting` 等專門的 subagents 工具。這些工具能更精確地處理大型文件與複雜邏輯，減少手動錯誤並提升自動化效率。

