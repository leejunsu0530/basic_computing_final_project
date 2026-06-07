from pathlib import Path
import yt_dlp
from rich.progress import (track,
                           Progress,
                           SpinnerColumn,
                           TextColumn,
                           BarColumn,
                           TaskProgressColumn,
                           TimeElapsedColumn,
                           TimeRemainingColumn,
                           MofNCompleteColumn)
import json
from typing import Generator, Literal
from concurrent.futures import ThreadPoolExecutor, as_completed
# from yt_dlp.extractor.common import _InfoDict  # type: ignore
from .type import _InfoDict  # type: ignore
from .console import console  # type: ignore
from .utils import to_path_file, to_path_dir, read_json, write_json, safe_filename  # type: ignore
import itertools  # type: ignore


class YdlDownloader:
    def __init__(self,
                 *playlist_or_channel_urls: str,
                 playlist_info_json_dir: str | Path | None = None,
                 video_info_json_dir: str | Path | None = None,
                 ydl_quiet: bool = True,
                 ):
        """채널을 플리와 동일하게 처리 가능. 최소한 유튜브에서는. 타 플랫폼은 확인 못 해봄"""
        self.playlist_urls = playlist_or_channel_urls
        self.playlist_info_json_dir = to_path_dir(playlist_info_json_dir)
        self.video_info_json_dir = to_path_dir(video_info_json_dir)
        self.quiet = ydl_quiet

    def _get_playlist_info(self, pl_url: str) -> _InfoDict:
        ydl_opts = {
            'quiet': self.quiet,
            'skip_download': True,
            'noprogress': True,
            'extract_flat': 'in_playlist',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            flat_info_dict = ydl.extract_info(pl_url, download=False)
            flat_info_dict = ydl.sanitize_info(flat_info_dict)

        

        return flat_info_dict

    def _get_flat_videos_list(self, flat_info_dict: _InfoDict) -> Generator[dict, None, None]:
        """플랫한 info dict를 재귀적으로 순회해 `_type=='url'`인 항목들을 제너레이터로 반환합니다.
        메모리 사용을 줄이기 위해 즉시 yield 합니다.
        """

        def walk(node: _InfoDict, parent_info: dict | None = None) -> Generator[dict, None, None]:
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

        yield from walk(flat_info_dict)

    def _write_detailed_video_data(self, video_info_dict: _InfoDict):
        # 경로 모두 긁어오기(위쪽 계층에서, 다운로드할 목록 걸러내기...) > 끝나고
        
        url = video_info_dict.get('url')

        ydl_opts = {
            'quiet': self.quiet,
            'skip_download': True,
            'noprogress': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            info_dict = ydl.sanitize_info(info_dict)
            for k in ('formats', 'thumbnails'):
                if k in info_dict:
                    del info_dict[k]  # type: ignore

        write_json(
            self.video_info_json_dir / safe_filename(f"{video_info_dict.get('title')}.json"),
            info_dict,
        )
        # return info_dict

    def download_playlist_info(self, max_workers: int = 30):
        """rich.progress와 위 함수들을 사용해 실제로 영상 데이터를 뽑아오고 저장함. 실제 구동시에는 이 함수만 작동(아마도)"""
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            SpinnerColumn(),
            console=console,
            transient=True

        ) as progress:
            # flat_task = progress.add_task('', total=len(self.playlist_urls))
            pl_flat_list = [self._get_playlist_info(pl_url) for pl_url in track(self.playlist_urls,
                                                                                description="[cyan]각 플레이리스트들의 기본적인 정보들을 가져오는 중...",
                                                                                console=console,
                                                                                transient=True)]
            for pl in pl_flat_list:
                write_json(self.playlist_info_json_dir / pl.get('title'), pl)

            video_gen_list = [self._get_flat_videos_list(
                pl_info_dict) for pl_info_dict in pl_flat_list]
            combined_video_gen = itertools.chain(*video_gen_list)

            video_tasks = list(combined_video_gen)
            total_videos = len(video_tasks)

            if total_videos == 0:
                raise ValueError("[error] 추출할 비디오가 없습니다.")

            detail_task = progress.add_task(
                "각 비디오별 세부 정보 추출중...", total=total_videos)

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # submit 방식으로 작업을 예약
                worker_futures = {
                    executor.submit(self._write_detailed_video_data, video): video
                    for video in video_tasks
                }

                # 먼저 끝나는 스레드 순서대로 프로그래스 바 갱신
                for future in as_completed(worker_futures):
                    video_info = worker_futures[future]
                    video_title = video_info.get('title', 'Unknown')
                    try:
                        future.result()  # 에러 체크용
                        console.print(f"[green]비디오 처리 성공 ([white]title: {video_title}[/white]): {e}")
                    except Exception as e:  # type: ignore
                        console.print(f"[red]비디오 처리 실패 ([white]title: {video_title}[/white]): {e}")
                    finally:
                        progress.update(detail_task, advance=1)

            # with ThreadPoolExecutor(max_workers=max_workers) as executor:
            #     for _ in track(
            #         executor.map(self._write_detailed_video_data,
            #                     combined_video_gen),
            #         description="각 비디오별 세부 정보 추출중...",
            #         console=console,
            #         transient=True
            #     ):
            #         pass

    def read_data(self):
        """채널과 그에 해당하는 동영상을 전부 읽어와서 사전 지정된 포멧으로 만듦."""

    # def load_from_zip(self): # 위 함수로 통합
    #     pass
