#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   messages.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK inference messages module.
"""

from __future__ import annotations

from typing import Literal

from msgspec import Struct


class TextContent(Struct, kw_only=True):
    """Text content in a message.

    Attributes:
        type: Always "text" to indicate text content.
        text: The text content string.

    """

    text: str
    type: Literal["text"] = "text"


class ImageContent(Struct, kw_only=True):
    """Image content in a message (for local model inference).

    Attributes:
        type: Always "image" to indicate image content.
        image: Path to the image file or image data.

    """

    image: str
    type: Literal["image"] = "image"


class ImageURLContent(Struct, kw_only=True):
    """Image URL content in a message (for API-based inference).

    Attributes:
        type: Always "image_url" to indicate image URL content.
        image_url: Dictionary containing the image URL (or data URI).

    """

    type: Literal["image_url"] = "image_url"
    image_url: dict[str, str]


MessageContent = TextContent | ImageContent | ImageURLContent


class ChatMessage(Struct, kw_only=True):
    """A single message in a chat conversation.

    Attributes:
        role: The role of the message sender ("system", "user", or "assistant").
        content: The message content. Can be a string (for system messages)
            or a list of content items (for user/assistant messages with mixed content).

    Note:
        According to OpenAI API specifications:
        - System messages should use simple string content
        - User/assistant messages can use either string or list format for multimodal content

    """

    role: Literal["system", "user", "assistant"]
    content: str | list[MessageContent]


def create_system_message(text: str) -> dict[str, str]:
    """Create a system message with string content.

    Args:
        text: The system prompt text.

    Returns:
        Dictionary representing a system message with string content.

    """
    return {"role": "system", "content": text}


def create_user_message_with_image(
    image_path: str, text: str
) -> dict[str, str | list[dict[str, str]]]:
    """Create a user message with image and text content.

    Args:
        image_path: Path to the image file.
        text: The user prompt text.

    Returns:
        Dictionary representing a user message with image and text content.

    """
    return {
        "role": "user",
        "content": [
            {"type": "image", "image": image_path},
            {"type": "text", "text": text},
        ],
    }


def create_user_message_with_image_url(
    image_url: str, text: str
) -> dict[str, str | list[dict[str, str | dict[str, str]]]]:
    """Create a user message with image URL and text content.

    Useful for API-based services that accept base64-encoded images or URLs.

    Args:
        image_url: URL or data URI of the image (e.g., "data:image/jpeg;base64,...").
        text: The user prompt text.

    Returns:
        Dictionary representing a user message with image URL and text content.

    """
    return {
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": image_url}},
            {"type": "text", "text": text},
        ],
    }
