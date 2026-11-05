import json
import os
import urllib.request
from xml.sax.saxutils import escape

USERNAME = "Eduardodev065"
API = "https://api.github.com"
COLORS = ["#f1e05a", "#3572A5", "#e34c26", "#563d7c", "#3178c6", "#663399", "#4F5D95", "#89e051", "#00ADD8", "#dea584"]


def get_json(url):
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-language-card"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def collect_languages():
    totals = {}
    page = 1
    while True:
        repos = get_json(f"{API}/users/{USERNAME}/repos?type=owner&per_page=100&page={page}")
        for repo in repos:
            if repo.get("fork") or repo.get("archived"):
                continue
            languages = get_json(repo["languages_url"])
            for language, byte_count in languages.items():
                totals[language] = totals.get(language, 0) + byte_count
        if len(repos) < 100:
            break
        page += 1
    return sorted(totals.items(), key=lambda item: (-item[1], item[0]))


def make_svg(languages):
    width = 520
    height = 177
    total = sum(value for _, value in languages)
    if not total:
        languages = [("Sem dados ainda", 1)]
        total = 1
    shown = languages[:8]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Tecnologias</title>',
        '<desc id="desc">Linguagens somadas dos repositórios públicos ativos de Eduardo.</desc>',
        '<rect width="520" height="177" rx="12" fill="#0d1117" stroke="#30363d"/>',
        '<text x="24" y="31" fill="#79c0ff" font-family="Segoe UI,Arial,sans-serif" font-size="16" font-weight="700">Tecnologias</text>',
        '<text x="496" y="31" text-anchor="end" fill="#8b949e" font-family="Segoe UI,Arial,sans-serif" font-size="11">Repositórios públicos</text>',
        '<rect x="24" y="45" width="472" height="10" rx="5" fill="#21262d"/>',
    ]
    x = 24.0
    for index, (language, value) in enumerate(shown):
        segment = 472 * value / total
        if segment > 0.5:
            parts.append(f'<rect x="{x:.2f}" y="45" width="{segment:.2f}" height="10" fill="{COLORS[index % len(COLORS)]}"/>')
        x += segment
    for index, (language, value) in enumerate(shown):
        column = index % 2
        row = index // 2
        x = 24 + column * 240
        y = 79 + row * 22
        color = COLORS[index % len(COLORS)]
        percent = value / total * 100
        parts.extend([
            f'<circle cx="{x + 4}" cy="{y - 4}" r="4" fill="{color}"/>',
            f'<text x="{x + 14}" y="{y}" fill="#c9d1d9" font-family="Segoe UI,Arial,sans-serif" font-size="12">{escape(language)}</text>',
            f'<text x="{x + 218}" y="{y}" text-anchor="end" fill="#8b949e" font-family="Segoe UI,Arial,sans-serif" font-size="12">{percent:.2f}%</text>',
        ])
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    svg = make_svg(collect_languages())
    with open("tecnologias.svg", "w", encoding="utf-8", newline="\n") as card:
        card.write(svg)
