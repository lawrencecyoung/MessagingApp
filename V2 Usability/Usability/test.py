import db
import models   

db.create_group_chat("groupchatpoopers2000", ["Jason", "Ash"])
groupchat = db.get_groupchat("groupchatpoopers2000")
print(groupchat.chat_id)
members = db.get_users_in_group_chat("groupchatpoopers2000")
for member in members:
    print(member.username)

db.save_groupchat_message(3, "Ash", "hello")
messages = db.get_groupchat_messages(3)
for message in messages:
    print(message.content)

groupchats = (db.get_user_groupchats("Ash"))
for i in groupchats:
    print(i.chat_id)

# # db.insert_user("Lawrence", "Y0un9@", "abcdefg", "Student")


# # Test create_article function
# db.create_article("Test Article5", "This is a test articled.", "Lawrence")
# article = db.get_article("Test Article5", "Lawrence")
# print(article.article_id)

# # Test create_comment function
# comment = db.create_comment(article.article_id, "Lawrence", "This is a test comment.")
# comment = db.create_comment(article.article_id, "Lawrence", "This is a test comment2.")

# if comment:
#     print("Comment created successfully.")
# else:
#     print("Failed to create comment.")

# comments = db.get_comments_for_article(article.article_id)
# for i in comments:
#     print(i.comment_id)

# print(article.article_id)

# db.modify_article(article.article_id, "Modified Title", "Modified Content")

# article = db.get_article("Modified Title", "Lawrence")
# # article = db.get_article("Test Article5", "Lawrence")

# print(article.title, article.content)
# print(article.article_id)

# comments = db.get_comments_for_article(article.article_id)
# for i in comments:
#     print(i.comment_id)

# db.delete_comment(1,1)
# comments = db.get_comments_for_article(article.article_id)
# for i in comments:
#     print(i.content)

# print(db.get_all_articles())

# db.delete_article(article.article_id)
# print(db.get_article("Modified Title", "Lawrence"))



