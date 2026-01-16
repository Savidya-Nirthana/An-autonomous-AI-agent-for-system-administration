from typing import Literal, Any
import os
from dotenv import load_dotenv
from tenacity import Retrying, stop_after_attempt, wait_exponential, wait_random, retry_if_exception_type
from langchain_core.runnables import RunnableLambda
load_dotenv()



class LLMClient:
    def __init__(
        self,
        provider: Literal["google", "openai", "groq"],
        model: str,
        max_retries: int,
        backoff_base: float,
        backoff_jitter: float,
        hard_prompt_cap: int,
    ):
        self.provider = provider
        self.model = model
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.backoff_jitter = backoff_jitter
        self.hard_prompt_cap = hard_prompt_cap
        self.client = self._init_client()
        self.runnable = self._with_retry()
    

    def _init_client(self):
        
        if self.provider == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI
            api_key = os.getenv("GOOGLE_API_KEY")
            
            return ChatGoogleGenerativeAI(api_key=api_key, model=self.model)
            
        elif self.provider == "openai":
            from langchain_openai import ChatOpenAi
            api_key = os.getenv("OPENAI_API_KEY")

            return ChatOpenAi(api_key=api_key, model=self.model)
            
        elif self.provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            from langchain_groq import ChatGroq
            return ChatGroq(api_key=api_key, model=self.model)
            

    def _with_retry(self):
        retry_strategy = Retrying(
            stop=stop_after_attempt(self.max_retries),
            wait=(
                wait_exponential(multiplier=self.backoff_base, min=1, max=60)
                + wait_random(0, self.backoff_jitter)
            ),
            retry=retry_if_exception_type(Exception),
            reraise=True,
        )

    
        def invoke_with_retry(self, input):
            for attempt in retry_strategy:
                with attempt:
                    if attempt.retry_state.attempt_number > 1:
                        print(f"🔄 Retry attempt {attempt.retry_state.attempt_number}...")
                    
                    return self.client.invoke(input)
        

        return RunnableLambda(invoke_with_retry)
        

    
