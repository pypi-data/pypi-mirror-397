import re
from markdownify import markdownify


def to_markdown(html):
    result = markdownify(html, heading_style='ATX', bullets='-')

    subs = [
        # empty line before headings
        (r'([^\n])\n(#+) ', r'\1\n\n\2 '),

        # quote blocks
        (r'^>\s{2,}(?=.)', r'> ', re.M),
        (r'(^> *\n)+^$', '\n', re.M),
        (r'(^\n)+(^> *\n)+', r'\1', re.M),

        # code blocks
        (r'''^\[sourcecode\b.*\blanguage=['"](\w+)['"].*\]''', r'```\1', re.M),
        (r'^\[/sourcecode\]$', r'```', re.M),
        (r'(?!^$)(^.*$)(\n```.+$)', r'\1\n\2', re.M),

        # white space
        (r'(\n{2,})', '\n\n'),
        (r'([^ ]) $', r'\1', re.M),
        (r'([^\n])$', r'\1\n'),
    ]

    for sub in subs:
        result = re.sub(sub[0], sub[1], result,
                        flags=sub[2] if len(sub) > 2 else 0)

    return result
