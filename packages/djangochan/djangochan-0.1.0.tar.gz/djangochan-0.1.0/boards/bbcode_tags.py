from precise_bbcode.bbcode.tag import BBCodeTag
from precise_bbcode.tag_pool import tag_pool


class SpoilerTag(BBCodeTag):
    name = 'spoiler'
    definition_string = '[spoiler]{TEXT}[/spoiler]'
    format_string = '<span class="spoiler">{TEXT}</span>'


tag_pool.register_tag(SpoilerTag)
