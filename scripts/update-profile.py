#!/usr/bin/env python3
"""Generate repository-owned cards and a short public activity log. Stdlib only."""
import datetime as dt
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
USER = os.environ.get('PROFILE_USER', 'solfany')
if not re.fullmatch(r'[A-Za-z0-9-]+', USER):
    raise ValueError('Invalid GitHub username')


def api(path):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'solfany-profile',
               'X-GitHub-Api-Version': '2022-11-28'}
    if os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request('https://api.github.com' + path,
                                                          headers=headers), timeout=30) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def markdown(value):
    # Escape API-provided text, including Markdown punctuation and HTML.
    return re.sub(r'([\\`*_{}\[\]()#+.!|<>~-])', r'\\\1', str(value).replace('\n', ' '))


def generate():
    repos = []
    for page in range(1, 101):
        batch = api(f'/users/{USER}/repos?per_page=100&page={page}')
        repos.extend(batch)
        if len(batch) < 100:
            break
    owned = [r for r in repos if not r['fork']]
    stars = sum(r['stargazers_count'] for r in owned)
    languages = sorted({r['language'] for r in owned if r.get('language')})
    now = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')
    cards = {}
    for mode in ('light', 'dark'):
        dark = mode == 'dark'
        bg, ink, muted, border = (('#2e2a41', '#f7edf8', '#c7b9d7', '#746087') if dark else
                                 ('#fffaf4', '#514262', '#756381', '#c4afd4'))
        cells = ''
        for x, value, label in ((34, len(owned), 'PUBLIC REPOS'), (305, stars, 'STARS RECEIVED'),
                                (575, len(languages), 'MAIN LANGUAGES')):
            cells += (f'<text x="{x}" y="72" font-size="32" font-weight="bold">{value}</text>'
                      f'<text x="{x}" y="104" font-size="14" fill="{muted}">{label}</text>')
        cards[mode] = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 162" role="img" aria-labelledby="title desc">
<title id="title">Solfany public player stats</title><desc id="desc">{len(owned)} public non-fork repositories; {stars} stars received; {len(languages)} distinct primary repository languages. Updated {now} UTC.</desc>
<rect x="1" y="1" width="838" height="160" rx="6" fill="{bg}" stroke="{border}"/>
<g font-family="ui-monospace,Consolas,monospace" fill="{ink}">{cells}
<text x="34" y="139" font-size="12" fill="{muted}">PUBLIC · non-fork repositories · saved {now} UTC</text></g></svg>'''

    for mode in ('light', 'dark'):
        mobile = cards[mode].replace('0 0 840 162', '0 0 420 300')
        mobile = mobile.replace('width="838" height="160"', 'width="418" height="298"')
        mobile = mobile.replace('x="305" y="72"', 'x="34" y="148"').replace('x="305" y="104"', 'x="34" y="176"')
        mobile = mobile.replace('x="575" y="72"', 'x="34" y="224"').replace('x="575" y="104"', 'x="34" y="252"')
        mobile = mobile.replace('y="139"', 'y="282"').replace('PUBLIC · non-fork repositories · saved', 'PUBLIC · saved')
        cards[mode + '-mobile'] = mobile

    events = api(f'/users/{USER}/events/public?per_page=100')
    activity, seen = [], set()
    verbs = {'PushEvent': 'Pushed to', 'CreateEvent': 'Created in', 'PullRequestEvent': 'Updated a pull request in',
             'IssuesEvent': 'Updated an issue in', 'ReleaseEvent': 'Released in', 'ForkEvent': 'Forked',
             'IssueCommentEvent': 'Commented in', 'PullRequestReviewEvent': 'Reviewed in'}
    for event in events:
        name, kind = event['repo']['name'], event['type']
        if kind not in verbs or name.lower() == f'{USER}/{USER}'.lower():
            continue  # Keep automated profile refreshes out of the activity log.
        if not name.lower().startswith(USER.lower() + '/'):
            continue  # Do not imply ownership of other people's repositories.
        key = (name, kind)
        if key in seen:
            continue
        seen.add(key)
        activity.append(f"- `{event['created_at'][:10]}` {verbs[kind]} [{markdown(name)}](https://github.com/{name}).")
        if len(activity) == 4:
            break
    if not activity:
        activity = [f'No recent public project events in GitHub’s activity feed. [Explore my repositories →](https://github.com/{USER}?tab=repositories)']
    activity.append(f'\n<sub>Public GitHub activity · refreshed {now} UTC</sub>')
    readme = ROOT / 'README.md'
    current = readme.read_text()
    updated, count = re.subn(r'<!-- activity:start -->.*?<!-- activity:end -->',
                            lambda _: '<!-- activity:start -->\n' + '\n'.join(activity) + '\n<!-- activity:end -->',
                            current, flags=re.S)
    if count != 1:
        raise ValueError('Expected exactly one activity marker block')
    # Fetch everything before replacing anything. API failure leaves the saved images intact.
    for mode, svg in cards.items():
        (ROOT / 'assets' / f'stats-{mode}.svg').write_text(svg)
    readme.write_text(updated)
    print(f'Generated profile cards from {len(owned)} public non-fork repositories.')


if __name__ == '__main__':
    generate()
