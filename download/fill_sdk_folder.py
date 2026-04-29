import argparse
import subprocess
from pathlib import Path
from typing import Any

import requests

# Example usage:
# python3 fill_sdk_folder.py -a linux_aarch64 -g $GITHUB_TOKEN


def extract_tag_and_url_from_release(release: dict[str, Any], architecture: str) -> tuple[str, str]:
    """
    Extracts the release tag and the URL to download the SDK from a release.

    Args:
        release (dict[str, Any]): Github API release JSON.
        architecture (str): The architecture we are interested in.

    Returns:
        A tuple containing the release tag and the URL to download the SDK.
    """
    # Extract release tag
    tag: str = ""

    if "tag_name" in release:
        tag = release["tag_name"]

    # Filter out beta releases
    if "-" in tag:
        return "", ""

    # Extract URL to download SDK
    asset_url: str = ""

    if "assets" in release:
        assets: Any = release["assets"]
        if isinstance(assets, list):
            for asset in assets:
                if not isinstance(asset, dict):
                    continue
                if "name" in asset:
                    name = asset["name"]
                    if architecture in name:
                        asset_url = asset["browser_download_url"]

    # Return release tag and URL to download SDK
    return tag, asset_url


def create_dictionary_of_releases(releases: Any, architecture: str) -> dict[str, str]:
    """
    Creates a dictionary of release tags and URLs to download SDKs.

    Args:
        releases (Any): Github API releases JSON.
        architecture (str): The architecture we are interested in.

    Returns:
        A dictionary of release tags and URLs to download SDKs.
    """
    results: dict[str, str] = {}

    # Iterate over releases
    if isinstance(releases, list):
        for release in releases:
            # Filter out non-dict releases
            if not isinstance(release, dict):
                continue

            # Filter out draft releases
            if "draft" in release and release["draft"]:
                continue

            # Extract release tag and URL to download SDK
            result: tuple[str, str] = extract_tag_and_url_from_release(release, architecture)
            tag: str = result[0]
            asset_url: str = result[1]

            # Add release tag and URL to download SDK to results
            if tag:
                results[tag] = asset_url

    # Return dictionary of release tags and URLs to download SDKs
    return results


def download_sdks(tags: dict[str, str], sdk_path: Path) -> None:
    """
    Downloads SDKs from the given tags and saves them to the given SDK path.

    Args:
        tags (dict[str, str]): A dictionary of release tags and URLs to download SDKs.
        sdk_path (Path): The path to save the SDKs to.
    """
    for tag, asset_url in tags.items():
        tag_folder: Path = sdk_path.joinpath(tag)
        file_path: Path = tag_folder.joinpath(asset_url.split("/")[-1])

        # Folder of version exists and have some files in it
        if tag_folder.exists() and len(list(tag_folder.iterdir())) > 0:
            print(f"Skipping {asset_url} because it already exists")
            continue

        # Create folder
        tag_folder.mkdir(parents=True, exist_ok=True)

        is_macos: bool = "macos" in asset_url

        # Download tar/zip
        print(f"Downloading {asset_url} to {file_path}")
        response: requests.Response = requests.get(asset_url)
        response.raise_for_status()

        # Save tar/zip
        with open(file_path, "wb") as file:
            file.write(response.content)

        # Extract tar/zip and delete it
        print(f"Extracting {file_path.name} and deleting it")
        if is_macos:
            subprocess.run(["unzip", file_path, "-d", tag_folder], check=True)
        else:
            subprocess.run(["tar", "-xf", file_path, "-C", tag_folder], check=True)
        file_path.unlink()

        # Clean-up
        if is_macos:
            clean_macos_folder(tag_folder, file_path)
        else:
            clean_linux_folder(tag_folder)

        # Add rights
        add_rights(tag_folder)


def add_rights(folder_path: Path) -> None:
    """
    Adds rights to SDK executable files.

    Args:
        folder_path (Path): The path to folder with executable files.
    """
    for item in folder_path.iterdir():
        subprocess.run(["chmod", "+x", item.as_posix()], check=True)


def clean_linux_folder(release_folder: Path) -> None:
    """
    Cleans a release folder by keeping only CLI and lib.

    Args:
        release_folder (Path): The path to the release folder.
    """
    bin_folder: Path = release_folder.joinpath("bin")

    # Delete everything except bin
    for item in release_folder.iterdir():
        if item.name == "bin":
            # print(f"Skipping bin: {item.as_posix()}")
            continue
        if item.is_file():
            # print(f"Deleting file: {item.as_posix()}")
            item.unlink()
        if item.is_dir() and item.name != "bin":
            # print(f"Deleting folder: {item.as_posix()}")
            delete_folder(item)

    # Copy CLI and lib from bin
    for path in bin_folder.rglob("*"):
        if path.is_file():
            # Copy path to release folder
            # print(f"Copying file: {path.as_posix()} to {release_folder.as_posix()}")
            copy_file(path, release_folder.joinpath(path.name))

    # Delete bin
    # print(f"Deleting folder: {bin_folder.as_posix()}")
    delete_folder(bin_folder)


def clean_macos_folder(release_folder: Path, file_path: Path) -> None:
    """
    Cleans a release folder by keeping only CLI and lib.

    Args:
        release_folder (Path): The path to the release folder.
        file_path (Path): The path to the file that was downloaded.
    """
    sub_name: str = file_path.stem
    sub_folder: Path = release_folder.joinpath(sub_name)

    if not sub_folder.exists():
        clean_linux_folder(release_folder)
        return

    # Delete everything except extracted folder
    for item in sub_folder.iterdir():
        if item.name == "bin":
            # print(f"Skipping bin: {item.as_posix()}")
            continue
        if item.is_file():
            # print(f"Deleting file: {item.as_posix()}")
            item.unlink()
        if item.is_dir() and item.name != sub_name:
            # print(f"Deleting folder: {item.as_posix()}")
            delete_folder(item)

    bin_folder: Path = sub_folder.joinpath("bin")

    # Delete everything except bin
    for item in release_folder.iterdir():
        if item.name == sub_name:
            # print(f"Skipping {sub_name}: {item.as_posix()}")
            continue
        if item.is_file():
            # print(f"Deleting file: {item.as_posix()}")
            item.unlink()
        if item.is_dir() and item.name != "bin":
            # print(f"Deleting folder: {item.as_posix()}")
            delete_folder(item)

    # Copy CLI and lib from bin
    for path in bin_folder.rglob("*"):
        if path.is_file():
            # Copy path to release folder
            # print(f"Copying file: {path.as_posix()} to {release_folder.as_posix()}")
            copy_file(path, release_folder.joinpath(path.name))

    # Delete bin
    # print(f"Deleting folder: {sub_folder.as_posix()}")
    delete_folder(sub_folder)


def copy_file(source: Path, destination: Path) -> None:
    """
    Copies a file from the source path to the destination path.

    Args:
        source (Path): The path to the source file.
        destination (Path): The path to the destination file.
    """
    destination.write_bytes(source.read_bytes())

    # For large files
    # with source.open("rb") as source_file, destination.open("wb") as destination_file:
    #     while chunk := source_file.read(1024 * 1024):  # 1 MB chunks
    #         destination_file.write(chunk)


def delete_folder(folder: Path) -> None:
    """
    Deletes a folder and all its contents.

    Args:
        folder (Path): The path to the folder.
    """
    for item in folder.iterdir():
        if item.is_file():
            item.unlink()
        if item.is_dir():
            delete_folder(item)
    folder.rmdir()


def parse_version(version: str) -> tuple:
    """
    Parses a version string "vX.Y.Z" into a tuple of integers (X, Y, Z).

    Args:
        version (str): The version string to parse.

    Returns:
        A tuple of integers representing the version.
    """
    return tuple(map(int, version.lstrip("v").split(".")))


# Parse arguments
parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Download publihed PDFix SDKs into sdk folder.")
parser.add_argument(
    "-a",
    "--architecture",
    choices=["linux_aarch64", "linux_x86_64", "macos_arm64"],
    required=True,
    help="Architecture to download SDK for.",
)
parser.add_argument("-f", "--folder", required=True, help="Where to download SDKs to.")
parser.add_argument("-g", "--github-token", required=True, help="GitHub token to use for API requests.")
args: argparse.Namespace = parser.parse_args()

architecture: str = args.architecture
github_token: str = args.github_token
folder: str = args.folder

# Get paths
project_path: Path = Path(__file__).parent.parent
sdk_path: Path = project_path.joinpath(folder)
sdk_path.mkdir(parents=True, exist_ok=True)
constants_path: Path = project_path.joinpath("src", "constants.py")

# Retrieve list of published SDKs
api_url: str = "https://api.github.com/repos/pdfix/pdfix_sdk_builds/releases"
headers: dict[str, str] = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
headers["Authorization"] = f"Bearer {github_token}"

# Retrieve list of published SDKs
response: requests.Response = requests.get(api_url, headers=headers)
response.raise_for_status()
releases: Any = response.json()
tags: dict[str, str] = create_dictionary_of_releases(releases, architecture)

# Debug: print tags and URLs to download SDKs
# for tag, asset_url in tags.items():
#     print(f"{tag}: {asset_url}")

# Download SDKs
download_sdks(tags, sdk_path)

# Change latest version in constants.py
versions: list[str] = list(tags.keys())
print(f"Versions: {versions}")
highest_version: str = max(versions, key=parse_version)
print(f"Highest version: {highest_version}")
with open(constants_path, "r") as file:
    lines: list[str] = file.readlines()
    for i, line in enumerate(lines):
        if line.startswith("LATEST_SDK_VERSION:"):
            lines[i] = f'LATEST_SDK_VERSION: str = "{highest_version}"\n'
            break
with open(constants_path, "w") as file:
    file.writelines(lines)

print(f"Done. SDK trees under: {sdk_path}")
