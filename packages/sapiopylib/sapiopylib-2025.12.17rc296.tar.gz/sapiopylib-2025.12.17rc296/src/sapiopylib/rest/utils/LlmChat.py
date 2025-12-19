from sapiopylib.rest.LlmManagerService import LlmManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.Llm import LlmMessage, LlmMessageRole, LlmChatInput


class LlmChat:
    user: SapioUser
    llm_manager: LlmManager

    model: str
    system_prompt: str | None
    message_history: list[LlmMessage]
    temperature: float | None
    max_output_tokens: int | None

    def __init__(self, user: SapioUser, model: str, system_prompt: str | None = None,
                 message_history: list[LlmMessage] | None = None, temperature: float | None = None,
                 max_output_tokens: int | None = None):
        """
        :param user: The user to send the requests with.
        :param model: The model to send the requests to.
        :param system_prompt: The system prompt to use when sending messages.
        :param message_history: A pre-existing message history to start the conversation with. If not provided, the
            conversation will be started with a blank message history.
        :param temperature: The temperature of the model. If not provided, the model will use its default.
        :param max_output_tokens: The maximum number of output tokens that the model will respond with. If not provided,
            the model will use its default.
        """
        self.user = user
        self.llm_manager = LlmManager(user)

        self.model = model
        self.system_prompt = system_prompt
        self.message_history = [] if message_history is None else message_history
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

    def send_chat(self, message: str) -> str:
        """
        Send a message to the model. The message input and the LLM's response will be saved to this chat's
        message history.

        :param message: The message to send.
        :return: The response from the model.
        """
        self.message_history.append(LlmMessage(LlmMessageRole.USER, message))
        answer: str = self.llm_manager.get_llm_answer(self.model, self._build_input())
        self.message_history.append(LlmMessage(LlmMessageRole.ASSISTANT, answer))
        return answer

    def count_conversation_tokens(self, message: str | None = None) -> int:
        """
        Count the number of tokens that the conversation takes up for the model.

        :param message: An optional message to add to the conversation before counting. This message is not permanently
            saved to the conversation.
        :return: The token size of the current conversation.
        """
        chat_input: LlmChatInput = self._build_input()
        if message is not None:
            chat_input.messages.append(LlmMessage(LlmMessageRole.USER, message))
        return self.llm_manager.count_tokens(self.model, chat_input)

    def _build_input(self) -> LlmChatInput:
        return LlmChatInput(
            system=self.system_prompt,
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
            messages=self.message_history,
        )
