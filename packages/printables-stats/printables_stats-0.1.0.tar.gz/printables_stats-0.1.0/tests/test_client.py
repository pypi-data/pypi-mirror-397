import unittest
from unittest.mock import MagicMock, patch
from printables_stats import PrintablesClient


class TestPrintablesClient(unittest.TestCase):
    def test_parse_stats_success(self):
        client = PrintablesClient()
        html = """
        <html>
            <body>
                <div class="stats-row">
                    <i class="fa-arrow-down-to-line"></i><span class="count">1.2k</span>
                    <i class="fa-heart"></i><span class="count">500</span>
                    <button class="t"><span class="count">100</span> followers</button>
                    <button class="t"><span class="count">5</span> Following</button>
                </div>
                <div class="attribute-row">
                    <i class="fa-calendar-days"></i> <div>Joined in January 1, 2020</div>
                </div>
                <ul class="nav">
                    <li><a href="/user/models"><small>42</small></a></li>
                </ul>
                <div class="badges-list">
                    <div class="badge-item"><strong>Designer 1: Newcomer</strong></div>
                    <div class="badge-item"><strong>Maker 4: Skilled</strong></div>
                    <div class="badge-item"><strong>Printables Maniac</strong></div>
                </div>
            </body>
        </html>
        """
        stats = client.parse_stats(html)
        self.assertEqual(stats["downloads"], 1200)
        self.assertEqual(stats["likes"], 500)
        self.assertEqual(stats["followers"], 100)
        self.assertEqual(stats["following"], 5)
        self.assertEqual(stats["joined_date"], "January 1, 2020")
        self.assertEqual(stats["models_count"], 42)
        self.assertEqual(
            stats["badges"], {"Designer": 1, "Maker": 4, "Printables Maniac": 1}
        )

    @patch("requests.Session.get")
    def test_get_user_stats_network(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = (
            "<html></html>"  # Minimal HTML, parse_stats handles missing gracefully
        )
        mock_get.return_value = mock_response

        client = PrintablesClient()
        stats = client.get_user_stats("@testuser")
        self.assertIsNotNone(stats)


if __name__ == "__main__":
    unittest.main()
