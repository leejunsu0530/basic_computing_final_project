# 데이터 가져오기
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from yt_analysis.utils import read_json
from pathlib import Path
from yt_analysis.simple_ydl_downloader import YdlDownloader
from yt_analysis.utils import download_zip
from yt_analysis.codes_from_class import check_positive, generate_wordcloud
from rich.pretty import pprint
# from yt_analysis import console
from rich.console import Console
from rich.markdown import Markdown

console = Console()

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

console.print(Markdown(
    """# 분석 목표
- 틱톡과 유튜브의 1위 채널들을 분석하여, 각 플랫폼에서 사람들에게 선호되는 성향(영상 길이, 영상 제목의 방향성 등)을 비교한다

# 평가 기준
- 심층적인 분석
    - 예를 들어, 단순히 영상 제목이 부정적인지 긍정적인지를 비교하는 것에서 끝나는 게 아니라, 왜 이런 결과가 나오는지 가설 세우고 검증. > 높은 점수
"""))

# 1. 둘의 간략한 채널 데이터 비교(구독자 수, 평균 조회수, 채널 운영 기간 등)
console.print(Markdown("# 1. 둘의 간략한 채널 데이터 비교(구독자 수, 평균 조회수, 채널 운영 기간 등)"))
mrbeast_channel_info = read_json(json_path / "mrbeast.json")
khaby_channel_info = read_json(json_path / "khaby.lame.json")


def channel_summary(channel_info, df, name="channel"):
    subs = channel_info.get('channel_follower_count') or channel_info.get(
        'channel_subscriber_count')
    num_videos = len(df)
    avg_views = None
    if 'view_count' in df.columns:
        vc = pd.to_numeric(df['view_count'], errors='coerce')
        if vc.dropna().size:
            avg_views = int(vc.dropna().mean())

    # 채널 운영 기간(데이터에 upload_date가 있으면 계산)
    channel_period = None
    if 'upload_date' in df.columns and df['upload_date'].notna().any():
        try:
            dates = pd.to_datetime(df['upload_date'].astype(
                str), format='%Y%m%d', errors='coerce')
            if dates.dropna().size:
                channel_period = (dates.max() - dates.min()).days
        except Exception:
            channel_period = None

    print(f"--- {name} summary ---")
    print(f"subscribers: {subs}")
    print(f"num_videos (in JSON folder): {num_videos}")
    print(f"avg_views (available videos): {avg_views}")
    print(f"estimated_channel_period_days: {channel_period}")


channel_summary(mrbeast_channel_info, df_mrbeast, name='MrBeast')
channel_summary(khaby_channel_info, df_khaby, name='Khaby')


# 2. 두 채널 운영자의 영상을 각각 업로드 시간-조회수 스케터 플롯으로 나타내기(둘의 그래프의 축 범위는 동일하게)
console.print(
    Markdown("# 2. 두 채널 운영자의 영상을 각각 업로드 시간-조회수 스케터 플롯으로 나타내기(둘의 그래프의 축 범위는 동일하게)"))


def plot_time_vs_views(df, ax, title):
    if 'upload_date' not in df.columns or 'view_count' not in df.columns:
        ax.text(0.5, 0.5, 'data not available', ha='center')
        ax.set_title(title)
        return
    dates = pd.to_datetime(df['upload_date'].astype(
        str), format='%Y%m%d', errors='coerce')
    views = pd.to_numeric(df['view_count'], errors='coerce')
    mask = dates.notna() & views.notna()
    ax.scatter(dates[mask], views[mask], alpha=0.6)
    ax.set_title(title)
    ax.set_xlabel('upload_date')
    ax.set_ylabel('view_count')


fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
plot_time_vs_views(df_mrbeast, axes[0], 'MrBeast upload_date vs views')
plot_time_vs_views(df_khaby, axes[1], 'Khaby upload_date vs views')
plt.tight_layout()
plt.show()


# 3. 둘의 영상 제목을 각각 워드 클라우드로 나타내기 - 어떠한 단어가 주로 사용되는지 보기 위해
console.print(
    Markdown("# 3. 둘의 영상 제목을 각각 워드 클라우드로 나타내기 - 어떠한 단어가 주로 사용되는지 보기 위해"))


def make_title_df_for_wordcloud(df):
    tmp = df[['title']].dropna().rename(columns={'title': 'text'})
    return tmp


make_wc_df = make_title_df_for_wordcloud(df_mrbeast)
generate_wordcloud(make_wc_df, text_column='text')

make_wc_df = make_title_df_for_wordcloud(df_khaby)
generate_wordcloud(make_wc_df, text_column='text')


# 4. 둘의 영상 제목들을 부정적인지 여부를 구한 후, 값들을 df에 벨류로 추가하고 그 평균과 중앙값을 내서 그래프에 그리기 - 부정적인 제목이 많은지 긍정적인 제목이 많은지
console.print(Markdown(
    "# 4. 둘의 영상 제목들을 부정적인지 여부를 구한 후, 값들을 df에 벨류로 추가하고 그 평균과 중앙값을 내서 그래프에 그리기 - 부정적인 제목이 많은지 긍정적인 제목이 많은지"))


def add_polarity_column(df):
    def polarity_of(text):
        try:
            blob = check_positive(str(text))
            return float(blob.sentiment.polarity)
        except Exception:
            return None

    df = df.copy()
    df['title_polarity'] = df['title'].apply(
        polarity_of) if 'title' in df.columns else None
    return df


df_mrbeast = add_polarity_column(df_mrbeast)
df_khaby = add_polarity_column(df_khaby)


def polarity_summary(df, name):
    if 'title_polarity' not in df.columns:
        print(name, 'no polarity data')
        return
    vals = pd.to_numeric(df['title_polarity'], errors='coerce').dropna()
    print(f"{name} polarity mean: {vals.mean() if vals.size else None}")
    print(f"{name} polarity median: {vals.median() if vals.size else None}")


polarity_summary(df_mrbeast, 'MrBeast')
polarity_summary(df_khaby, 'Khaby')


# 5. 두 채널 운영자의 각 영상 제목의 긍정/부정치와 조회수의 상관관계를 스케터 플롯으로 그리기(둘의 그래프의 축 범위는 동일하게)
console.print(Markdown(
    "# 5. 두 채널 운영자의 각 영상 제목의 긍정/부정치와 조회수의 상관관계를 스케터 플롯으로 그리기(둘의 그래프의 축 범위는 동일하게)"))


def plot_polarity_vs_views(df, ax, title):
    if 'title_polarity' not in df.columns or 'view_count' not in df.columns:
        ax.text(0.5, 0.5, 'data not available', ha='center')
        ax.set_title(title)
        return
    x = pd.to_numeric(df['title_polarity'], errors='coerce')
    y = pd.to_numeric(df['view_count'], errors='coerce')
    mask = x.notna() & y.notna()
    ax.scatter(x[mask], y[mask], alpha=0.6)
    ax.set_xlabel('title_polarity')
    ax.set_ylabel('view_count')
    ax.set_title(title)


fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
plot_polarity_vs_views(df_mrbeast, axes[0], 'MrBeast polarity vs views')
plot_polarity_vs_views(df_khaby, axes[1], 'Khaby polarity vs views')
plt.tight_layout()
plt.show()
