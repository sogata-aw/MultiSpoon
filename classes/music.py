import base64
import hashlib
import os


class Music:
    def __init__(self, title: str, url: str, requested_by: str, downloaded: bool = False):
        self.title = title
        self.url = url
        self.downloaded = downloaded
        self.requested = [requested_by]

    def download(self):
        os.system(
            f'yt-dlp.exe -x --audio-format opus --audio-quality 0 --cookies cookies.txt -v -P "music" -o "{self.title}.%(ext)s" --restrict-filenames ' + self.url)
