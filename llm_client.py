import os
from dotenv import load_dotenv # type: ignore
import instructor # type: ignore
# import groq  # Make sure to install the groq package
from groq import AsyncGroq # type: ignore

load_dotenv()

# Initialize the Groq client
# groq_client = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")
groq_client = AsyncGroq(api_key=api_key)

# Use instructor to patch the Groq client
# llm = instructor.from_groq(groq_client)
llm = groq_client
