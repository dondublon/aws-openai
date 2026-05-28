from chat_store import ChatStore
from datetime import datetime, timezone
from uuid import uuid4
import boto3
from boto3.resources.base import ServiceResource 
from boto3.dynamodb.conditions import Key   
from config import DYNAMODB_CONVERSATIONS_TABLE, DYNAMODB_MESSAGES_TABLE    
class _DynamoChatStore(ChatStore):
    def __init__(
        self,
        conversations_table: str,
        messages_table: str
    ):
        dynamodb_resource = boto3.resource("dynamodb")
        self._conversations = dynamodb_resource.Table(conversations_table)
        self._messages = dynamodb_resource.Table(messages_table)

    
    def create_session(self, name:str = None) -> tuple[str, str]:
        session_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        if not name:
            name = session_id
        self._conversations.put_item(
            Item={
                "session_id": session_id,
                "next_seq": 0,
                "created_at": now,
                "updated_at": now,
                "name": name
            }
        )
        return session_id, name

    def get_messages(self, session_id: str) -> list[dict]:
        response = self._messages.query(
            KeyConditionExpression=Key("session_id").eq(session_id)
            
        )
        items = response.get("Items", [])
        return [
    {
        "role": item["role"],
        "content": item["content"],
        **(
            {"tool_call_id": item["tool_call_id"]}
            if "tool_call_id" in item
            else {}
        ),
    }
    for item in items
]

    def append_message(self, session_id: str, role: str, content: str, tool_call_id: str | None = None) -> None:
        now = datetime.now(timezone.utc).isoformat()
        counter = self._conversations.update_item(
            Key={"session_id": session_id},
            UpdateExpression=(
                "SET updated_at = :updated "
                "ADD next_seq :incr"
            ),
            ExpressionAttributeValues={
                ":updated": now,
                ":incr": 1,
            },
            ReturnValues="UPDATED_NEW",
        )["Attributes"]["next_seq"]
        self._messages.put_item(
            Item={
                "session_id": session_id,
                "seq": counter,
                "role": role,
                "content": content,
                "tool_call_id":tool_call_id,
                "created_at": now
            }
        )
chatStore:ChatStore = _DynamoChatStore(DYNAMODB_CONVERSATIONS_TABLE, DYNAMODB_MESSAGES_TABLE)        