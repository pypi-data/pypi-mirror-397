import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime


class PrintablesClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        self.base_url = "https://www.printables.com"

    def get_user_stats(self, user_id):
        """
        Get public stats for a user.

        Args:
            user_id (str): The user identifier (e.g. '@username_1234567').

        Returns:
            dict: Dictionary containing user stats (downloads, followers, etc.) or None if failed.
        """
        if not user_id.startswith("@"):
            user_id = f"@{user_id}"

        try:
            url = f"{self.base_url}/{user_id}"
            response = self.session.get(url)
            response.raise_for_status()

            return self.parse_stats(response.text)

        except Exception as e:
            print(f"Error fetching user stats: {e}")
            return None

    def parse_stats(self, html_content):
        """
        Parse user stats from HTML content.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        stats = {}

        try:
            downloads_icon = soup.select_one(".fa-arrow-down-to-line")
            if downloads_icon:
                count_span = downloads_icon.find_next_sibling("span", class_="count")
                if count_span:
                    stats["downloads"] = self._parse_int(count_span.get_text())

            likes_icon = soup.select_one(".fa-heart")
            if likes_icon:
                count_span = likes_icon.find_next_sibling("span", class_="count")
                if count_span:
                    stats["likes"] = self._parse_int(count_span.get_text())

            for btn in soup.select("button.t"):
                text = btn.get_text()
                if "followers" in text.lower():
                    count_span = btn.select_one(".count")
                    if count_span:
                        stats["followers"] = self._parse_int(count_span.get_text())
                elif "following" in text.lower():
                    count_span = btn.select_one(".count")
                    if count_span:
                        stats["following"] = self._parse_int(count_span.get_text())

            calendar_icon = soup.select_one(".fa-calendar-days")
            if calendar_icon:
                joined_div = calendar_icon.find_next_sibling("div")
                if joined_div:
                    date_text = joined_div.get_text(strip=True).replace(
                        "Joined in ", ""
                    )
                    try:
                        stats["joined_date"] = datetime.strptime(
                            date_text, "%B %d, %Y"
                        ).strftime("%Y-%m-%d")
                    except ValueError:
                        stats["joined_date"] = date_text

            models_link = soup.select_one('a[href$="/models"]')
            if models_link:
                small_tag = models_link.select_one("small")
                if small_tag:
                    stats["models_count"] = self._parse_int(small_tag.get_text())

            level_elem = soup.select_one(".level")
            if level_elem:
                level_text = level_elem.get_text(strip=True)
                match = re.search(r"(\d+)", level_text)
                if match:
                    stats["level"] = int(match.group(1))

            badges = {}
            json_badges_found = False
            scripts = soup.find_all("script")
            for s in scripts:
                if s.string and "badgesSelection" in s.string:
                    try:
                        data = json.loads(s.string)
                        if "body" in data:
                            body_json = json.loads(data["body"])
                            if "data" in body_json and "user" in body_json["data"]:
                                badges_sel = body_json["data"]["user"][
                                    "badgesSelection"
                                ]
                                for b in badges_sel:
                                    if "badge" in b and "userLevel" in b:
                                        category = b["badge"]["name"]
                                        if (
                                            b["userLevel"]
                                            and "badgeLevel" in b["userLevel"]
                                        ):
                                            level = b["userLevel"]["badgeLevel"][
                                                "level"
                                            ]
                                            badges[category] = level
                                        else:
                                            badges[category] = 1
                                json_badges_found = True
                                break
                    except Exception:
                        continue
                if json_badges_found:
                    break

            if not badges:
                badges_list = soup.select(".badges-list .badge-item strong")
                if badges_list:
                    for badge_strong in badges_list:
                        text = badge_strong.get_text(separator=" ", strip=True)
                        match = re.search(r"^(.*?)\s+(\d+):\s+(.*)$", text)
                        if match:
                            category = match.group(1).strip()
                            level = int(match.group(2))
                            badges[category] = level
                        else:
                            badges[text] = 1

            if not badges:
                for badge_name in soup.select(".badges .name"):
                    name = badge_name.get_text(strip=True)
                    badges[name] = 1

            stats["badges"] = badges

            return stats

        except Exception as e:
            print(f"Error parsing stats: {e}")
            return None

    def _parse_int(self, text):
        """Helper to parse integers like '1.2k' or '195'"""
        if not text:
            return 0
        text = text.strip().lower()
        multiplier = 1
        if text.endswith("k"):
            multiplier = 1000
            text = text[:-1]
        elif text.endswith("m"):
            multiplier = 1000000
            text = text[:-1]

        try:
            return int(float(text.replace(",", "")) * multiplier)
        except ValueError:
            return 0
