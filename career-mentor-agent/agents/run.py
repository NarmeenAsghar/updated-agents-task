class RunConfig:
    def __init__(self, model=None, model_provider=None, tracing_disabled=True):
        self.model = model
        self.model_provider = model_provider
        self.tracing_disabled = tracing_disabled 