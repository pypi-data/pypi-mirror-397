"""
Streaming Response Support for GUI
Enables real-time LLM response streaming in Electron app
"""
from typing import Generator, Optional


def stream_chat(backend, model: str, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
    """
    Stream chat response from LLM backend
    
    Args:
        backend: LLM backend instance (Ollama, Llamafile, etc.)
        model: Model name to use
        prompt: User prompt
        system_prompt: Optional system prompt
    
    Yields:
        Text chunks as they arrive from LLM
    """
    try:
        # Most backends support stream=True parameter
        response = backend.chat(
            prompt=prompt,
            model=model,
            system_prompt=system_prompt,
            temperature=0.7,
            stream=True
        )
        
        # If response is a generator (streaming), yield chunks
        if hasattr(response, '__iter__') and not isinstance(response, str):
            for chunk in response:
                if isinstance(chunk, dict) and 'content' in chunk:
                    yield chunk['content']
                elif isinstance(chunk, str):
                    yield chunk
        else:
            # If not streaming, just yield the full response
            yield response
            
    except Exception as e:
        yield f"Error: {str(e)}"


def format_stream_event(chunk: str) -> str:
    """
    Format chunk as Server-Sent Event (SSE) for FastAPI
    
    Args:
        chunk: Text chunk from LLM
    
    Returns:
        SSE-formatted string
    """
    # Escape newlines in chunk
    escaped = chunk.replace('\n', '\\n')
    return f"data: {escaped}\n\n"
