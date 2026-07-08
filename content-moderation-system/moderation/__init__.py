"""
The 'moderation' package holds all the logic that decides whether a piece
of content is okay, needs review, or should be rejected.

It's split into two files:
- text_moderator.py  -> analyzes text content
- image_moderator.py -> analyzes image content

Keeping them separate mirrors the real Azure design, where Azure AI Language
handles text and Azure AI Vision handles images.
"""
