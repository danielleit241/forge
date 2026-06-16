# Changelog

## 2.1.4

- Preserve files from the previous agent adapter during `migrate` instead of deleting the old `.claude`, `.codex`, `.agents`, `CLAUDE.md`, or `AGENTS.md` outputs.
- Merge generated toolkit paths into the project `.gitignore`, including agent folders, instruction files, lockfiles, `.ck.json`, and `session-data/`.
- Add `session-data/.gitignore` automatically and move runtime session state to root-level `session-data/` shared by supported agents.
- Improve Claude/Codex instruction migration by creating `@CLAUDE.md` or `@AGENTS.md` reference bridge files when project instructions already exist.
- Capture Codex user prompts through the migrated hook pipeline so session summaries include user messages, not only changed files.
- Align Codex sub-agent model rendering with Claude frontmatter and force the `scout` agent to `gpt-5.4-mini`.
- Replace the packaged `CLAUDE.md` template with concise behavioral guidelines focused on assumptions, simplicity, surgical edits, and verification.
- Update CK workflow skills, add the `ck-spec` skill, and include the upstream `agent-skills` reference as a tracked submodule for future migration work.

## 2.1.3

- Infer migration source from the lockfile so onboarding cannot select an agent that contradicts the installed toolkit.

## 2.1.2

- Add a colored, keyboard-driven onboarding wizard with selectable actions, agents, and bundles.
- Add `--project-root` for the current working directory and `--project-path` for automatic root discovery.
- Remove the nonexistent `.claude/contexts` package path that caused `ENOENT` during Claude installation.
- Make the test command portable across Windows and Linux CI runners.

## 2.1.1

- Correct the npm package scope to `@danielle241/my-skills`.

## 2.1.0

- Add interactive onboarding through `my-skills setup` and the default no-command flow.
- Add npm-registry based `update` and `revert` support for globally installed or `npx` usage.
- Merge existing `.claude` and `.codex` directory contents without deleting unrelated files.
- Deep-merge `.claude/settings.json`, `.codex/hooks.json`, and `.ck.json`.
- Read the CLI version from `package.json` to keep release metadata aligned.

## 2.0.1

- Align Codex migration output with current hooks, agent, and configuration behavior.

## 2.0.0

- Introduce the versioned toolkit CLI, lockfile, adapters, migrations, and transactional updates.
