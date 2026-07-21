import os
import requests

USERNAME = os.environ["GITHUB_USERNAME"]
TOKEN = os.environ["GH_TOKEN"]

README = "README.md"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
}

BAR_LENGTH = 20


def get_repositories():
    repos = []
    page = 1

    while True:
        url = (
            f"https://api.github.com/users/{USERNAME}/repos"
            f"?per_page=100&page={page}"
        )
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()

        data = r.json()
        if not data:
            break

        repos.extend(data)
        page += 1

    return repos


def get_languages(repo_name):
    url = f"https://api.github.com/repos/{USERNAME}/{repo_name}/languages"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()


def progress_bar(percent):
    filled = round((percent / 100) * BAR_LENGTH)
    return "█" * filled + "░" * (BAR_LENGTH - filled)


def build_section():
    totals = {}

    repos = get_repositories()

    for repo in repos:
        if repo.get("fork"):
            continue

        langs = get_languages(repo["name"])

        for lang, bytes_count in langs.items():
            totals[lang] = totals.get(lang, 0) + bytes_count

    total_bytes = sum(totals.values())

    if total_bytes == 0:
        return "No language statistics found."

    lines = []

    for lang, count in sorted(
        totals.items(),
        key=lambda x: x[1],
        reverse=True,
    ):
        pct = count / total_bytes * 100
        bar = progress_bar(pct)
        lines.append(f"{lang:<12} {bar} {pct:5.1f}%")

    return "```text\n" + "\n".join(lines) + "\n```"


def update_readme():
    with open(README, "r", encoding="utf-8") as f:
        content = f.read()

    start = "<!--START_SECTION:languages-->"
    end = "<!--END_SECTION:languages-->"

    new_block = (
        start
        + "\n\n"
        + build_section()
        + "\n\n"
        + end
    )

    s = content.index(start)
    e = content.index(end) + len(end)

    updated = content[:s] + new_block + content[e:]

    with open(README, "w", encoding="utf-8") as f:
        f.write(updated)


if __name__ == "__main__":
    update_readme()
