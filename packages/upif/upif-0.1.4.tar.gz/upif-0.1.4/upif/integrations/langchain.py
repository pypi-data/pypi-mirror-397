from upif import guard

class ProtectChain:
    """
    Wrapper for a LangChain Runnable (Chain/Model) to secure invocations.
    """
    def __init__(self, chain):
        self.chain = chain
        
    def invoke(self, input_data, config=None, **kwargs):
        # 1. Scan numeric/string inputs
        if isinstance(input_data, str):
            safe_input = guard.process_input(input_data)
            if safe_input == guard.input_guard.refusal_message:
                 return safe_input 
            input_data = safe_input
            
        elif isinstance(input_data, dict):
            for k, v in input_data.items():
                if isinstance(v, str):
                    safe_v = guard.process_input(v)
                    if safe_v == guard.input_guard.refusal_message:
                        return f"Refused: Input '{k}' triggered security."
                    input_data[k] = safe_v

        # 2. Invoke Chain
        result = self.chain.invoke(input_data, config, **kwargs)
        
        # 3. Scan Output (Primitive only for now)
        if isinstance(result, str):
            return guard.process_output(result)
        # Handle AIMessage object
        if hasattr(result, 'content') and isinstance(result.content, str):
            result.content = guard.process_output(result.content)
            
        return result
