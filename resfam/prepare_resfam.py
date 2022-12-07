#!/usr/bin/env python3
# License: GNU Affero General Public License v3 or later
# A copy of GNU AGPL v3 should have been included in this software package in LICENSE.txt.

"""Script to download and fix the resfam database"""

import gzip
import hashlib
import os
import subprocess
from typing import Any, Type
from urllib import error as urlerror
from urllib import request

RESFAM_URL = "http://dantaslab.wustl.edu/resfams/Resfams.hmm.gz"
RESFAM_CHECKSUM = "82e9325283b999b1fb1351502b2d12194561c573d9daef3e623e905c1af66fd6"

CHUNKSIZE = 128 * 1024


class DownloadError(RuntimeError):
    """Exception to throw when downloads fail."""

    pass  # pylint: disable=unnecessary-pass


def get_remote_filesize(url: str) -> int:
    """Get the file size of the remote file."""
    try:
        with request.urlopen(request.Request(url, method="HEAD")) as usock:
            dbfilesize = usock.info().get("Content-Length", "0")
    except urlerror.URLError:
        dbfilesize = "0"

    dbfilesize = int(dbfilesize)  # db file size in bytes
    return dbfilesize


def get_free_space(folder: str) -> int:
    """Return folder/drive free space (in bytes)."""
    return os.statvfs(folder).f_bfree * os.statvfs(folder).f_frsize


def check_diskspace(file_url: str) -> None:
    """Check if sufficient disk space is available."""
    dbfilesize = get_remote_filesize(file_url)
    free_space = get_free_space(".")
    if free_space < dbfilesize:
        raise DownloadError(
            "ERROR: Insufficient disk space available "
            f"(required: {dbfilesize}, free: {free_space})."
        )


def download_file(url: str, filename: str) -> str:
    """Download a file."""
    try:
        req = request.urlopen(url)  # pylint: disable=consider-using-with
    except urlerror.URLError as exc:
        raise DownloadError("ERROR: File not found on server.\n"
                            "Please check your internet connection.") from exc

    # use 1 because we want to divide by the expected size, can't use 0
    expected_size = int(req.info().get("Content-Length", "1"))

    basename = os.path.basename(filename)
    dirname = os.path.dirname(filename)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    overall = 0
    with open(filename, "wb") as handle:
        while True:
            try:
                chunk = req.read(CHUNKSIZE)
                if not chunk:
                    print("")
                    break
                overall += len(chunk)
                print(
                    f"\rDownloading {basename}: {(overall / expected_size) * 100:5.2f}% downloaded.",
                    end="",
                )
                handle.write(chunk)
            except IOError as exc:
                raise DownloadError("ERROR: Download interrupted.") from exc
    return filename


def checksum(filename: str, chunksize: int = 2 ** 20) -> str:
    """Get the SHA256 checksum of a file."""
    sha = hashlib.sha256()
    with open(filename, "rb") as handle:
        for chunk in iter(lambda: handle.read(chunksize), b""):
            sha.update(chunk)

    return sha.hexdigest()


def unzip_file(filename: str, decompressor: Any, error_type: Type[Exception]) -> str:
    """Decompress a compressed file."""
    newfilename, _ = os.path.splitext(filename)
    try:
        zipfile = decompressor.open(filename, "rb")
        with open(newfilename, "wb") as handle:
            while True:
                try:
                    chunk = zipfile.read(CHUNKSIZE)
                    if not chunk:
                        break
                    handle.write(chunk)
                except IOError as exc:
                    raise DownloadError("ERROR: Unzipping interrupted.") from exc
    except error_type as exc:
        raise RuntimeError(
            f"Error extracting {os.path.basename(filename)}."
            " Please try to extract it manually."
        ) from exc
    print(f"Extraction of {os.path.basename(filename)} finished successfully.")
    return newfilename


def delete_file(filename: str) -> None:
    """Delete a file."""
    try:
        os.remove(filename)
    except OSError:
        pass


def present_and_checksum_matches(filename: str, sha256sum: str) -> bool:
    """Check if a file is present and the checksum matches."""
    if os.path.exists(filename):
        print(f"Creating checksum of {os.path.basename(filename)}")
        csum = checksum(filename)
        if csum == sha256sum:
            return True
    return False


def download_if_not_present(url: str, filename: str, sha256sum: str) -> None:
    """Download a file if it's not present or checksum doesn't match."""
    # If we are missing the archive file, go and download
    if not present_and_checksum_matches(filename, sha256sum):
        download_file(url, filename)

    print(f"Creating checksum of {os.path.basename(filename)}")
    csum = checksum(filename)
    if csum != sha256sum:
        raise DownloadError(
            f"Error downloading {filename}, sha256sum mismatch."
            f" Expected {sha256sum}, got {csum}."
        )


def download_resfam() -> None:
    """Download and sanitise the Resfam database."""
    archive_filename = os.path.join(os.getcwd(), "Resfams.hmm.gz")
    filename = os.path.splitext(archive_filename)[0]

    print("Downloading Resfam database")
    check_diskspace(RESFAM_URL)
    download_if_not_present(RESFAM_URL, archive_filename, RESFAM_CHECKSUM)
    filename = unzip_file(archive_filename, gzip, gzip.zlib.error)  # type: ignore
    delete_file(filename + ".gz")
    # remove tabs
    with subprocess.Popen(["hmmconvert", filename], stdout=subprocess.PIPE) as proc:
        out, err = proc.communicate()
        if proc.returncode:
            raise DownloadError(
                f"Failed to hmmconvert {filename}, "
                f"error:\n{err.decode(encoding='utf-8')}"
            )
    print("Ensuring all cutoffs are present")
    # add TC to those entries missing them
    # calculated as 10% less than the minimum scoring hit in their own group
    missing_cutoffs = {
        "RF0174": int(374 * 0.9),
        "RF0172": int(85 * 0.9),
        "RF0173": int(295 * 0.9),
        "RF0168": int(691 * 0.9),
    }
    with open(filename, "w", encoding="utf-8") as handle:
        lines = list(out.decode(encoding="utf-8").splitlines())
        i = 0
        while i < len(lines):
            # find an accession
            while i < len(lines) and not lines[i].startswith("ACC"):
                print(lines[i], file=handle)
                i += 1
            # end of file with no new accession
            if i >= len(lines):
                break
            # write the accession line itself
            print(lines[i], file=handle)

            # add the cutoffs if missing
            acc = lines[i].split()[1]
            i += 1
            if acc not in missing_cutoffs:
                continue
            value = missing_cutoffs[acc]
            # an accession of interest, so add cutoffs in the same place as others
            while not lines[i].startswith("CKSUM"):
                print(lines[i], file=handle)
                i += 1
            # write the CKSUM line
            print(lines[i], file=handle)
            # and finally add the cutoffs
            for cutoff in ["TC", "NC"]:
                handle.write(f"{cutoff}    {value}.00 {value}.00\n")
            i += 1


if __name__ == "__main__":
    download_resfam()
