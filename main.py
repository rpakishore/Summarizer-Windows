from pathlib import Path
from functools import lru_cache
import subprocess
import tomllib
import uuid
from requests.auth import HTTPBasicAuth
import requests
import getpass

import streamlit as st

st.set_page_config(page_title="Meeting Summarizer", page_icon="📃")

with open(Path(__file__).parent / "config.toml", "r") as f:
    config = tomllib.loads(f.read())


class TempMp3:
    def __init__(self, filepath: Path):
        self.__ffmpeg_path: Path | str = Path(__file__).parent / "binary" / "ffmpeg.exe"
        self.filepath = filepath
        assert self.filepath.exists()

    @lru_cache(maxsize=1)
    def __mp3_path(self) -> Path:
        return self.__convert_to_audio(file=self.filepath)

    def __enter__(self) -> Path:
        return self.__mp3_path()

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            print(f"[red]An exception occurred:[/red] {exc_type} - {exc_value}")
        self.__mp3_path().unlink()
        return False

    def __convert_to_audio(self, file: Path) -> Path:
        """Convert the given audio file to an ogg format."""
        with st.spinner("Extracting Audio..."):
            outputpath = Path(__file__).parent / "Temp" / f"{file.stem}_temp.ogg"
            outputpath.parent.mkdir(parents=True, exist_ok=True)
            # ffmpeg -i input.mp4 -ac 1 -ar 16000 -b:a 24k -c:a aac output.ogg
            command = f'"{self.__ffmpeg_path}" -loglevel quiet -stats -hide_banner -i "{file}" -vn -ac 1 -ar 16000 -c:a libopus -b:a 32k "{outputpath}" -y'
            _res = run_command(command=command)
            if _res != 0:
                st.error("Conversion to `.ogg` failed.")
                st.warning(f"Command: {command}\nResponse: {_res}")
                st.stop()
            st.success(f"Audio Extraction Successful!")
        return outputpath


def run_command(command: str) -> int:
    """Run shell commands using Subprocess; Returns the process returncode"""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    return process.returncode


_filepath = st.text_input("Enter the filepath:")

filepath = Path(_filepath.strip().strip('"').strip("'"))
if not filepath.exists():
    st.error("Specified file does not exist.")
    st.stop()

_run = st.button("Process & Upload")
if not _run:
    st.stop()

with TempMp3(filepath=filepath) as audiofile:
    with st.spinner("Uploading audio for summarization..."):
        with open(audiofile, "rb") as f:
            additional_data = {
                "email": config["user"]["email"],
                "filename": filepath.name,
                "uuid": f"{getpass.getuser()}{uuid.getnode()}",
            }
            files = {"file": (audiofile.name, f, "audio/mpeg")}
            response = requests.post(
                config["server"]["url"],
                files=files,
                data=additional_data,
                # auth=HTTPBasicAuth(config["server"]["user"], config["server"]["key"]),
            )

    if response.status_code == 200:
        st.success(
            "Summarizations Started. You will receive an email shortly (~30 mins with the summary.)"
        )
    else:
        st.error(
            "Error sending data to Summarization Service."
            " Retry or contact [Arun](mailto:summarization_service@rpakishore.co.in)"
            f' for support: "{response.text}"'
        )
