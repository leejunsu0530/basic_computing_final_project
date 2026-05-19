from pathlib import Path
import yt_dlp
from rich.progress import Progress
from rich.console import Console
import json

console = Console()

class YdlDownloader:
    def __init__(self):
        pass

    @staticmethod
    def write_json(path: str | Path, dict_: dict, encoding: str = 'utf-8') -> Path:
        """작성한 파일 경로를 반환"""
        if isinstance(path, str):
            path = Path(path)
        if 'json' not in path.suffix: # 확장자가 .json으로 끝나지 않으면 json 붙인 새 이름으로 반환
            path = path.with_name(path.name + '.json')
        path.parent.mkdir(parents=True, exist_ok=True) # path의 폴더를 만들기
        # console.log(f'{path.parent} 생성')
        with path.open('w', encoding=encoding) as file:
            json.dump(dict_, file, ensure_ascii=False, indent=4)
        return path

    @staticmethod
    def read_json(path: str | Path, encoding: str = 'utf-8') -> dict:
        """
        파일이 없을 시 FileNotFoundError 발생
        """
        if isinstance(path, str):
            path = Path(path)
        if not path.exists(): 
            raise FileNotFoundError(f"주어진 경로 {path}에 파일이 없습니다.")
        else:
            with path.open('r', encoding=encoding) as file:
                dict_: dict = json.load(str(file))
            return dict_

    def _get_video_list(self, info_dict: dict) -> list[dict]:
        """재귀함수로 순회하면서 영상 딕셔너리 리스트 반환"""
        # pl_opts = {'skip_download': True, 'extract_flat': 'in_playlist', "quiet": quiet}
        # with yt_dlp.YoutubeDL(pl_opts) as ydl:
        #     pl_flat_dict = ydl.extract_info(PLAYLIST_URL, download=False)
        # 이 위 부분은 다른 함수로 이관

        # # 재귀함수 클로저로 딕셔너리 내 entries 계층 들어가면서 _type가 url인 것들을 tmplst에 추가. 아래 함수 참고
        tmplst = []
        def walk(node: dict):
            node_type = node.get
                
    def extract_video_entries(data: dict) -> list[dict]:
        videos = []

        def walk(node):
            node_type = node.get('_type')

            # 실제 영상
            if node_type == 'url':
                videos.append(node)
                return

            # playlist류
            if node_type == 'playlist':
                for entry in node.get('entries', []):
                    walk(entry)

        walk(data)
        return videos


    def download_playlist_info(url: str, quiet:bool = True):
        
        def load_info_json()

        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        # 아래는 개 오래걸릴거니까 위 방식+멀티프로세싱
    !yt-dlp --skip-download --flat-playlist \
    --paths {str(json_path)} --output "%(upload_date>%y.%m)s/%(title)s [%(id)s].%(ext)s" \
    --write-comments --extractor-args "youtube:comment_sort=top;max_comments=10,10,0,0;lang=ko;skip=translated_subs" \ 
    --write-info-json -N 8 \
    --sleep-subtitles 5 --sleep-requests 0.75 --sleep-interval 5 --max-sleep-interval 5 \
    {PLAYLIST_URL}
    # def load_from_zip()