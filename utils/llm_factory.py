"""
Unified LLM Factory supporting Google Gemini and smart DemoChatModel fallback.
"""
import os
from typing import Optional, List, Any
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration

load_dotenv()


class DemoChatModel(BaseChatModel):
    """
    Deterministic simulated Chat Model for zero-setup offline demonstrations.
    Produces rich event planning recommendations matching state context.
    """
    model_name: str = "demo-event-planner"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        last_msg = messages[-1].content if messages else ""
        content_str = str(last_msg).lower()

        # Generate responsive simulated response based on context
        if "birthday" in content_str:
            reply = "[Birthday Party] Birthday party planning initiated! I've recorded the event details. What venue style or budget do you have in mind?"
        elif "workshop" in content_str or "college" in content_str:
            reply = "[Event Planning] Great! A college workshop/meetup requires good scheduling and audio-visual equipment. I've noted down your attendees and details."
        elif "task" in content_str or "venue" in content_str or "food" in content_str:
            reply = "[Task Tracker] Tasks updated in your event task pipeline! You can see them appended in your event state tracker."
        elif "budget" in content_str:
            reply = "[Budget Planner] Budget noted! A suggested allocation would be: 40% Venue & AV, 35% Catering/Food, 15% Materials/Decor, 10% Contingency."
        elif "guest" in content_str or "rahul" in content_str or "ahmed" in content_str:
            reply = "[Guest Registry] Guests have been added to your guest registry using the state reducer."
        elif "outdoor" in content_str or "indoor" in content_str:
            reply = "[Profile Memory] Preference saved to your Long-Term Profile! I will remember your event style preferences across all future event planning threads."
        else:
            reply = f"I've updated your event plan based on your input ('{last_msg}'). What would you like to coordinate next (tasks, guests, budget, or schedule)?"

        generation = ChatGeneration(message=AIMessage(content=reply))
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        return "demo-chat-model"


def get_llm(api_key: Optional[str] = None, model_name: Optional[str] = None) -> BaseChatModel:
    """
    Returns configured ChatGoogleGenerativeAI instance if Gemini API key is available,
    otherwise returns DemoChatModel.
    """
    key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    model = model_name or os.getenv("GEMINI_MODEL") or "gemini-3.6-flash"

    if key and key.strip():
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=model,
                google_api_key=key.strip(),
                temperature=0.7
            )
        except Exception as e:
            print(f"Warning: Could not initialize ChatGoogleGenerativeAI: {e}. Falling back to DemoChatModel.")
            return DemoChatModel()

    return DemoChatModel()
