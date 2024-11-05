#EmoAnalyze: See what they feel

import streamlit as st
import requests
import validators
import os
import googleapiclient.discovery
import googleapiclient.errors
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('vader_lexicon')
import requests
from dotenv import load_dotenv
api_key = os.environ.get('API_KEY')

def configure():
    load_dotenv()
configure()

def validate_url(url):
    """Validates a URL using multiple checks."""

    if not url:
        return False, "Enter only youtube video url"

    if not validators.url(url):
        return False, "Invalid URL format."

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return False, f"Error fetching URL: {e}"

    return True, "URL is valid."

st.title("EmoAnalyze: See what they feel")
st.subheader("YouTube Comments Analysis")
url = st.text_input("Enter the youtube video url and hit Analyze button:")


def analyze():
    is_valid, message = validate_url(url)
    if is_valid:
        st.success(message)
        def get_video_comments(video_url):
            def extract_video_id(video_url):
                pattern = re.compile(r'(?:youtu\.be/|youtube\.com/(?:[^/]+/.*[?&]v=|v/|em(?:bed)?/|watch\?(?:.*&)?v=))(?P<videoid>[^"&?/ ]{11})')
                match = pattern.search(video_url)
                return match.group('videoid') if match else None

            video_id = extract_video_id(video_url)
            api_service_name = "youtube"
            api_version = "v3"
            #DEVELOPER_KEY=os.getenv("API_KEY")
            youtube = googleapiclient.discovery.build(
                api_service_name, api_version, developerKey=api_key)

            max_results = 100
            comments = []

            next_page_token = None

            while True:
                request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=max_results,
                    pageToken=next_page_token
                )
                response = request.execute()

                for item in response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']
                    comments.append([
                        comment['authorDisplayName'],
                        comment['likeCount'],
                        comment['textDisplay']
                    ])

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
            comments_df = pd.DataFrame(comments, columns=['author', 'like_count', 'text'])
            
            #drop null comments if any
            if(comments_df.isnull().sum().sum()!=0):
                comments_df.dropna(inplace=True)
            
            comments_df=comments_df.reset_index().drop('index',axis=1)
            
            
            comments_df['text']=comments_df['text'].str.replace("[^a-zA-Z#]", " ")
            
            comments_df['text']=comments_df['text'].apply(lambda x: re.sub(r'[^a-zA-Z 😊-🙏]', '', x))
            
            #removing emojies
            def remove_emojis(text):
                emoji_pattern = re.compile("["
                                        u"\U0001F600-\U0001F64F"  # emoticons
                                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                        u"\U0001F700-\U0001F77F"  # alchemical symbols
                                        u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                                        u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                                        u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                                        u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                                        u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                                        u"\U00002702-\U000027B0"  # Dingbats
                                        "]+", flags=re.UNICODE)
                return emoji_pattern.sub(r'', text)
            comments_df['text'] = comments_df['text'].apply(remove_emojis)
            
            #lowercase
            comments_df['text']=comments_df['text'].apply(lambda x:x.lower())
            
            #tokenization
            tokenized_comments= comments_df['text'].apply(lambda x: x.split())
            
            #lemmatization
            stop_words = set(stopwords.words('english'))
            wnl=WordNetLemmatizer()
            tokenized_comments.apply(lambda x: [wnl.lemmatize(i) for i in x if i not in stop_words])
            tokenized_comments.head()

            #combining the tokenized words
            for i in range(len(tokenized_comments)):
                tokenized_comments[i]=' '.join(tokenized_comments[i])
            comments_df['text']=tokenized_comments
            
            #sentiment-analysis
            sia=SentimentIntensityAnalyzer()
            comments_df['Sentiment Score']=comments_df['text'].apply(lambda x:sia.polarity_scores(x)['compound'])
            comments_df['Sentiment']=comments_df['Sentiment Score'].apply(lambda x: 'Positive' if x>0 else ('Negative' if x<0 else 'Neutral'))
            sentiment_counts=comments_df.Sentiment.value_counts()
            
            #pie-chart
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.pie(sentiment_counts, labels=sentiment_counts.index, autopct="%1.1f%%")
            ax.set_title('Sentiment Distribution', fontsize=8)

            st.header("Distribution of Positive, Negative, and Neutral Comments")
            st.pyplot(fig) 
            
            # #word-clouds
            # # Get all words
            # all_words = ' '.join([x for x in comments_df['text']])
            # all_pos_words = ' '.join([x for x in comments_df['text'][comments_df.Sentiment == 'Positive']])
            # all_neg_words = ' '.join([x for x in comments_df['text'][comments_df.Sentiment == 'Negative']])
            
            # # Create word clouds
            # wordcloud = WordCloud(width=430, height=300, random_state=21, max_font_size=55, font_path='fonts/DejaVuSans-Bold.ttf').generate(all_words)
            # wordcloud_posi = WordCloud(width=430, height=300, random_state=21, max_font_size=55, font_path='fonts/DejaVuSans-Bold.ttf').generate(all_pos_words)
            # wordcloud_negi = WordCloud(width=430, height=300, random_state=21, max_font_size=55, font_path='fonts/DejaVuSans-Bold.ttf').generate(all_neg_words)
            
            # # Convert to image using PIL
            # wordcloud_image = Image.fromarray(wordcloud.to_array())
            # wordcloud_posi_image = Image.fromarray(wordcloud_posi.to_array())
            # wordcloud_negi_image = Image.fromarray(wordcloud_negi.to_array())

            # st.header("Most Frequent Words")
            # st.write("All Words")
            # st.image(wordcloud_image)

            # st.write("Most frequent words in positive comments")
            # st.image(wordcloud_posi_image)
            
            # st.write("Most frequent words in negative comments")
            # st.image(wordcloud_negi_image)
            
            #Comments
            sorted_comments = comments_df.sort_values(by='Sentiment Score', ascending=True)
            
            most_negative_comments = sorted_comments.head(5)
            st.write("")
            st.header("Top 5 Negative Comments")
            sr=1
            for index, row in most_negative_comments.iterrows():
                with st.container(): 
                    st.write(f"Comment {sr}: {row['text']}")
                    sr+=1
            
            most_positive_comments = sorted_comments.tail(5)
            st.write("")
            st.header("Top 5 Positive Comments")
            sr=1
            for index, row in most_positive_comments.iterrows():
                with st.container(): 
                    st.write(f"Comment {sr}: {row['text']}")
                    sr+=1

        get_video_comments(url)
            
    else:
        st.error(message)

if st.button("Analyze"):
    analyze()
