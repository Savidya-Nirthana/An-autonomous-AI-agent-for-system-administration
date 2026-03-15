from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import VectorParams, Distance, PointStruct
from src.infrastructure.llm import get_default_embedding
from datetime import datetime
import uuid
from src.infrastructure.config import EMBEDDING_DIM
from paths import QDRANT_DATA_DIR


class QdrantStorage:
    def __init__(self, collection: str = "chatops", dim=EMBEDDING_DIM):
        # Local embedded mode — no Docker/server needed
        QDRANT_DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.client = QdrantClient(path=str(QDRANT_DATA_DIR))
        self.collection = collection
        self.embeddings = get_default_embedding()

        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
            )

     
    def upsert(self, session_id: str, user_test: str, assistant_text: str):
        memory_object = [
            {
                "role": "user", "content": user_test
            },
            {
                "role": "assistant", "content": assistant_text
            }
        ]

        conbine_text = f"User: {user_test}\nAssistant: {assistant_text}"
        vecotor  = self.embeddings.embed_query(conbine_text)


        point_id = str(uuid.uuid4())
        
        
        self.client.upsert(
            collection_name=self.collection,
            points=[PointStruct(id=point_id, vector=vecotor, payload={"session_id": session_id, "full_conversation": memory_object, "timestamp": datetime.now().isoformat()})]
        )   


    def search(self, session_id: str, query: str, k: int = 5):
        result = self.client.query_points(
            collection_name=self.collection,
            query=self.embeddings.embed_query(query),
            with_payload=True,
            limit=k,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="session_id",
                        match=models.MatchValue(value=session_id) 
                    )
                ]
            ),
        )

        context = []

        for r in result.points:
            payload = getattr(r, "payload", None) or {}
            text = payload.get("full_conversation", "")
            if text:
                context.append(text)
            
        target = []
        for c in context:
            for i in c:
                if isinstance(i, dict):
                    target.append(i)
        return target