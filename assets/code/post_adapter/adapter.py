import markdown

from config import *
from utils import *

logger = logging.getLogger(__name__)


class BaseAdapter:
    def __init__(self):
        self.is_wrapped_display = False

    def adapt_display_math(self, string):
        # ensure align environment is wrapped with `$$`
        if '$$' in string or string.startswith('```'):
            self.is_wrapped_display = not self.is_wrapped_display
        elif string.startswith(r'\begin{align') and not self.is_wrapped_display:
            string = '$$\n' + string
        elif string.startswith(r'\end{align') and not self.is_wrapped_display:
            assert string.endswith('\n')
            string = string + '$$\n'
        return string

    @staticmethod
    def adapt_escape(string, mode='link'):
        # https://stackoverflow.com/questions/6116978/how-to-replace-multiple-substrings-of-a-string
        # https://stackoverflow.com/questions/18737863/passing-a-function-to-re-sub-in-python
        if mode == 'link':
            # [desc|xx](link) -> [desc\|xx](link)
            pattern = r'(\[.*?\|.*?\])\(.*?\)'
            rep = {r'|': r'\|'}
        else:
            # inline-math
            # \{xx\} -> \\{xx\\}
            pattern = r'\$(.*?)\$'
            rep = {
                r'\{': r'\\{',
                r'\}': r'\\}',
                r'^*': r'^\ast',
                r'\#': r'\\#',
            }
        new_strings = []
        pos = 0
        sub_pattern = re.compile("|".join(re.escape(k) for k in rep.keys()))
        for match in re.finditer(pattern, string):
            new_text = sub_pattern.sub(lambda m: rep[m.group()], match.group(1))
            new_strings += [string[pos:match.start(1)], new_text]
            pos = match.end(1)
        new_strings.append(string[pos:])
        return ''.join(new_strings)

    def adapt_img(self, string, is_md=False):
        # ![desc](link) -> ![desc](link "desc")
        # The first desc part is retained for compatibility
        # ![](link) -> ![](link)
        match = re.match(r'!\[(.*?)\]\((.*?)\)', string)
        if not match:
            return string
        desc, link = match.group(1), match.group(2)
        if '(' in link:
            logger.warning(f'parentheses in link: {string}')
        desc = f' "{desc}"' if desc and not is_md else ''
        if not link.startswith('http'):
            link = joinurl(IMG_URL_ROOT, link)
        new_strings = [string[:match.start(2)], link, desc, string[match.end(2):]]
        return ''.join(new_strings)


class PostAdapter(BaseAdapter):
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.isin_details = False
        super().__init__()

    def handle_details(self, line):
        if not line.startswith('<details>'):
            return self.adapt_img(line, is_md=True)
        pattern = r'<details><summary>{}</summary>'
        appendix = Tag.font(' (Show more &raquo;)', 'deepskyblue')
        return re.sub(
            pattern.format(r'(.*)'),
            lambda m: pattern.format(m.group(1) + appendix),
            line
        )

    def adapt_line(self, line):
        raw_line = line
        line = self.adapt_escape(line, mode='link')
        line = self.adapt_escape(line, mode='inline-math')
        line = self.adapt_display_math(line)
        line = self.adapt_img(line)
        if r'^*' in line:
            # might cause trouble in display math
            logger.warning(f'{self.path.name}: "^*" in display math: {line}')
        if raw_line != line:
            logger.debug(f'Raw: {raw_line}Adapted: {line}')
        return line

    def adapt(self):
        lines_buffer = []
        new_lines = []
        with open(self.path, encoding='utf8') as reader:
            for line in reader:
                if line.startswith('<details>') or line.startswith('</details>'):
                    self.isin_details = not self.isin_details
                if self.isin_details:
                    lines_buffer.append(self.handle_details(line))
                else:
                    if lines_buffer:
                        html_line = markdown.markdown(
                            ''.join(lines_buffer[1:]),
                            extensions=['fenced_code']
                        )
                        new_lines += [lines_buffer[0], html_line]
                        lines_buffer.clear()
                    new_lines.append(self.adapt_line(line))
        return ''.join(new_lines)
