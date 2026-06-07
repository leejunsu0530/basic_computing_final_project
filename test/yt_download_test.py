from yt_analysis.simple_ydl_downloader import YdlDownloader

YdlDownloader(
    "http://www.youtube.com/channel/UCX6OQ3DkcsbYNE6H8uQQuVA", 
    info_json_dir=r"C:\Users\leeju\Projects\basic_computing_final_project\test\.test").download_playlist_info()
