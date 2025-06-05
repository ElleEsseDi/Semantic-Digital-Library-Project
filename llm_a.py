import json
import os
from typing import Literal

import ollama
import requests
from dotenv import load_dotenv


class LSDAgentInterface:

    def __init__(
        self,
        mode: Literal["remote", "local"],
        model: str,
        sys_prompt,
        settings: dict | None = None,
        key: str | None = None,
        endpoint: str | None = "https://openrouter.ai/api/v1/chat/completions",
    ):

        self.model = model
        self.sys_prompt = sys_prompt
        self.settings = settings

        # Remote mode
        if mode == "remote":

            if not (key and endpoint):

                raise TypeError(
                    "Specify a valid API key and an endpoint if you want to use a remote model"
                )

            # Storing attributes to perform API calls to a remote LLM agent service
            self.key = key
            self.endpoint = endpoint
            self.headers = {
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            }
        # Local mode
        else:
            if (
                self._check_ollama_reqs()
            ):  # checking that ollama is running locally and the model was downloaded (pulled)
                self.client = ollama.Client()

        self.mode = mode

    def _check_ollama_reqs(self):

        try:
            models_list = [info.model for info in ollama.list()["models"]]
            if not self.model in models_list:
                print(
                    f"Model {self.model} not found. Please pull it with 'ollama pull {self.model}'"
                )
                return False
            return True
        except requests.exceptions.ConnectionError:
            print("Ollama is not running. Please start Ollama service.")
            return False

    def remote_call(self, query, contexts):

        if self.mode != "remote":
            raise AttributeError(
                "Instance was not set to be used as a remote API interface"
            )

        # Fallback models
        fallback_models = {
            "qwen/qwen3-235b-a22b:free",
            "deepseek/deepseek-r1:free",
            "google/gemma-3-27b-it:free",
            "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
        }

        if self.model in fallback_models:
            fallback_models.remove(self.model)

        formatted_query, formatted_contexts = self._format_data(
            query=query, contexts=contexts
        )

        payload = {
            "model": self.model,  # chosen model
            "messages": [
                {"role": "system", "content": self.sys_prompt},
                {"role": "user", "content": formatted_query},
                {"role": "user", "content": formatted_contexts},
            ],
            "max_tokens": 5000,
            "temperature": 0.3,
            "top_k": 40,
            "top_p": 0.8,
            "models": list(fallback_models),
        }

        # adding settings, if specified, to payload
        if self.settings:
            for k, v in self.settings.items():
                payload[k] = v

        response = requests.post(
            self.endpoint, headers=self.headers, data=json.dumps(payload)
        )
        print(response.text)
        response.raise_for_status()

        api_response = response.json()

        if api_response.get("choices") and len(api_response["choices"]) > 0:
            agent_reply = api_response["choices"][0]["message"]["content"]
            if "<think>" in agent_reply:
                agent_reply = agent_reply.split("</think>")[
                    1
                ]  # getting only the response from reasoning models, cutting out the CoT
            print("AI Response:")
            print(agent_reply)
        else:
            agent_reply = None
            print("No response choices found.")
            print("API Response:", api_response)

        return agent_reply

    def local_call(self, query, contexts):

        if self.mode != "local":
            raise AttributeError(
                "Instance was not set to be used in as a local API interface"
            )

        formatted_query, formatted_contexts = self._format_data(query, contexts)
        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": self.sys_prompt},
                {"role": "user", "content": formatted_query},
                {"role": "user", "content": formatted_contexts},
            ],
            options=self.settings,
        )
        response_text = response["message"]["content"]
        if "<think>" in response_text:
            response_text = response_text.split("</think>")[
                1
            ]  # getting only the response from reasoning models, cutting out the CoT
        print(response_text)

        return response_text

    def _format_data(self, query, contexts) -> tuple:
        f_contexts = (
            "<AVAILABLE INFORMATION>" + "\n".join(contexts)
            if contexts
            else "***NO INFO***" + "</AVAILABLE INFORMATION>"
        )
        f_query = "<USER QUERY>" + query + "</USER QUERY>"

        return f_query, f_contexts


if __name__ == "__main__":

    load_dotenv()  # loading .env file containing API key

    # Getting prompt
    with open("prompt.txt", mode="r", encoding="utf-8") as f:
        sys_prompt = f.read()

    # Getting API key
    key = os.environ.get("API_KEY")
    if key is None:
        raise TypeError("key is None")

    # Initalizing agent interface
    agent = LSDAgentInterface(
        mode="remote",
        model="qwen/qwen3-235b-a22b:free",  # deepseek/deepseek-r1:free
        sys_prompt=sys_prompt,
        key=key,
    )

    agent.remote_call(
        query="What is the capital of Italy?",
        contexts="""The capital of Italy is Rome\n
                    Rome was founded in 1922\n
                    The pope resides in Rome\n""",
    )
    response = requests.get(
        url="https://openrouter.ai/api/v1/auth/key",
        headers={"Authorization": f"Bearer {key}"},
    )
