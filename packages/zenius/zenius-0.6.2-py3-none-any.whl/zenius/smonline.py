import os
import shutil
import zipfile as zf
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from threading import Thread
from typing import NamedTuple

import questionary as qy
import requests
from bs4 import BeautifulSoup as bs
from bs4 import Tag
from bs4.element import ResultSet
from iterfzf import iterfzf  # type: ignore
from loguru import logger

BASE = "https://stepmaniaonline.net"
SEARCH = f"{BASE}/search"


class Job(NamedTuple):
    name: str
    thread: Thread


class Jobs:
    tracker: list[Job] = []

    @classmethod
    def track_jobs(cls) -> None:
        running: list[Job] = []
        for job in cls.tracker:
            if job.thread.is_alive():
                running.append(job)
            else:
                logger.debug(f"END THREAD: {job.name}")
        cls.tracker = running

    @classmethod
    def add(cls, name: str, thread: Thread) -> None:
        logger.trace(f"START THREAD: {name}")
        thread.daemon = True
        thread.start()
        cls.tracker.append(Job(name, thread))


class Storage:
    root: Path = Path.home() / ".local" / "zenius"
    songs: Path = root / "songs"
    log: Path = root / "smonline.log"


Storage.songs.mkdir(parents=True, exist_ok=True)


class Entry(NamedTuple):
    pack_title: str
    size: str
    songs: int
    cdate: date
    download: str
    idx: int

    def __repr__(self) -> str:
        return f"{self.pack_title:<68} | {self.songs:<3} | {self.size:<9} | {self.cdate} | ID:{self.idx}"


class SearchEntry(NamedTuple):
    song_title: str
    artist: str
    pack_title: str
    download: str
    idx: int

    def __repr__(self) -> str:
        return f"{self.song_title:<68} | {self.artist:<20} | {self.pack_title:<68} | ID:{self.idx}"


@dataclass
class Cache:
    _results: set[Entry] = field(default_factory=set)

    def build(self) -> None:
        logger.info("Building pack cache...")
        response = requests.get(f"{BASE}/packs").text
        soup = bs(response, "lxml")
        entries = soup.select("tbody tr")
        self._results = set(map(gen_row, entries))

    @property
    def results(self) -> set[Entry]:
        if not self._results:
            self.build()
        return self._results

    @property
    def map(self) -> dict[int, Entry]:
        return {entry.idx: entry for entry in self.results}


cache = Cache()


def gen_row(row: Tag) -> Entry:
    tags = row.select("td")
    title = tags[1].find("a").text  # type: ignore
    size = tags[2].text.replace("\xa0", " ")
    songs = int(tags[3].text)
    cdate = datetime.strptime(tags[5].text.strip(), "%Y-%m-%d").date()
    download = f"{BASE}{tags[6].find('a').get('href')}"  # type: ignore
    idx = int(download.split("/")[-2])
    return Entry(title, size, songs, cdate, download, idx)


def gen_search_row(row: Tag) -> SearchEntry:
    tags = row.select("td")
    title = tags[1].text
    artist = tags[2].text
    pack = tags[3].text
    download = f"{BASE}/download{tags[3].find('a').get('href')}/"  # type: ignore
    idx = int(download.split("/")[-2])
    return SearchEntry(title, artist, pack, download, idx)


def fetch_table(url: str) -> ResultSet[Tag]:
    response = requests.get(url).text
    soup = bs(response, "lxml")
    return soup.select("tbody tr")


def download_zip(pack_title: str, url: str) -> None:
    if pack_exists(pack_title):
        logger.warning(f"Pack {pack_title} from {url} exists. Skipping")
        return None
    prefix = Storage.songs
    prefix.mkdir(parents=True, exist_ok=True)
    archive = prefix / Path(f"{pack_title}.zip")
    with requests.get(url, stream=True) as response:
        with open(archive, "wb") as file:
            shutil.copyfileobj(response.raw, file)
    if not zf.is_zipfile(archive):
        logger.error(f"Cannot download {pack_title} from {url}")
        return None
    with zf.ZipFile(archive, "r") as zipped:
        extracted_name = zipped.getinfo(zipped.namelist()[0]).filename.split("/")[0]
        extracted_path = prefix / extracted_name
        destination = prefix / pack_title
        zipped.extractall(path=prefix)
    shutil.move(extracted_path, destination)
    archive.unlink()
    logger.debug(f"Downloaded {pack_title}\n\t{url}")


def pack_exists(title: str, storage: Path = Storage.songs) -> bool:
    packs = [f.name for f in os.scandir(storage) if f.is_dir()]
    if title in packs:
        return True
    return False


def spawn_threads(
    mapping: dict[int, Entry] | dict[int, SearchEntry], selection: list[str]
) -> None:
    rows = [mapping[int(s.split("ID:")[-1])] for s in selection]
    for row in rows:
        name = f"Downloading pack: {row.pack_title}"
        thread = Thread(target=download_zip, args=[row.pack_title, row.download])
        Jobs.add(name, thread)


def search_interface(category: str) -> None:
    query = qy.text(f"Enter {category} name: ").ask()
    if not query:
        return
    rows = fetch_table(f"{SEARCH}/{category}/{query}")
    entries = set(map(gen_search_row, rows))
    mapping = {entry.idx: entry for entry in entries}
    try:
        selection = iterfzf(
            iter([str(entry) for entry in entries]), multi=True, sort=True
        )
    except KeyboardInterrupt:
        return
    spawn_threads(mapping, selection)


def interface(menu: str) -> str:
    if menu == "main":
        jobs = Jobs.tracker
        qy.print(f"{len(jobs)} jobs in progress.")
        choices = [
            qy.Choice("Search Title", "title", shortcut_key="t"),
            qy.Choice("Search Artist", "artist", shortcut_key="a"),
            qy.Choice("Search Pack", "pack", shortcut_key="p"),
        ]
        choice = qy.select(
            "Choose an option", choices=choices, use_shortcuts=True
        ).ask()
        if not choice:
            if len(jobs) > 0:
                print(f"{len(jobs)} Active job(s):")
                for job in jobs:
                    print(f"\t{job.name}")
            message = "Do you want to quit?"
            if qy.confirm(message, default=False).ask() is True:
                return "exit"
        menu = choice
    if menu == "pack":
        mapping = cache.map
        try:
            selection = iterfzf(
                iter([str(entry) for entry in mapping.values()]), multi=True, sort=True
            )
        except KeyboardInterrupt:
            return "main"
        spawn_threads(mapping, selection)
    if menu == "title":
        search_interface("title")
    if menu == "artist":
        search_interface("artist")
    return "main"


def main() -> None:
    logger.remove()
    logger.add(Storage.log, retention="1 day")
    menu = "main"
    while True:
        if menu == "exit":
            break
        Jobs.track_jobs()
        menu = interface(menu)


if __name__ == "__main__":
    main()
