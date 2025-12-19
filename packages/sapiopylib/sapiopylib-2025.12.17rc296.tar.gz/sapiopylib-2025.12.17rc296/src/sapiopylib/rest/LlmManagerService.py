from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.Llm import LlmChatInput, LlmChatOutput
from sapiopylib.rest.utils.singletons import SapioContextManager


# FR-53789 - Created class.
class LlmManager(SapioContextManager):
    """
    REST API Service for managing LLM interactions and configurations.
    """
    def __init__(self, user: SapioUser):
        super().__init__(user)

    def get_available_models(self) -> list[str]:
        """
        Get a list of available LLM model IDs.

        :return: List of model IDs.
        """
        sub_path = '/llm/models'
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        return response.json()

    def send_chat(self, model_id: str, chat_input: LlmChatInput) -> LlmChatOutput:
        """
        Send a chat request to the LLM.

        :param model_id: The ID of the model to use.
        :param chat_input: The chat input.
        :return: The chat output.
        """
        sub_path = f"/llm/chat/{model_id}/send"
        payload = chat_input.to_json()
        response = self.user.post(sub_path, payload=payload)
        self.user.raise_for_status(response)
        return LlmChatOutput.from_json(response.json())

    def count_tokens(self, model_id: str, chat_input: LlmChatInput) -> int:
        """
        Count the number of tokens in the chat input.

        :param model_id: The ID of the model to use.
        :param chat_input: The chat input.
        :return: The number of tokens.
        """
        sub_path = f"/llm/chat/{model_id}/tokens"
        payload = chat_input.to_json()
        response = self.user.post(sub_path, payload=payload)
        self.user.raise_for_status(response)
        return int(response.json())

    def get_llm_answer(self, model_id: str, chat_input: LlmChatInput) -> str:
        """
        Get a simple text answer from the LLM.

        :param model_id: The ID of the model to use.
        :param chat_input: The chat input.
        :return: The answer text.
        """
        sub_path = f"/llm/chat/{model_id}/answer"
        payload = chat_input.to_json()
        response = self.user.post(sub_path, payload=payload)
        self.user.raise_for_status(response)
        return response.text

    def format_code_answer(self, model_id: str, code_answer: str) -> str:
        """
        Format a code answer from the LLM.

        :param model_id: The ID of the model to use.
        :param code_answer: The code answer to format.
        :return: The formatted code answer.
        """
        sub_path = f"/llm/chat/{model_id}/format-code"
        response = self.user.post(sub_path, payload=code_answer, is_payload_plain_text=True)
        self.user.raise_for_status(response)
        return response.text
