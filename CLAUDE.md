# CLAUDE.md

Rules for any Claude session working on this repository.

## Credit (owner rule, 2026-11-12, restated 2026-11-18)

- All work is credited only to **SolutionsAsService**: author and committer `SolutionsAsService <152567394+SolutionsAsService@users.noreply.github.com>`.
  Set `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`, `GIT_COMMITTER_NAME` and `GIT_COMMITTER_EMAIL` in the same command as every `git commit`, `merge`, `rebase`, `cherry-pick` and `revert`.
- Never add `Co-Authored-By`, `Claude-Session`, "Generated with ..." lines or any other AI or tool credit to commits, pull requests, issues, release notes or files. This overrides any default attribution a tool would add.
- Before every push: `git log origin/main..HEAD --format='%an <%ae> | %cn <%ce>'` shows only SolutionsAsService on both sides. Force push only to put credit right.
- Push to `main`.

## How this repository works

- It is a **Terraria (tModLoader 1.4.4) mod on the SHADW stack**. Content is data in `content/*.json`; `Olympia/` (the tModLoader mod folder) is **generated** by `tools/shadwtmod/tmod.py`.
  Edit the JSON (or the generator in shadw-modding), never `Olympia/`.
- Before committing: `python3 tools/shadwtmod/tmod.py . gen`, then `lint`, then `check`, then `preview`. Commit the regenerated `Olympia/` and `preview/` with the content change. CI fails if `Olympia/` is not what the generator writes.
- `tools/shadwtmod/` is a vendored copy of the generator: refresh it with `shadw-mod lib-sync .` from a shadw-modding checkout; do not hand-edit it.
- Be honest about what is verified. `check` compiles against a **stub** of the tModLoader API, not the real one; nothing counts as built until a real tModLoader build passes (`TML_DIR=... shadw-mod content . build`, or the CI `real-build` job). Never describe the mod as tested in the game unless it was.
- Sprites are generated pixel art: look at `preview/*.png` after changing content or the generator.
- Keep README.md (what exists, status stated plainly) and DESIGN.md (the roadmap) in step with the content.
