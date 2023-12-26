from pydantic import BaseModel
from typing import List, Union, Optional
from peewee import *
from playhouse.shortcuts import model_to_dict


import json
import uuid
import time

from apps.web.internal.db import DB


####################
# Chat DB Schema
####################


class Chat(Model):
    id = CharField(unique=True)
    user_id: CharField()
    title = CharField()
    chat = TextField()  # Save Chat JSON as Text
    timestamp = DateField()

    class Meta:
        database = DB


class ChatModel(BaseModel):
    id: str
    user_id: str
    title: str
    chat: dict
    timestamp: int  # timestamp in epoch


####################
# Forms
####################


class ChatForm(BaseModel):
    chat: dict


class ChatUpdateForm(ChatForm):
    id: str


class ChatTitleIdResponse(BaseModel):
    id: str
    title: str


class ChatTable:
    def __init__(self, db):
        self.db = db
        db.create_tables([Chat])

    def insert_new_chat(self, user_id: str, form_data: ChatForm) -> Optional[ChatModel]:
        id = str(uuid.uuid4())
        chat = ChatModel(
            **{
                "id": id,
                "user_id": user_id,
                "title": form_data.chat["title"],
                "chat": json.dump(form_data.chat),
                "timestamp": int(time.time()),
            }
        )

        result = Chat.create(**chat.model_dump())
        return chat if result else None

    def update_chat_by_id(self, id: str, chat: dict) -> Optional[ChatModel]:
        try:
            query = Chat.update(chat=json.dump(chat)).where(Chat.id == id)
            query.execute()

            chat = Chat.get(Chat.id == id)
            return ChatModel(**model_to_dict(chat))
        except:
            return None

    def get_chat_lists_by_user_id(
        self, user_id: str, skip: int = 0, limit: int = 50
    ) -> List[ChatModel]:
        return [
            ChatModel(**model_to_dict(chat))
            for chat in Chat.select(Chat.id, Chat.title)
            .where(Chat.user_id == user_id)
            .limit(limit)
            .offset(skip)
        ]

    def get_chat_by_id_and_user_id(self, id: str, user_id: str) -> Optional[ChatModel]:
        try:
            chat = Chat.get(Chat.id == id, Chat.user_id == user_id)
            return ChatModel(**model_to_dict(chat))
        except:
            return None

    def get_chats(self, skip: int = 0, limit: int = 50) -> List[ChatModel]:
        return [
            ChatModel(**model_to_dict(chat))
            for chat in Chat.select().limit(limit).offset(skip)
        ]


Chats = ChatTable(DB)