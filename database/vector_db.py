from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import VectorParams, Distance, PointStruct
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from datetime import datetime
import uuid
import os

load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
class QdrantStorage:
    def __init__(self, url: str = "http://localhost:6333", collection: str = "chatops" , dim=3072):
        self.client = QdrantClient(url=url, timeout=30)
        self.collection = collection
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

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
            points=[PointStruct(id=point_id, vector=vecotor, payload={"session_id": session_id, "full_conversation": memory_object, "timestamp": datetime.now()})]
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
        # sources = set()

        # print(result)

        for r in result.points:
            payload = getattr(r, "payload", None) or {}
            text = payload.get("full_conversation", "")
            # session_id = payload.get("session_id", "")
            if text:
                context.append(text)
                # sources.add(session_id)
            
        # if len(context) >= 1:
        #     context = context[0]

        target = []
        for c in context:
            for i in c:
                if isinstance(i, dict):
                    target.append(i)
        return target