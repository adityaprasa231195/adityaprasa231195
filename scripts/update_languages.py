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


def build_sections():
    totals = {}
    c_bytes = 0
    c_repositories = 0

    repos = get_repositories()

    for repo in repos:
        if repo.get("fork"):
            continue

        langs = get_languages(repo["name"])

        if "C" in langs:
            c_repositories += 1
            c_bytes += langs["C"]

        for lang, bytes_count in langs.items():
            totals[lang] = totals.get(lang, 0) + bytes_count

    total_bytes = sum(totals.values())

    if total_bytes == 0:
        return "No language statistics found.", "No C statistics found."

    # Language section
    language_lines = []

    for lang, count in sorted(
        totals.items(),
        key=lambda x: x[1],
        reverse=True,
    ):
        pct = count / total_bytes * 100
        bar = progress_bar(pct)
        language_lines.append(f"{lang:<12} {bar} {pct:5.1f}%")

    language_section = (
        "```text\n"
        + "\n".join(language_lines)
        + "\n```"
    )

    # C section
    c_percent = (c_bytes / total_bytes * 100) if total_bytes else 0

    c_section = (
        "```text\n"
        "C Programming Statistics\n\n"
        f"C Repositories : {c_repositories}\n"
        f"Total C Bytes  : {c_bytes:,}\n"
        f"C Share        : {c_percent:.2f}%\n"
        "```"
    )

    return language_section, c_section


def replace_section(content, start, end, body):
    new_block = f"{start}\n\n{body}\n\n{end}"

    s = content.index(start)
    e = content.index(end) + len(end)

    return content[:s] + new_block + content[e:]


def update_readme():
    with open(README, "r", encoding="utf-8") as f:
        content = f.read()

    language_section, c_section = build_sections()

    content = replace_section(
        content,
        "<!--START_SECTION:languages-->",
        "<!--END_SECTION:languages-->",
        language_section,
    )

    content = replace_section(
        content,
        "<!--START_SECTION:c-programming-->",
        "<!--END_SECTION:c-programming-->",
        c_section,
    )

    with open(README, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    update_readme()
