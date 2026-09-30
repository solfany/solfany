# Solfany profile assets

The header, stat cards and footer are original SVG artwork for this profile. Cream,
lavender and dusty pink form a small retro desktop; the cat appears only at the end.
All README images are stored in this repository. Headers include a readable mobile
variant and respect reduced-motion preferences.

## Automation

| Workflow | Schedule (UTC / KST) | Output |
| --- | --- | --- |
| `profile-3d.yml` | 18:00 / 03:00 next day | Existing `profile-3d-contrib/` garden |
| `stats.yml` | 19:17 / 04:17 next day | Public stat cards and four recent events |
| `snake.yml` | 19:37 / 04:37 next day | Two contribution snake SVGs |

All three also support **Actions → workflow → Run workflow**. Enable GitHub Actions
and allow these actions in repository/organization policy. No extra secret is
required: all workflows use the automatically provided `GITHUB_TOKEN`.
Job-level `contents: write` saves generated assets; default permission is read-only.
If branch protection forbids bot pushes, permit the workflow bot under your policy
or change the publication strategy before enabling the schedules.

The former `TOKEN` secret is no longer referenced. Do not delete it without checking
whether another repository uses it. Private-repository statistics are intentionally
not collected. There are no push triggers, so generated commits cannot recursively
run these workflows. A shared concurrency group serializes the three writers, and
each commit stages only its own output files. Unchanged files do not cause a commit.
Failed refreshes leave the previous committed images available.

## Data definitions

Player Stats counts public, non-fork repositories; stars received by those repos;
and distinct primary languages reported by GitHub for those repos. It is not a
language percentage, private contribution count or artificial developer score.
Recent Activity uses GitHub's limited public events feed, with up to four distinct
project/type pairs. Profile refresh events and repos not owned by Solfany are
excluded. Dates and refresh stamps are UTC. An empty feed is stated explicitly.

Initial Snake SVGs were generated with the official Platane/snk v3 generator from
Solfany's public contribution calendar on 2026-09-30; future refreshes use the
standard token-backed Action. The original rainbow 3D SVG is preserved unchanged
until its next successful workflow refresh. Historical Actions runs were not
available in the public API at implementation time, so its prior health was not
assumed.

## Decisions and official references (checked 2026-09-30)

- [Platane/snk](https://github.com/Platane/snk): SVG-only v3, custom palettes.
- [3D Contrib v0.9.3](https://github.com/yoshi389111/github-profile-3d-contrib/releases/tag/v0.9.3): Node 24, default token supported.
- [actions/checkout v7](https://github.com/actions/checkout/releases): current stable major on GitHub-hosted runners.
- [GitHub Readme Stats](https://github.com/stats-organization/github-readme-stats): upstream recommends repository-generated cards or self-hosting over the best-effort public instance. This profile uses a small local Python generator for its own visual style; no public Stats endpoint is embedded.
- [Metrics](https://github.com/lowlighter/metrics): considered, omitted to avoid another visual system and its personal-token requirement.
- [Streak Stats](https://github.com/DenverCoder1/github-readme-streak-stats): still maintained when checked; omitted because the existing garden and snake already represent consistency without another hosted service.
- Typing SVG: replaced with a subtle animated local status light.

Promfeed's public site was verified. WMS, Solfany Store and Solfany Portal have no
unverified repository/site links. Quest states describe current work, not an API
status monitor.

Run `python3 scripts/update-profile.py` to refresh public cards locally; optionally
provide `GITHUB_TOKEN` through the environment to increase the API rate limit.
