"""
Default sample configuration used by the bootstrap command.
"""

SITE_TITLE = "djangochan"
SITE_DESCRIPTION = "after the showers the sun will be shining"
SITE_ISSUE = "Under development. Server will be reset daily at midnight."
SITE_DOMAIN = "localhost"

# slug -> name
BOARDS = {
    "meta": "meta",
    "rand": "random",
    "math": "mathematics",
    "phys": "physics",
    "prog": "programming",
    "tech": "technology",
    "anime": "anime",
}

BOARD_DESCRIPTIONS = {
    "meta": "Meta discussion",
    "rand": "Anything",
    "math": "Mathematics",
    "phys": "Physics",
    "prog": "Programming",
    "tech": "Technology",
    "anime": "Anime & Manga",
}
