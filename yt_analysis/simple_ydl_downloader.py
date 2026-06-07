from pathlib import Path
import yt_dlp
from rich.progress import Progress, track
import json
from typing import Generator, Literal
from .console import console
from .utils import to_path_file, to_path_dir, read_json, write_json


class YdlDownloader:
    def __init__(self,
                 *playlist_or_channel_urls: str,
                 info_json_dir: str | Path | None = None,
                 ydl_quiet: bool = False,
                 ):
        """채널을 플리와 동일하게 처리 가능. 최소한 유튜브에서는. 타 플랫폼은 확인 못 해봄"""
        self.playlists = playlist_or_channel_urls
        self.info_json_dir = to_path_dir(info_json_dir)
        self.quiet = ydl_quiet

    def _get_videos_list_from_flat(self, pl_url: str) -> Generator[dict, None, None]:
        """플랫한 info dict를 재귀적으로 순회해 `_type=='url'`인 항목들을 제너레이터로 반환합니다.
        메모리 사용을 줄이기 위해 즉시 yield 합니다.
        """

        def walk(node: dict, parent_info: dict | None = None) -> Generator[dict, None, None]:
            node_type = node.get('_type')
            if parent_info is None:
                parent_info = {}

            # 실제 영상
            if node_type == 'url':
                merged = dict(node)
                merged.update(parent_info)
                yield merged
            # playlist류
            elif node_type == 'playlist':
                # 직계 부모 플래이리스트의 정보를 동영상에 추가. 직계만 보존함.
                parent_info = {f"playlist_{parent_key}": node.get(parent_key, "N/A") for parent_key in (
                    "title", "uploader", "uploader_id", "uploader_url", "webpage_url", "playlist_count")}
                for entry in node.get('entries', []):
                    yield from walk(entry, parent_info)
            # 기타: _type이 둘 중 아무것도 아니더라도, entries가 있으면 재귀
            else:
                for entry in node.get('entries', []):
                    yield from walk(entry, parent_info)

        ydl_opts = {
            'quiet': self.quiet,
            'skip_download': True,
            'noprogress': True,
            'extract_flat': 'in_playlist',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            flat_info_dict = ydl.extract_info(pl_url, download=False)
            flat_info_dict = ydl.sanitize_info(flat_info_dict)

        yield from walk(flat_info_dict)

    def _get_real_video_data(self, video_info_dict: dict):
        pass

    def download_playlist_info(self):
        """rich.progress와 위 함수들을 사용해 실제로 영상 데이터를 뽑아오고 저장함. 실제 구동시에는 이 함수만 작동(아마도)"""
        videos = []
        for pl_url in track(self.playlists):
            for idx, video in enumerate(self._get_videos_list_from_flat(pl_url)):
                # console.print(idx, video.get('title'))
                videos.append(video)

        
        write_json(Path.cwd()/"mrbeast_flat_final.json", videos)



    def load_from_zip(self):
        pass
