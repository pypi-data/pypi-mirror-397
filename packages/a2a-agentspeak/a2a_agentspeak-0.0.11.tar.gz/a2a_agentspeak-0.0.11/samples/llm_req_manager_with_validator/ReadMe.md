# Scenario with a validator agent (human or LLM), a generator agent (with a LLM), and a manager agent.

This example shows a manager agent that talks with a LLM agent and 
to a validator agent (human or LLM based)
to build a list of requirements from a short specification.

## Validator agent

Several validator agents are shipped in the `a2a-acl` source repository. 
They are programmed in python, not in AgentSpeak. 
Run one of those.

* To run the user-in-the-loop agent :

    ```bash
    python3 PATH/TO/sample_agents/human_validation/run_validator_agent.py
    ```

* To run the LiteLLM validator agent :
    ```bash
    python3 PATH/TO/sample_agents/llm_validator_litellm_api/run_validator_agent.py
    ```
    This agent needs the `litellm` package installed. The example uses Mistral but you can change the LLM used. 
    A convenient key must be available.

* To run the Mistral validator agent :
    ```bash
    python3 PATH/TO/sample_agents/llm_validator_mistral_api/run_validator_agent.py
    ```
    
    This agent needs the `mistralai` package installed
    and the convenient key available.

_The validator agent should run on port 9999._

## Generator agent

The generator agent is an A2A/ACL agent programmed in AgentSpeak that uses an LLM to generate atomic requirements.
Each request to that agent generates exactly one requirement.

Run the generator agent :

```bash
  python3 run_requirement_generator.py 
```

_The generator agent should run on port 9990._

## Manager agent

The manager agents send requests to the generator agent, then submits the result to the validator agent.
After reply from the validator agent, according to the answer, the manager will either stop, or ask new inputs to the generator.

Run the manager agent:

```bash
    python3 run_manager.py 
```

_The manager agent should run on port 9981._

### Parameters

* The specification is defined in `manager.asl` .
