from typing import List, Any, Optional

from .core import ChatMessage, ChatModelCallable

    
def make_litellm_chat_model(
  model_name: str = "openai/gpt-4o-mini",
  trim: bool = True,
  trim_ratio: float = 0.75,
  max_input_tokens: Optional[int] = None,
  **default_kwargs: Any,
) -> ChatModelCallable:
  """
  Create a chat model callable using LiteLLM.
  
  Example:
    chat_model = make_litellm_chat_model(
      model_name="openai/gpt-4o-mini",
      temperature=0.2,
      max_tokens=512,
    )
    response = chat_model("Hello, how are you?")
  """
  from litellm import completion, CustomStreamWrapper, StreamingChoices # Import here to avoid hard dependency
  from litellm.utils import trim_messages
  
  def _call(messages: List[ChatMessage], **kwargs) -> str:
    combined_kwargs = {**default_kwargs, **kwargs, "stream": False} # Ensure stream is False for simplicity
    msgs = [{"role": msg.role, "content": msg.content} for msg in messages]
    if trim:
      if max_input_tokens is not None:
        msgs = trim_messages(
          msgs,
          model=model_name,
          max_tokens=max_input_tokens,
          trim_ratio=trim_ratio,
        )
      else:
        msgs = trim_messages(
          msgs,
          model=model_name,
          trim_ratio=trim_ratio,
        )
    
    response = completion(
      model=model_name,
      messages=msgs, # type: ignore
      **combined_kwargs
    )
    if isinstance(response, CustomStreamWrapper) or isinstance(response.choices[0], StreamingChoices): # Hypothetical check for streaming
      raise ValueError("Streaming responses are not supported in this callable.")
    
    # LiteLLM guarantees OpenAI-style response structure
    message = response.choices[0].message
    
    # message can be a dict or object with .content; handle both
    content = getattr(message, "content", None)
    if content is None and isinstance(message, dict):
      content = message.get("content", "")
    return content or ""
  
  return _call
