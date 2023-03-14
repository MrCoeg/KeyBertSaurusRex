import json

from instagram_scrapper.model import *


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, User):
            return {
                "username": obj.username,
                "posts": obj.posts
            }
        elif isinstance(obj, Post):
            return {
                "description": obj.description,
                "post_code": obj.post_code,
                "comments": obj.comments,
            }
        elif isinstance(obj, Comment):
            return {
                "text": obj.text,
                "replies": obj.replies,
            }
        elif isinstance(obj, Reply):
            return {
                "text": obj.text,
            }
        else:
            return super().default(obj)
