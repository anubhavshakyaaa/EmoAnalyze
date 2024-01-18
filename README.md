# EmoAnalyze: See what they feel
A YouTube Comments Sentiment Analysis

## Description
EmoAnalyze is a Python-based project that aims to analyze sentiments in YouTube comments. The project utilizes the Streamlit library for the user interface and integrates with natural language processing (NLP) techniques for sentiment analysis.

## Key Features
**YouTube Comments Analysis:** Users can input a YouTube video URL, and the system performs sentiment analysis on the associated comments by fetching the comments using the Google YouTube API V3.

**Text Preprocessing:** The project includes text preprocessing steps such as tokenization, lemmatization, and stopword removal to enhance the quality of the sentiment analysis.

**Interactive User Interface:** Streamlit is used to create an interactive web-based user interface, making it easy for users to input URLs and view sentiment analysis results.

## Dependencies
Python

Streamlit

NLTK (Natural Language Toolkit)

Other required libraries

## How to Use
-Clone the repository to your local machine.

-Install the required dependencies using ```pip install -r requirements.txt```

-Add you YouTube API Key in .env file ```API_KEY=your_api_key```

-Run the Streamlit app using ```streamlit run your_app_name.py```

Open your web browser and navigate to the specified local host to interact with the application.

## Contributions
Contributions are welcome! If you find any issues or have ideas for improvements, feel free to create an issue or submit a pull request.

## License
This project is licensed under the [MIT License](LICENSE).
