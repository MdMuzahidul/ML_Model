from flask import Flask, request, jsonify
import pickle
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load the data and similarity matrix
books = pd.read_pickle('model/books_list.pkl')
similarity = pickle.load(open('model/similarity.pkl', 'rb'))

blogs = pd.read_pickle('model/blog_list.pkl')
similarity_blogs = pickle.load(open('model/similarity_blog.pkl', 'rb'))

# Helper function to recommend books by ISBN
def recommend_books(isbn, top_n=5):
    if isbn not in books['isbn'].values:
        return []
    idx = books[books['isbn'] == isbn].index[0]
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    recommended = books.iloc[[i[0] for i in sim_scores]][['isbn']]
    return recommended.to_dict(orient='records')

# Helper function to recommend blogs by title
def recommend_blogs(blog_title, top_n=5):
    if blog_title not in blogs['bookTitle'].values:
        return []
    idx = blogs[blogs['bookTitle'] == blog_title].index[0]
    sim_scores = list(enumerate(similarity_blogs[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    recommended = blogs.iloc[[i[0] for i in sim_scores]][['_id', 'bookTitle']].copy()

    # Convert ObjectId to string for JSON serialization
    recommended['_id'] = recommended['_id'].astype(str)
    
    return recommended.to_dict(orient='records')

@app.route('/recommend', methods=['GET'])
def recommend():
    isbn = request.args.get('isbn')
    if not isbn:
        return jsonify({'error': 'Please provide an ISBN number.'}), 400
    results = recommend_books(isbn)
    if not results:
        return jsonify({'error': 'Book not found or no recommendations.'}), 404
    return jsonify({'recommendations': results})

@app.route('/blog_recommend', methods=['GET'])
def blog_recommend():
    bookTitle = request.args.get('bookTitle')
    if not bookTitle:
        return jsonify({'error': 'Please provide a blog title.'}), 400
    results = recommend_blogs(bookTitle)
    if not results:
        return jsonify({'error': 'Blog not found or no recommendations.'}), 404
    return jsonify({'recommendations': results})


if __name__ == '__main__':
    app.run(debug=True)
