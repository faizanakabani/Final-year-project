import os
from dotenv import load_dotenv # type: ignore
import instructor # type: ignore
# import groq  # Make sure to install the groq package
from groq import AsyncGroq # type: ignore

load_dotenv()

# Initialize the Groq client
# groq_client = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))
groq_client = AsyncGroq(api_key="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")

# Use instructor to patch the Groq client
# llm = instructor.from_groq(groq_client)
llm = groq_client
