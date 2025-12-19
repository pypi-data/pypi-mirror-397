from upif import guard

class UpifOpenAI:
    """
    Wrapper for OpenAI Client to automatically sanitize inputs and outputs.
    """
    def __init__(self, client):
        self.client = client
        self.chat = self.Chat(client.chat)

    class Chat:
        def __init__(self, original_chat):
            self.completions = self.Completions(original_chat.completions)

        class Completions:
            def __init__(self, original_completions):
                self.create = self._create_wrapper(original_completions.create)

            def _create_wrapper(self, original_create):
                def wrapper(*args, **kwargs):
                    # 1. Scan Input (Messages)
                    messages = kwargs.get("messages", [])
                    for msg in messages:
                        if "content" in msg and isinstance(msg["content"], str):
                            processed = guard.process_input(msg["content"])
                            # Check failure (refusal)
                            if processed == guard.input_guard.refusal_message:
                                # Return a mocked response object that refuses
                                return self._mock_refusal(processed)
                            msg["content"] = processed
                    
                    # 2. Call Original
                    response = original_create(*args, **kwargs)
                    
                    # 3. Scan Output (Response Content)
                    # Handle object access (obj.choices[0].message.content)
                    try:
                        content = response.choices[0].message.content
                        if content:
                            safe_content = guard.process_output(content)
                            response.choices[0].message.content = safe_content
                    except Exception:
                        pass # Streaming or different structure
                        
                    return response
                return wrapper

            def _mock_refusal(self, message):
                """Creates a fake OpenAI response object with the refusal message."""
                from types import SimpleNamespace
                return SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            message=SimpleNamespace(
                                content=message,
                                role="assistant"
                            )
                        )
                    ]
                )
