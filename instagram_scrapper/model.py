class User:
    def __init__(self, username):
        self.username = username
        self.posts = []

    def add_post(self, post):
        self.posts.append(post)

    def __str__(self):
        return f"User(username='{self.username}', posts={self.posts})"


class Post:
    def __init__(self, description, post_code):
        self.description = description
        self.post_code = post_code
        self.comments = []

    def add_comment(self, comment):
        self.comments.append(comment)

    def __str__(self):
        return f"Post(description='{self.description}', post_code={self.post_code}, comments={self.comments})"


class Comment:
    def __init__(self, text):
        self.text = text
        self.replies = []

    def add_reply(self, reply):
        self.replies.append(reply)

    def __str__(self):
        return f"Comment(text='{self.text}', replies={self.replies})"


class Reply:
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return f"Reply(text='{self.text}')"
