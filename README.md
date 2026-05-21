# basic_computing_final_project
대학교 1학년 1학기 컴퓨팅 기초 기말과제

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/leejunsu0530/basic_computing_final_project/blob/main/project.ipynb)

TODO:
-조회수와 여러 값들의 상관관계 분석하기. 채널은 미스터비스트로 결정.
ex: 과거 영상은 숏폼이 조회수가 더 높았지만 요즘은 그에 따른 피로감에 롱폼이 늘어가는 추세다.

1차 피드백: 다른 플랫폼도 가져와서, 유튜브만 비교하면 그냥 '기간이 짧을수록 조회수 높다' 같은건데, 다른 플랫폼이면 '사람들은 이런 조건에 마음이 음직인다'를 분석 가능. ex: 넷플릭스는 긴데 왜 조회수가 높은가.

[유튜브](https://kr.noxinfluencer.com/youtube-channel-rank/top-100-all-all-youtuber-sorted-by-subs-weekly), [트위치](https://kr.noxinfluencer.com/twitch-channel-rank/top-100-all-all-sorted-by-followers-weekly), [틱톡](https://kr.noxinfluencer.com/tiktok-channel-rank/top-100-all-all-sorted-by-followers-weekly) 구독자 수 상위 5명씩 뽑아서 분석

분석할 값:
- 조회수
- 업로드 날짜
- 업로드 시간
- 업로드 주기
- hf를 사용한 제목의 키워드
- 다른 플랫폼 데이터


---

## info_dict 구조 예시
- 일반 플래이리스트 형태 예시
    ```json
    {
        "title": "Playlist Title",
        "_type": "playlist",
        "entries": [
            {
                "title": "Title1",
                "_type": "url",
                "url": "Url1"
            },
            {
                "title": "Title2",
                "_type": "url",
                "url": "Url2"
            }
        ]
    }
    ```
- 채널로 불러왔을 때 예시
    ```json
    {
        "title": "Channel Name",
        "_type": "playlist",
        "entries": [
            {
                "title": "Channel Name - Videos",
                "_type": "playlist",
                "entries": [
                    {
                        "title": "Title1",
                        "_type": "url",
                        "url": "Url1"
                    },
                    {
                        "title": "Title2",
                        "_type": "url",
                        "url": "Url2"
                    }
                ]
            },
            {
                "title": "Channel Name - Shorts",
                "_type": "playlist",
                "entries": [
                    {
                        "title": "Title1",
                        "_type": "url",
                        "url": "Url1"
                    },
                    {
                        "title": "Title2",
                        "_type": "url",
                        "url": "Url2"
                    }
                ]
            },

        ]

    }
    ```
