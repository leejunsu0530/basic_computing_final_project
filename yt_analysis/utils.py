import requests
import json
import zipfile
from pathlib import Path
from typing import Generator, Union, Literal


def safe_filename(filename: str | Path) -> str:
    """윈도우에서 불가능한 파일명을 전각 문자로 바꿔서 해결"""
    invalid_to_fullwidth = str.maketrans({
        '<': '＜',  # U+FF1C
        '>': '＞',  # U+FF1E
        ':': '：',  # U+FF1A
        '"': '＂',  # U+FF02
        '/': '／',  # U+FF0F
        '\\': '＼',  # U+FF3C
        '|': '｜',  # U+FF5C
        '?': '？',  # U+FF1F
        '*': '＊',  # U+FF0A
    })
    return str(filename).translate(invalid_to_fullwidth)


def check_path_format(path: Path, right_type: Literal['file', 'dir']):
    """파일 자리에 폴더 넣거나, 그 반대면 에러. 
    근데 is_ 함수들은 실제로 그 위치에 존재하지 않으면 무조건 false임 > 수정 필요. 
    to path 함수들에 넣을거임"""

    if right_type == 'file' and not path.suffix:
        raise TypeError(f"해당 위치의 변수에는 파일 경로가 와야 하지만, 디렉토리 경로가 입력되었습니다: {path}")
    if right_type == 'dir' and path.suffix:
        raise TypeError(f"해당 위치의 변수에는 디렉토리 경로가 와야 하지만, 파일 경로가 입력되었습니다: {path}")


def to_path_file(
    path: Path | str,
    *,
    force_ext: str | None = None,
    safe_filename_: bool = True
) -> Path:
    """force_ext: 확장자 강제 지정. zip이 필요한 경우 등에 txt 들어가면 안되니까 넣은 기능이지만, 폴더를 의도했어도 묻지 않고 파일로 만들어버리니 주의."""
    if isinstance(path, str):
        path = Path(path)
    if safe_filename_:
        path = Path(safe_filename(path))
    if not force_ext: # 확장자 강제 지정 안하면 폴더경로인지 확인 후 반환
        check_path_format(path, 'file')
        return path
    force_ext = force_ext.lstrip('.')
    if force_ext not in path.suffix: # 폴더여도 파일로 만들어버린다
        path = path.with_name(path.name + f'.{force_ext}') 
    return path


def to_path_dir(path: Union[Path, str, None],
                *, make_dir: bool = True) -> Path:
    if isinstance(path, str):
        path = Path(path)
        check_path_format(path, 'dir')
        if make_dir:
            path.mkdir(parents=True, exist_ok=True)
    elif path is None:
        path = Path.cwd()

    return path


def download_zip(
    url: str,
    extract_dir: Union[Path, str, None],
    *,
    zip_dir: Union[Path, str, None] = None,
    zip_name: str = "downloaded_file.zip",
    delete_zip: bool = True,
    timeout: int = 10
) -> Generator[Path, None, None]:
    """
    주로 colab에서 외부 파일 가져오는 용도.

    Params:
        url: zip 파일의 위치.
        extract_dir: 최종적으로 압축 해제할 경로. None일 경우 cwd.
        zip_dir: zip 파일을 다운로드할 디렉토리. None일 경우 cwd에 지정
        zip_name: zip 파일의 이름.
        delete_zip: 압축 해제 후 다운로드한 zip 파일 삭제 여부.
        timeout: requests 요청 제한 시간 (초). 기본값 10초.
    """
    extract_dir = to_path_dir(extract_dir)
    zip_path = to_path_dir(zip_dir) / zip_name

    try:
        # 1. 파일 다운로드 (timeout 추가)
        print(f"Downloading from {url}...")
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()  # 4xx, 5xx HTTP 에러 발생 시 예외 발생

        with zip_path.open("wb") as f:
            f.write(r.content)

    except requests.exceptions.Timeout:
        print(f"[Error] 다운로드 시간이 초과되었습니다. ({timeout}초)")
        raise
    except requests.exceptions.HTTPError as e:
        print(f"[Error] HTTP 에러가 발생했습니다: {e}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"[Error] 네트워크 요청 중 오류가 발생했습니다: {e}")
        raise
    except IOError as e:
        print(f"[Error] 파일 저장 중 입출력 오류가 발생했습니다: {e}")
        raise

    try:
        # 2. 압축 해제
        print(f"Extracting to {extract_dir}...")

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

    except zipfile.BadZipFile:
        print("[Error] 올바르지 않은 zip 파일이거나 파일이 손상되었습니다.")
        # 에러 발생 시 쓰레기 파일이 남지 않도록 지워줍니다.
        if zip_path.exists():
            zip_path.unlink()
        raise
    except Exception as e:
        print(f"[Error] 압축 해제 중 예상치 못한 오류가 발생했습니다: {e}")
        raise

    # 3. 임시 파일 삭제
    if delete_zip and zip_path.exists():
        try:
            zip_path.unlink()
            print("Temporary zip file deleted.")
        except IOError as e:
            print(f"[Warning] 임시 zip 파일 삭제 실패: {e}")

    print("Success!")
    return extract_dir.iterdir()


def write_json(file_path: str | Path, dict_: dict, encoding: str = 'utf-8') -> Path:
    """작성한 파일 경로를 반환"""
    file_path = to_path_file(file_path, force_ext='json')
    with file_path.open('w', encoding=encoding) as file:
        json.dump(dict_, file, ensure_ascii=False, indent=4)
    return file_path


def read_json(file_path: str | Path, encoding: str = 'utf-8') -> dict:
    """
    파일이 없을 시 FileNotFoundError 발생
    """
    file_path = to_path_file(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"주어진 경로 {file_path}에 파일이 없습니다.")
    else:
        with file_path.open('r', encoding=encoding) as file:
            dict_: dict = json.load(file)
        return dict_
