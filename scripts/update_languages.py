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

        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        data = response.json()

        if not data:
            break

        repos.extend(data)
        page += 1

    return repos


def get_languages(repo_name):
    url = f"https://api.github.com/repos/{USERNAME}/{repo_name}/languages"

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    return response.json()


def progress_bar(percent):
    filled = round((percent / 100) * BAR_LENGTH)
    return "█" * filled + "░" * (BAR_LENGTH - filled)


def build_language_section():
    totals = {}

    for repo in get_repositories():
        if repo.get("fork"):
            continue

        languages = get_languages(repo["name"])

        for language, byte_count in languages.items():
            totals[language] = totals.get(language, 0) + byte_count

    total_bytes = sum(totals.values())

    if total_bytes == 0:
        return "```text\nNo language statistics found.\n```"

    lines = []

    for language, byte_count in sorted(
        totals.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        percent = byte_count / total_bytes * 100
        bar = progress_bar(percent)

        lines.append(
            f"{language:<12} {bar} {percent:5.1f}%"
        )

    return "```text\n" + "\n".join(lines) + "\n```"


def replace_section(content, start, end, replacement):
    start_index = content.index(start)
    end_index = content.index(end) + len(end)

    new_block = (
        start
        + "\n\n"
        + replacement
        + "\n\n"
        + end
    )

    return (
        content[:start_index]
        + new_block
        + content[end_index:]
    )


def update_readme():
    with open(README, "r", encoding="utf-8") as file:
        content = file.read()

    language_section = build_language_section()

    content = replace_section(
        content,
        "<!--START_SECTION:languages-->",
        "<!--END_SECTION:languages-->",
        language_section,
    )

    with open(README, "w", encoding="utf-8") as file:
        file.write(content)


if __name__ == "__main__":
    update_readme()
