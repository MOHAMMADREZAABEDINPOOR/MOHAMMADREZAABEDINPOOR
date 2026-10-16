"""Refresh README badges from GitHub. Uses only Python's standard library."""
import json
import os
from html import escape
from pathlib import Path
from urllib.request import Request, urlopen

OWNER = 'MOHAMMADREZAABEDINPOOR'
REPOSITORIES = ['PIMX_PASS_DNS', 'PIMX_MOJI', 'PIMX_MORPH', 'PIMX_NODE', 'PIMX_WIDE']
OUTPUT = Path(__file__).resolve().parents[1] / 'assets/readme'


def get(path):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'PIMX-readme-stats'}
    if os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    with urlopen(Request('https://api.github.com' + path, headers=headers), timeout=30) as response:
        return json.load(response)


def badge(filename, title, fields):
    labels = [title] + [f'{label}: {value}' for label, value in fields]
    widths = [max(90, len(label) * 7 + 24) for label in labels]
    total = sum(widths)
    elements = []
    left = 0
    for index, (label, width) in enumerate(zip(labels, widths)):
        color = '#202936' if index == 0 else '#151923'
        text_color = '#ffffff' if index == 0 else '#a9c6ff'
        elements.append(f'<rect x="{left}" width="{width}" height="26" fill="{color}"/>')
        elements.append(f'<text x="{left + width / 2}" y="17" text-anchor="middle" fill="{text_color}">{escape(label)}</text>')
        left += width
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="26" viewBox="0 0 {total} 26" role="img" aria-label="{escape("; ".join(labels), quote=True)}"><title>{escape("; ".join(labels))}</title><g font-family="Verdana,DejaVu Sans,sans-serif" font-size="11">{"".join(elements)}</g></svg>\n'
    (OUTPUT / filename).write_text(svg, encoding='utf-8', newline='\n')


def main():
    # Fetch everything before writing so API failures leave the checked-in badges intact.
    user = get(f'/users/{OWNER}')
    records = []
    for repo in REPOSITORIES:
        data = get(f'/repos/{OWNER}/{repo}')
        commit = get(f'/repos/{OWNER}/{repo}/commits/{data["default_branch"]}')
        # open_issues_count includes pull requests; keep the displayed label accurate.
        records.append((repo, data, commit['commit']['committer']['date'][:10]))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for repo, data, date in records:
        badge(f'live-{repo}.svg', repo.replace('_', ' '), [('stars', data['stargazers_count']), ('issues + PRs', data['open_issues_count']), ('commit', date)])
    badge('live-profile.svg', 'PIMX / GITHUB', [('public repos', user['public_repos']), ('followers', user['followers'])])
    print(f'Refreshed {len(records)} project badges and profile stats.')


if __name__ == '__main__':
    main()
