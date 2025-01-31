import praw
import google.generativeai as genai
from typing import List, Dict
import time

# Initialize Reddit client
reddit = praw.Reddit(
    client_id="hC7NMet3OC0yKNGGFvRENQ",
    client_secret="6jBGaDVoAIsHvkw0dXI7OZKyJe41ZA",
    user_agent="script:my_reddit_scraper:v1.0 (by /u/jass6122)"
)

# Initialize Gemini
genai.configure(api_key='AIzaSyDUF1FsfSV3JapEl8XzTaX0IVY6D6e91nA')
model = genai.GenerativeModel('gemini-1.5-flash')

def get_post_with_comments(post) -> Dict:
    """Collect a post and its top comments"""
    post.comments.replace_more(limit=0)  # Remove CommentForest instances
    comments = []
    
    # Get top 10 comments
    for comment in post.comments[:10]:
        comments.append({
            'body': comment.body,
            'score': comment.score
        })
    
    return {
        'title': post.title,
        'body': post.selftext,
        'score': post.score,
        'url': post.url,
        'comments': comments
    }

def analyze_sentiment(post_data: Dict) -> Dict:
    """Send post and comments to Gemini for sentiment analysis"""
    
    # Construct the prompt
    prompt = f"""Analyze the sentiment of this Reddit post and its comments:
    
Post Title: {post_data['title']}
Post Body: {post_data['body']}
Post URL: {post_data['url']}

Top Comments:
"""
    
    for i, comment in enumerate(post_data['comments'], 1):
        prompt += f"\n{i}. {comment['body']}\n"

    prompt += "\nProvide a brief sentiment analysis of both the post and the overall comment sentiment."

    try:
        response = model.generate_content(prompt)
        return {
            'post_data': post_data,
            'sentiment_analysis': response.text
        }
    except Exception as e:
        print(f"Error in Gemini API call: {e}")
        return None

def main():
    subreddit = reddit.subreddit('wallstreetbets')
    
    # Collect and analyze posts
    for post in subreddit.hot(limit=5):  # Reduced to 5 posts to manage API costs
        # Collect post and comments
        post_data = get_post_with_comments(post)
        
        # Analyze sentiment
        analysis = analyze_sentiment(post_data)
        
        if analysis:
            print(f"\n{'='*50}")
            print(f"Post: {analysis['post_data']['title']}")
            print(f"\nSentiment Analysis:")
            print(analysis['sentiment_analysis'])
            
        # Sleep to respect rate limits
        time.sleep(2)

if __name__ == "__main__":
    main()