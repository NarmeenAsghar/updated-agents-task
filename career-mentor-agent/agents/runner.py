class RunConfig:
    def __init__(self, model=None, model_provider=None, tracing_disabled=True):
        self.model = model
        self.model_provider = model_provider
        self.tracing_disabled = tracing_disabled

class AgentRunner:
    def __init__(self, agents, initial_agent):
        self.agents = agents
        self.current_agent = initial_agent

    def run(self, history):
        agent = self.agents[self.current_agent]
        response, handoff = agent.respond(history)
        return response, handoff

    def switch_agent(self, agent_name):
        if agent_name in self.agents:
            self.current_agent = agent_name 

class Runner:
    @staticmethod
    def run_sync(starting_agent, input, run_config):
        # Placeholder for OpenAI Agent SDK runner logic
        # For now, just call the agent's respond method
        response, _ = starting_agent.respond(input)
        class Result:
            final_output = response
            def to_input_list(self):
                return input
        return Result() 