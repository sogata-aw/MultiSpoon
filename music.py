import pytube


class Music:
    def __init__(self, url, title, path, thumbnail_url, time):
        self.url = url
        self.title = title
        self.path = path
        self.thumbnail_url = thumbnail_url
        self.time = time
