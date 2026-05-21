import requests
import zipfile
from pathlib import Path

# URL = "https://github.com/leejunsu0530/basic_computing_team/raw/main/datasets/datasets.zip"
# zip_path = Path("/content/datasets.zip")
# extract_path = Path("/content/datasets")


def to_path(path: Path | str) -> Path:
    if isinstance(path, str):
        return Path(path)
    else:
        return path


def download_zip(
    url: str,
    extract_path: Path | str,
    *,
    zip_path: Path | str = Path.cwd(),
    delete_zip: bool = True
):
    """
    주로 colab에서 외부 파일 가져오는 용도.
    Params:
        url: zip 파일의 위치. ex) https://github.com/leejunsu0530/basic_computing_team/raw/main/datasets/datasets.zip
        extract_path: 압축 해제할 경로
        zip_path: zip 파일을 다운로드할 경로. 입력 안하면 cwd에 다운로드 후 삭제
        delete_zip: 압축 해제 후 지울지 여부

    예외처리와 반환 부분 수정 필요
    """
    r = requests.get(url)
    extract_path = to_path(extract_path)
    zip_path = to_path(zip_path)

    with zip_path.open("wb") as f:
        f.write(r.content)

    # 폴더 없으면 생성
    extract_path.mkdir(parents=True, exist_ok=True)

    # 압축해제
    with zipfile.ZipFile(str(zip_path), 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    if delete_zip:
        zip_path.unlink()

    return extract_path.iterdir()


def download_zip2(
    url: str,
    extract_path: Path | str,
    zip_path: Path | str = Path.cwd(),
    delete_zip: bool = True
):
    """
    주로 colab에서 외부 파일 가져오는 용도
    Params:
        url: zip 파일의 위치. ex) https://github.com/leejunsu0530/basic_computing_team/raw/main/datasets/datasets.zip
        extract_path: 압축 해제할 경로
        zip_path: zip 파일을 다운로드할 경로 또는 파일명. 입력 안하면 cwd에 다운로드 후 삭제
        delete_zip: 압축 해제 후 지울지 여부
    """
    if not isinstance(url, str) or not url.strip():
        raise ValueError("url must be a non-empty string")

    extract_path = to_path(extract_path)
    zip_path = to_path(zip_path)

    if zip_path.exists() and zip_path.is_dir():
        filename = Path(url).name or "downloaded.zip"
        zip_path = zip_path / filename

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            f"Failed to download zip from {url}: {exc}") from exc

    if not response.content:
        raise RuntimeError(f"Downloaded file from {url} is empty")

    try:
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        with zip_path.open("wb") as f:
            f.write(response.content)
    except OSError as exc:
        raise RuntimeError(
            f"Failed to write downloaded zip to {zip_path}: {exc}") from exc

    try:
        extract_path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise RuntimeError(
            f"Failed to create extract directory {extract_path}: {exc}") from exc

    extracted = False
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)
        extracted = True
    except zipfile.BadZipFile as exc:
        raise RuntimeError(
            f"Downloaded file is not a valid zip archive: {zip_path}") from exc
    except OSError as exc:
        raise RuntimeError(
            f"Failed to extract zip file {zip_path}: {exc}") from exc
    finally:
        if delete_zip and extracted and zip_path.exists():
            try:
                zip_path.unlink()
            except OSError:
                pass

    return extract_path
