# doc_search(q: str) -> list[url: str]

# doc_fetch(url: str) -> list[block]

# doc_grep(url: str, regex: str) -> list[block]



from typing import Optional


class FileReader:
    def __init__(self, url: str):
        pass

    def open(self, page_id: Optional[str] = None) -> str:
        pass

    def grep(self, regex: str) -> list[str]:
        pass