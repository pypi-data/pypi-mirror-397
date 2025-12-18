import argparse
import re
import shutil
import sys
import tempfile
import zipfile as zf
from collections.abc import Iterator
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import IntEnum, auto
from itertools import repeat
from pathlib import Path
from threading import Thread
from typing import NamedTuple

import questionary as qy
import requests
from bs4 import BeautifulSoup as bs
from bs4 import Tag
from iterfzf import iterfzf  # type: ignore
from loguru import logger

BASE = "https://zenius-i-vanisher.com/v5.2/"
SEARCH = f"{BASE}simfiles_search_ajax.php"


@dataclass
class Config:
    nozip: bool = False


config = Config()


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
                logger.info(f"END THREAD: {job.name}")
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
    log: Path = root / "vanisher.log"


Storage.songs.mkdir(parents=True, exist_ok=True)


class Group(IntEnum):
    ARCADE = auto()
    SPINOFF = auto()
    OFFICIAL = auto()
    USER = auto()
    INVALID = auto()


class Levels(NamedTuple):
    sp: str
    dp: str


@dataclass
class Sim:
    idx: str
    _title: str = ""

    @property
    def site(self) -> str:
        raise NotImplementedError

    @property
    def zipfile(self) -> str:
        raise NotImplementedError

    @property
    def title(self) -> str:
        if self._title == "":
            html = requests.get(self.site).text
            if match := re.search(r"<h1>\s?(.+?)(?=\s\/\s|<\/h1>)", html):
                self._title = match.group(1)
        return self._title


@dataclass
class Category(Sim):
    @property
    def site(self) -> str:
        return f"{BASE}viewsimfilecategory.php?categoryid={self.idx}"

    @property
    def zipfile(self) -> str:
        return f"{BASE}download.php?type=ddrpack&categoryid={self.idx}"


@dataclass
class Simfile(Sim):
    @property
    def site(self) -> str:
        return f"{BASE}viewsimfile.php?simfileid={self.idx}"

    @property
    def zipfile(self) -> str:
        return f"{BASE}download.php?type=ddrsimfile&simfileid={self.idx}"

    @property
    def zipfile_custom(self) -> str:
        return f"{BASE}download.php?type=ddrsimfilecustom&simfileid={self.idx}"


@dataclass
class Result:
    song_name: str
    song_page: str
    pack_name: str
    pack_page: str
    group: str
    difficulties: Levels
    artist: str = field(default_factory=str)

    @property
    def song(self) -> Simfile:
        simfile = Simfile("", self.song_name)
        if match := re.search(r"id=(\d+)", self.song_page):
            simfile.idx = match.group(1)
        return simfile

    @property
    def pack(self) -> Category:
        category = Category("", self.pack_name)
        if match := re.search(r"id=(\d+)", self.pack_page):
            category.idx = match.group(1)
        return category

    @property
    def entry(self) -> str:
        return f"{self.song_name} | {self.artist} | sp: {self.difficulties.sp} dp: {self.difficulties.dp} | {self.pack_name}"


def get_group(listing: Tag) -> set[Group]:
    groups = set()
    if (parent := listing.find_parent()) is not None:
        if group := parent.find_previous_sibling():
            if group.text != "User":
                groups.add(Group.OFFICIAL)
                if group.text == "Arcade":
                    groups.add(Group.ARCADE)
                else:
                    groups.add(Group.SPINOFF)
            elif group.text == "User":
                groups.add(Group.USER)
    if not groups:
        return {Group.INVALID}
    return groups


def categories(group: Group) -> Iterator[Category]:
    response = requests.get(f"{BASE}simfiles.php?category=simfiles").content
    soup = bs(response, "lxml")
    for listing in soup.select("tr td.border select"):
        if group in get_group(listing):
            for category in listing.select("option"):
                if (idx := category["value"]) != "0" and isinstance(idx, str):
                    yield Category(idx, category.text)


def search_song(title: str = "", artist: str = "") -> list[Result]:
    params = {"songtitle": f"{title}", "songartist": f"{artist}"}
    r = requests.post(SEARCH, data=params).text
    soup = bs(r, "lxml")
    results = []
    passed = False
    for group in soup.select("thead th[colspan]"):
        if group:
            current_group = group.text
            if table := group.find_next("tbody"):
                if hasattr(table, "select"):
                    if matches := table.select("tr"):
                        passed = True
        if not passed:
            continue
        for match in matches:
            if len(data := match.find_all("td")) != 4:
                continue
            song_name, artist = data[0].a["title"].split(" / ", 1)
            song_page = f"{BASE}{data[0].a['href']}"
            sp_lvls = data[1].text.strip()
            dp_lvls = data[2].text.strip()
            pack_name = data[3].a.text.strip()
            pack_page = f"{BASE}{data[3].a['href']}"
            result = Result(
                song_name,
                song_page,
                pack_name,
                pack_page,
                current_group,
                Levels(sp_lvls, dp_lvls),
                artist,
            )
            results.append(result)
    return results


def download_custom(simfile: Simfile, prefix: Path) -> bool:
    archive = Path(f"{simfile.title}.zip")
    try:
        with requests.get(simfile.zipfile_custom, stream=True) as response:
            with open(archive, "wb") as file:
                shutil.copyfileobj(response.raw, file)
    except:
        logger.error(f"No custom zipfile available {simfile.site}")
        return False
    if zf.is_zipfile(archive):
        with tempfile.TemporaryDirectory() as path:
            tmp_path = Path(path)
            destination = prefix
            if not any(
                [simfile.title + "/" in x for x in zf.ZipFile(archive).namelist()]
            ):
                destination = prefix / simfile.title
                tmp_path = tmp_path / simfile.title
            zf.ZipFile(archive).extractall(path=tmp_path)
            archive.unlink()
            shutil.copytree(tmp_path, destination, dirs_exist_ok=True)
            logger.info(f"Downloaded {simfile.title}\n\t{simfile.site}")
            return True
    else:
        logger.error(f"Custom zipfile download not a zip {simfile.site}")
        return False


def download_zip(
    sim: Sim, dump: bool = False, pack: str = "", cwd: bool = False
) -> None:
    if pack:
        prefix = Storage.songs / pack
        prefix.mkdir(parents=True, exist_ok=True)
    elif cwd:
        prefix = Path()
    elif dump:
        prefix = Storage.songs / "dump"
        prefix.mkdir(parents=True, exist_ok=True)
    else:
        prefix = Storage.songs
    if isinstance(sim, Category) and config.nozip:
        name = f"Downloading individual sims for {sim.title}"
        thread = Thread(target=download_category_zips, args=[sim])
        Jobs.add(name, thread)
        return
    archive = Path(f"{sim.title}.zip")
    if isinstance(sim, Simfile):
        if download_custom(sim, prefix):
            return
    with requests.get(sim.zipfile, stream=True) as response:
        with open(archive, "wb") as file:
            shutil.copyfileobj(response.raw, file)
    if extract_zip(archive, prefix, sim):
        return
    else:
        if isinstance(sim, Category):
            logger.info("No category zipfile found, attempting to download songs")
        else:
            logger.info("No chart zipfile found")
    if isinstance(sim, Category):
        name = f"Downloading individual sims for {sim.title}"
        thread = Thread(target=download_category_zips, args=[sim])
        Jobs.add(name, thread)


def extract_zip(archive: Path, prefix: Path, sim: Sim) -> bool:
    if zf.is_zipfile(archive):
        with tempfile.TemporaryDirectory() as path:
            tmp_path = Path(path)
            destination = prefix
            if not any([sim.title + "/" in x for x in zf.ZipFile(archive).namelist()]):
                destination = prefix / sim.title
                tmp_path = tmp_path / sim.title
            zf.ZipFile(archive).extractall(path=tmp_path)
            archive.unlink()
            shutil.copytree(tmp_path, destination, dirs_exist_ok=True)
            logger.info(f"Downloaded {sim.title}\n\t{sim.site}")
            return True
    else:
        Path(archive).unlink()
        return False


def download_category_zips(category: Category) -> None:
    html = requests.get(category.site).text
    songs = re.findall(r'viewsimfile\.php\?simfileid=(\d+).*?title="(.*?)\s\/', html)
    simfiles = [Simfile(idx, title) for idx, title in songs]
    with ThreadPoolExecutor(max_workers=8) as tp:
        tp.map(download_zip, simfiles, repeat(False), repeat(category.title))


def download_group(group: Group) -> None:
    for category in categories(group):
        name = f"Downloading for {group.name}: {category.title}"
        thread = Thread(target=download_zip, args=[category])
        Jobs.add(name, thread)


def download_url(url: str) -> None:
    if match := re.search(r"(category|simfile)id=(\d+)", url):
        if len(match.groups()) == 2:
            typ, idx = match.groups()
            sim = Sim("")
            if typ == "category":
                sim = Category(idx)
                dump = False
                if config.nozip:
                    name = f"Downloading individual sims for {sim.title}"
                    thread = Thread(target=download_category_zips, args=[sim])
                    Jobs.add(name, thread)
                    return
            else:
                sim = Simfile(idx)
                dump = True
            print(f"Downloading {typ} {idx}")
            download_zip(sim, dump=dump)
            return
    logger.error(f"Not a valid url: {url}")


def interface(menu: str) -> str:
    Jobs.track_jobs()
    qy.print(f"{len(Jobs.tracker)} jobs active")
    if menu == "main":
        choices = [
            qy.Choice("Download bundles", "download", shortcut_key="d"),
            qy.Choice("Song search", "song", shortcut_key="s"),
            qy.Choice("Pack search", "pack", shortcut_key="p"),
        ]
        choice = qy.select(
            "Choose an option", choices=choices, use_shortcuts=True
        ).ask()
        if not choice:
            Jobs.track_jobs()
            jobs = Jobs.tracker
            if len(jobs) > 0:
                print(f"{len(jobs)} Active job(s):")
                for job in jobs:
                    print(f"\t{job.name}")
            message = "Do you want to quit?"
            if qy.confirm(message, default=False).ask() is True:
                return "exit"
        menu = choice
    if menu == "download":
        choices = [qy.Choice("Go back", value=Group.INVALID, shortcut_key="b")]
        choices.extend(
            [qy.Choice(g.name, g, shortcut_key=str(g.value)) for g in list(Group)[:3]]
        )
        group: Group = qy.select(
            "Choose group to download", choices=choices, use_shortcuts=True
        ).ask()
        if group is Group.INVALID or not group:
            return "main"
        name = f"Downloading group: {group.name}"
        print(name)
        thread = Thread(target=download_group, args=[group])
        Jobs.add(name, thread)
        return "download"
    if menu == "song":
        answers = qy.form(
            title=qy.text("Enter song name"), artist=qy.text("Enter artist name")
        ).ask()
        if not answers:
            return "main"
        title = answers.get("title", "")
        artist = answers.get("artist", "")
        if title == "" and artist == "":
            if qy.confirm("Would you like to go back to main menu?").ask():
                return "main"
            return menu
        print("Fetching results...")
        search_results = search_song(title, artist)
        if not search_results:
            print("No results found. Try again.")
            return "song"
        results = [qy.Choice(song.entry, song) for song in search_results]
        choices = qy.checkbox("Pick songs to download", choices=results).ask()
        if not choices:
            return "main"
        for choice in choices:
            name = f"Downloading song: {choice.song_name} by {choice.artist}"
            thread = Thread(target=download_zip, args=[choice.song, True])
            Jobs.add(name, thread)
        return menu
    if menu == "pack":
        choices = [qy.Choice("Go back", value=Group.INVALID, shortcut_key="b")]
        choices.extend(
            [
                qy.Choice(g.name, g, shortcut_key=s)
                for g, s in zip((Group.USER, Group.OFFICIAL), ("u", "o"))
            ]
        )
        group: Group = qy.select("", choices=choices, use_shortcuts=True).ask()  # type: ignore
        if group is Group.INVALID or not group:
            return "main"
        pack_lookup = {pack.title: pack for pack in categories(group)}
        try:
            answer = iterfzf(iter(pack_lookup.keys()), multi=True)
        except KeyboardInterrupt:
            return "pack"
        if not answer or len(answer) == 0:
            return "pack"
        Jobs.track_jobs()
        for pack_name in answer:
            pack = pack_lookup[pack_name]
            name = f"Downloading pack: {pack.title}"
            thread = Thread(target=download_zip, args=[pack])
            Jobs.add(name, thread)
        return "pack"
    return "main"


usage = """Usage:
    zenius [-l,--log] [url...]

    Enter the cli by not passing args.
    Log located at $HOME/.local/zenius/vanisher.log
"""


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CLI program with log and config options"
    )
    parser.add_argument("--url", help="zenius site url for chart or pack")
    parser.add_argument(
        "-l", "--log", action="store_true", help="Open log file in editor"
    )
    parser.add_argument(
        "--nozip",
        action="store_true",
        help="Ignore pack zips and attempt to download charts individually",
    )
    parser.add_argument(
        "-c", "--config", action="store_true", help="Open configuration file in editor"
    )

    return parser.parse_args()


def main() -> None:
    logger.remove()
    logger.add(Storage.log, retention="1 day")
    args = cli()
    config.nozip = args.nozip
    if args.log:
        with open(Storage.log) as f:
            shutil.copyfileobj(f, sys.stdout)
    elif args.url:
        with ThreadPoolExecutor() as tp:
            tp.map(download_url, args)
        return None
    else:
        menu = "main"
        while True:
            if menu == "exit":
                break
            Jobs.track_jobs()
            menu = interface(menu)


if __name__ == "__main__":
    main()
