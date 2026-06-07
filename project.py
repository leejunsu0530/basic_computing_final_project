# 데이터 가져오기
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from yt_analysis.utils import read_json
import sys
from pathlib import Path
from yt_analysis.simple_ydl_downloader import YdlDownloader
from yt_analysis.utils import download_zip
from yt_analysis.codes_from_class import check_positive, generate_wordcloud
from rich.pretty import pprint


json_path = Path('yt_dlp_jsons')
json_path.mkdir(parents=True, exist_ok=True)

# ----------

# 영상 파일들에서 필요한 데이터만 glob으로 가져와 df로 만들기

mrbeast_jsons = [read_json(p) for p in (json_path / "mrbeast").rglob("*.json")]
khaby_jsons = [read_json(p) for p in (json_path / "khabylame").rglob("*.json")]

# 영상 데이터에서 필요한 키와 벨류들을 가져와 df로 만들기
# 각각의 채널의 각 영상에서, 아래 키들을 가져온다. 만약 해당 키가 없으면 벨류를 None으로 하여 둔다.
keys = ('id', 'title', 'duration', 'view_count', 'comment_count',
        'like_count', 'upload_date', 'duration_string', 'aspect_ratio')

# mrbeast 데이터프레임 생성
mrbeast_data = [{key: video_info.get(key) for key in keys}
                for video_info in mrbeast_jsons]
df_mrbeast = pd.DataFrame(mrbeast_data)

# khaby 데이터프레임 생성
khaby_data = [{key: video_info.get(key) for key in keys}
              for video_info in khaby_jsons]
df_khaby = pd.DataFrame(khaby_data)

print(df_mrbeast.head())

# 분석 목표
# 틱톡과 유튜브의 1위 채널들을 분석하여, 각 플랫폼에서 사람들에게 선호되는 성향(영상 길이, 영상 제목의 방향성 등)을 비교한다

# 평가 기준
# 심층적인 분석
# 예를 들어, 단순히 영상 제목이 부정적인지 긍정적인지를 비교하는 것에서 끝나는 게 아니라, 왜 이런 결과가 나오는지 가설 세우고 검증. > 높은 점수


# 1. 둘의 간략한 채널 데이터 비교(구독자 수, 평균 조회수, 채널 운영 기간 등)
mrbeast_channel_info = read_json(json_path / "mrbeast.json")
khaby_channel_info = read_json(json_path / "khaby.lame.json")

# (둘의 파일을 읽고 간단하게 필요한 것들을 출력하는 코드)


# 2. 두 채널 운영자의 영상을 각각 업로드 시간-조회수 스케터 플롯으로 나타내기(둘의 그래프의 축 범위는 동일하게)


# 3. 둘의 영상 제목을 각각 워드 클라우드로 나타내기 - 어떠한 단어가 주로 사용되는지 보기 위해
# (generate_wordcloud() 사용)

# 4. 둘의 영상 제목들을 부정적인지 여부를 구한 후, 값들을 df에 벨류로 추가하고 그 평균과 중앙값을 내서 그래프에 그리기 - 부정적인 제목이 많은지 긍정적인 제목이 많은지
# (check_positive() 사용)

# 5. 두 채널 운영자의 각 영상 제목의 긍정/부정치와 조회수의 상관관계를 스케터 플롯으로 그리기(둘의 그래프의 축 범위는 동일하게)
