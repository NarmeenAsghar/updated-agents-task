class AsyncOpenAI:
    def __init__(self, api_key, base_url=None):
        self.api_key = api_key
        self.base_url = base_url

class OpenAIChatCompletionsModel:
    def __init__(self, model, openai_client):
        self.model = model
        self.openai_client = openai_client 