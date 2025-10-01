import sqlite3
import re
def strip_html_tags(text):
    text = re.sub(r'<.*?>', '', text)
    text = text.replace('&nbsp;', ' ')
    text = re.sub(r'\s+$', '', text)
    return text
def show_posts():
    with sqlite3.connect('agro.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT posts.post_id,posts.title, posts.description, farmers.userid, posts.likes
            FROM posts
            JOIN farmers ON posts.email = farmers.email
            ORDER BY posts.created_at DESC
        ''')
        posts = []
        for row in cursor.fetchall():
            post = {
                'post_id': row[0],
                'title': row[1],
                'description': row[2],
                'userid': row[3],
                'likes': row[4],
            }
            posts.append(post)
        conn.commit()
    return posts
def trending_posts():
    with sqlite3.connect('agro.db') as conn:
        cursor=conn.cursor()
        cursor.execute('''
            SELECT posts.post_id,posts.title, posts.description, farmers.userid, posts.likes
            FROM posts
            JOIN farmers ON posts.email = farmers.email
            ORDER BY likes DESC''')  
        posts = []
        for row in cursor.fetchall():
            post = {
                'post_id': row[0],
                'title': row[1],
                'description': row[2],
                'userid': row[3],
                'likes': row[4],
            }
            posts.append(post)
        conn.commit()
    return posts
def insert_post(title,description,email):
    try:
        plain_description = strip_html_tags(description)  # Remove HTML tags
        with sqlite3.connect('agro.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO posts (email, title, description)
                VALUES (?, ?, ?)
            ''', (email, title, plain_description))
            conn.commit()
        return "Post created successfully."
    except sqlite3.Error as e:
        return f"An error occurred: {e}"
def add_comment_db(post_id, comment, email):
    with sqlite3.connect('agro.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO comments (post_id, email, comment) VALUES (?, ?, ?)', (post_id, email, comment))
        conn.commit()
    return True
def fetch_comments_db(post_id):
    with sqlite3.connect('agro.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT email, comment FROM comments WHERE post_id = ?", (post_id,))
        return [{'user': row[0], 'text': row[1]} for row in cursor.fetchall()]
def update_reaction_db(post_id, user_email):
    with sqlite3.connect('agro.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM posts WHERE post_id = ?", (post_id,))
        if cursor.fetchone() is None:
            return None  # Return None if post does not exist
        cursor.execute("SELECT 1 FROM liked_posts WHERE post_id = ? AND user_email = ?", (post_id, user_email))
        if cursor.fetchone():
            return "already_liked" 
        cursor.execute("INSERT INTO liked_posts (post_id, user_email) VALUES (?, ?)", (post_id, user_email))
        cursor.execute("UPDATE posts SET likes = likes + 1 WHERE post_id = ?", (post_id,))
        conn.commit()
        cursor.execute("SELECT likes FROM posts WHERE post_id = ?", (post_id,))
        return cursor.fetchone()[0]
