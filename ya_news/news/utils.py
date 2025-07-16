from news.models import Comment


def comment_counter():
    comment_count = Comment.objects.count()
    return comment_count
