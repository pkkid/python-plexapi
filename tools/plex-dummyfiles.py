#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plex-DummyFiles creates dummy files for testing with the proper
Plex folder and file naming structure.
"""

import argparse
import os
import re
import shutil
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union


BASE_DIR_PATH = Path(__file__).parents[1].absolute()
STUB_VIDEO_PATH = BASE_DIR_PATH / "tests" / "data" / "video_stub.mp4"


class DummyFiles:
    def __init__(self, **kwargs: Any):
        self.dummy_file: Path = kwargs['file']
        self.root_folder: Path = kwargs['root']
        self.title: str = kwargs['title']
        self.year: int = kwargs['year']
        self.tmdb: Optional[int] = kwargs['tmdb']
        self.tvdb: Optional[int] = kwargs['tvdb']
        self.imdb: Optional[str] = kwargs['imdb']
        self.dry_run: bool = kwargs['dry_run']
        self.clean: bool = kwargs['clean']

    @property
    def external_id(self) -> Optional[str]:
        """Return the external ID of the media."""
        if self.tmdb:
            return f"tmdb-{self.tmdb}"
        if self.tvdb:
            return f"tvdb-{self.tvdb}"
        if self.imdb:
            return f"imdb-{self.imdb}"
        return None

    def create_folder(self, folder: Path, parent: Optional[Path] = None, level: int = 0) -> None:
        """Create a folder with the path."""
        print(f"{'│  ' * level}├─ {folder}{os.sep}")

        if parent:
            folder = parent / folder
        folder = self.root_folder / folder

        if not self.dry_run:
            if self.clean and folder.exists():
                shutil.rmtree(folder)
            # No check for illegal characters in folder name
            folder.mkdir(parents=True, exist_ok=True)

    def create_files(self, files: List[Path], parent: Optional[Path] = None, level: int = 1) -> None:
        """Create a list of files with the given paths."""
        for file in files:
            print(f"{'│  ' * level}├─ {file}")

            if parent:
                file = parent / file
            file = self.root_folder / file

            if not self.dry_run:
                # No check for illegal characters in file name
                # Will overwrite files if they exist
                shutil.copy(self.dummy_file, file)


class DummyMovie(DummyFiles):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        versions = kwargs['versions'] or [["", 1]]
        self.edition: Optional[str] = kwargs['edition']
        self.versions: List[str] = [v[0] for v in versions]
        self.parts: List[int] = [v[1] for v in versions]
        self.movie_folder: Path = self.create_movie_folder()
        self.create_movie_files()

    def create_movie_folder(self) -> Path:
        """Create the movie folder with the proper naming structure."""
        folder = f"{self.title} ({self.year})"

        if self.edition:
            folder = f"{folder} {{edition-{self.edition}}}"
        if self.external_id:
            folder = f"{folder} {{{self.external_id}}}"

        movie_folder = Path(folder)
        self.create_folder(movie_folder)
        return movie_folder

    def create_movie_files(self) -> None:
        """Create the list of movie files with the proper naming structure."""
        title = f"{self.title} ({self.year})"

        _movie_parts: List[List[str]] = []
        movie_files: List[Path] = []

        for version in self.versions:
            if version:
                _movie_parts.append([title, f"- {version}"])
            else:
                _movie_parts.append([title])

        if self.edition:
            for _movie_part in _movie_parts:
                _movie_part.append(f"{{edition-{self.edition}}}")

        if self.external_id:
            for _movie_part in _movie_parts:
                _movie_part.append(f"{{{self.external_id}}}")

        for _movie_part, parts in zip(_movie_parts, self.parts):
            if parts > 1:
                for part in range(1, parts + 1):
                    _movie_file = f"{' '.join(_movie_part)} - pt{part}{self.dummy_file.suffix}"
                    movie_files.append(Path(_movie_file))
            else:
                _movie_file = f"{' '.join(_movie_part)}{self.dummy_file.suffix}"
                movie_files.append(Path(_movie_file))

        self.create_files(movie_files, parent=self.movie_folder)


class DummyShow(DummyFiles):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.seasons: List[List[int]] = kwargs['seasons']
        self.episodes: List[List[Union[int, List[int], Tuple[int, int]]]] = kwargs['episodes']
        self.show_folder: Path = self.create_show_folder()
        self.create_episode_files()

    def create_show_folder(self) -> Path:
        """Create the show folder with the proper naming structure."""
        folder = f"{self.title} ({self.year})"

        if self.external_id:
            folder = f"{folder} {{{self.external_id}}}"

        show_folder = Path(folder)
        self.create_folder(show_folder)
        return show_folder

    def create_episode_files(self) -> None:
        """Create the list of season folders and episode files with the proper naming structure."""
        for seasons, episodes in zip(self.seasons, self.episodes):
            for season in seasons:
                season_folder = Path(f"Season {season:02}")

                self.create_folder(season_folder, parent=self.show_folder, level=1)

                episode_files: List[Path] = []

                for episode in episodes:
                    if isinstance(episode, tuple):
                        _episode_file = (
                            f"{self.title} ({self.year})"
                            f" - S{season:02}E{episode[0]:02}-E{episode[1]:02}{self.dummy_file.suffix}"
                        )
                        episode_files.append(Path(_episode_file))
                    elif isinstance(episode, list) and episode[1] > 1:
                        for part in range(1, episode[1] + 1):
                            _episode_file = (
                                f"{self.title} ({self.year})"
                                f" - S{season:02}E{episode[0]:02} - pt{part}{self.dummy_file.suffix}"
                            )
                            episode_files.append(Path(_episode_file))
                    else:
                        _episode_file = f"{self.title} ({self.year}) - S{season:02}E{episode:02}{self.dummy_file.suffix}"
                        episode_files.append(Path(_episode_file))

                self.create_files(episode_files, parent=self.show_folder / season_folder, level=2)


def validate_folder_path(folder: str) -> Path:
    folder_path = Path(folder)
    if not folder_path.exists():
        raise argparse.ArgumentTypeError(f"Folder does not exist: {folder_path}")
    if not folder_path.is_dir():
        raise argparse.ArgumentTypeError(f"Path is not a folder: {folder_path}")
    return folder_path


def validate_file_path(file: str) -> Path:
    file_path = Path(file)
    if not file_path.exists():
        raise argparse.ArgumentTypeError(f"File does not exist: {file_path}")
    if not file_path.is_file():
        raise argparse.ArgumentTypeError(f"Path is not a file: {file_path}")
    return file_path


def validate_imdb_id(imdb_id: str) -> str:
    if re.match(r"tt\d{7,8}", imdb_id):
        return imdb_id
    raise argparse.ArgumentTypeError(f"Invalid IMDB ID: {imdb_id}")


def validate_versions(
    version_str: str,
    sep_parts: str = "|",
) -> List[Union[str, int]]:
    version_parts = version_str.split(sep_parts)
    if len(version_parts) == 1:
        return [version_parts[0], 1]
    return [version_parts[0], int(version_parts[1])]


def validate_number_ranges(
    num_str: str,
    sep: str = ",",
    sep_range: str = "-",
    sep_stack: str = "+",
    sep_parts: str = "|",
) -> List[Union[int, List[int], Tuple[int, int]]]:
    parsed: List[Union[int, List[int], Tuple[int, int]]] = []
    for part in num_str.split(sep):
        if sep_range in part:
            r1, r2 = [int(i) for i in part.split(sep_range)]
            parsed.extend(list(range(r1, r2 + 1)))
        elif sep_stack in part:
            s1, s2 = [int(i) for i in part.split(sep_stack)]
            parsed.append((s1, s2))
        elif sep_parts in part:
            ep, pt = [int(i) for i in part.split(sep_parts)]
            parsed.append([ep, pt])
        else:
            parsed.append(int(part))
    return parsed


if __name__ == "__main__":  # noqa: C901
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "media_type",
        help="Type of media to create",
        choices=["movie", "show"],
    )
    parser.add_argument(
        "-r",
        "--root",
        help="Root media folder to create the dummy folders and files",
        type=validate_folder_path,
        required=True
    )
    parser.add_argument(
        "-t",
        "--title",
        help="Title of the media",
        required=True,
    )
    parser.add_argument(
        "-y",
        "--year",
        help="Year of the media",
        type=int,
        required=True,
    )

    movie_group = parser.add_argument_group("Movie Options")
    movie_group.add_argument(
        "-ed",
        "--edition",
        help="Edition title"
    )
    movie_group.add_argument(
        "-vs",
        "--versions",
        help="Versions and parts to create (| for parts)",
        action="append",
        type=validate_versions,
    )

    show_group = parser.add_argument_group("TV Show Options")
    show_group.add_argument(
        "-sn",
        "--seasons",
        help="Seasons to create (- for range)",
        action="append",
        type=validate_number_ranges,
    )
    show_group.add_argument(
        "-ep",
        "--episodes",
        help="Episodes to create (- for range, + for stacked, | for parts)",
        action="append",
        type=validate_number_ranges,
    )

    id_group = parser.add_mutually_exclusive_group()
    id_group.add_argument(
        "--tmdb",
        help="TMDB ID of the media",
        type=int,
    )
    id_group.add_argument(
        "--tvdb",
        help="TVDB ID of the media",
        type=int,
    )
    id_group.add_argument(
        "--imdb",
        help="IMDB ID of the media",
        type=validate_imdb_id,
    )

    parser.add_argument(
        "-f",
        "--file",
        help="Path to the dummy video file",
        type=validate_file_path,
        default=STUB_VIDEO_PATH,
    )
    parser.add_argument(
        "--dry-run",
        help="Print the folder and file structure without creating the files",
        action="store_true",
    )
    parser.add_argument(
        "--clean",
        help="Remove the old files before creating new dummy files",
        action="store_true",
    )

    opts, _ = parser.parse_known_args()

    if opts.dry_run:
        print("Dry Run: No files will be created")

    print(f"{opts.root}{os.sep}")

    if opts.media_type == "movie":
        DummyMovie(**vars(opts))
    elif opts.media_type == "show":
        if not opts.seasons or not opts.episodes:
            parser.error("Both --seasons and --episodes are required for TV shows")
        if len(opts.seasons) != len(opts.episodes):
            parser.error("Number of seasons and episodes arguments must match")
        if any(not isinstance(season, int) for season_groups in opts.seasons for season in season_groups):
            parser.error("Seasons must be a list of integers or integer ranges")
        DummyShow(**vars(opts))
