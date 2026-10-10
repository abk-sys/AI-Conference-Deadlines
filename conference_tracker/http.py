"""Bounded HTTPS requests with robots.txt checks and transient retries."""
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

USER_AGENT = 'AIConferenceDeadlinesBot/1.0'
MAX_BYTES = 5_000_000


class HttpClient:
    def __init__(self):
        self.robots = {}

    def _read(self, url):
        if urlsplit(url).scheme != 'https':
            raise ValueError('Only HTTPS sources are supported')
        for attempt in range(3):
            try:
                request = Request(url, headers={'User-Agent': USER_AGENT, 'Accept': '*/*'})
                with urlopen(request, timeout=30) as response:
                    content = response.read(MAX_BYTES + 1)
                    if len(content) > MAX_BYTES:
                        raise ValueError(f'Response too large: {url}')
                    return content.decode('utf-8')
            except HTTPError as error:
                if error.code != 429 and error.code < 500:
                    raise
                if attempt == 2:
                    raise
            except (URLError, TimeoutError):
                if attempt == 2:
                    raise
            time.sleep(2 ** attempt)

    def get(self, url):
        parts = urlsplit(url)
        origin = f'{parts.scheme}://{parts.netloc}'
        if origin not in self.robots:
            parser = RobotFileParser()
            try:
                parser.parse(self._read(origin + '/robots.txt').splitlines())
            except HTTPError as error:
                if error.code == 404:
                    parser.parse(['User-agent: *', 'Allow: /'])
                else:
                    raise
            self.robots[origin] = parser
        parser = self.robots[origin]
        if not parser.can_fetch(USER_AGENT, url):
            raise ValueError(f'robots.txt disallows {url}')
        delay = parser.crawl_delay(USER_AGENT) or 0
        if delay > 30:
            raise ValueError('robots.txt requests a crawl delay longer than this collector supports')
        time.sleep(max(0.25, delay))
        return self._read(url)
