import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob


def generate_wordcloud(df, text_column='text', font_path=None,
                       width=800, height=400, background_color='white'):
    """generate_wordcloud(df, 'text', font_path = "/content/NanumBarunGothic.ttf")"""

    # The input must be a string.
    # pandas dataframe --> list ---> string
    text_data = " ".join(df[text_column].dropna().astype(str).to_list())

    # Create a wordcloud
    wordcloud = WordCloud(
        width=width,
        height=height,
        background_color=background_color,
        font_path=font_path  # Specify the font path here
    ).generate(text_data)

    # Visualize the wordcloud
    plt.figure(figsize=(width / 100, height / 100))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()


def check_positive(*text: str) -> TextBlob:
    """.sentiment의 polarity가 1에 가까우면 긍정적, 반대면 부정적 문장"""
    blob = TextBlob(text)
    return blob
