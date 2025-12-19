import unittest

from sapiopylib.rest.LlmManagerService import LlmManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.Llm import LlmChatInput, LlmChatOutput

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")

class FR53789Test(unittest.TestCase):
    manager: LlmManager

    def test_get_available_models(self):
        """Test getting available LLM models."""
        self.manager = LlmManager(user)
        # Expected models should be available on the server.
        # Note: This list may need to be updated as models are added/removed.
        expected_models = ["gpt-4o", "gpt-3.5-turbo"]
        
        models = self.manager.get_available_models()
        
        # Verify that expected models are present in the returned list
        for model in expected_models:
            self.assertIn(model, models)

    def test_send_chat(self):
        """Test sending a chat request."""
        self.manager = LlmManager(user)
        model_id = "gpt-3.5-turbo"
        chat_input = LlmChatInput(user_message="Hello")
        
        output = self.manager.send_chat(model_id, chat_input)

        self.assertIsInstance(output, LlmChatOutput)
        self.assertIsNotNone(output.content)
        self.assertTrue(len(output.content) > 0)
        self.assertIsNotNone(output.content[0].text)

    def test_count_tokens(self):
        """Test counting tokens."""
        self.manager = LlmManager(user)
        model_id = "gpt-3.5-turbo"
        chat_input = LlmChatInput(user_message="Hello")

        tokens = self.manager.count_tokens(model_id, chat_input)

        self.assertIsInstance(tokens, int)
        self.assertTrue(tokens > 0)

    def test_get_llm_answer(self):
        """Test getting a simple LLM answer."""
        self.manager = LlmManager(user)
        model_id = "gpt-3.5-turbo"
        chat_input = LlmChatInput(user_message="What is 2+2?")
        
        answer = self.manager.get_llm_answer(model_id, chat_input)

        self.assertIsInstance(answer, str)
        self.assertTrue(len(answer) > 0)
        self.assertIn("4", answer)

    def test_format_code_answer(self):
        """Test formatting a code answer."""
        self.manager = LlmManager(user)
        model_id = "gpt-3.5-turbo"
        code_answer = "def foo(): pass"
        
        # Note: We are testing that the endpoint works, not necessarily that the formatting is perfect,
        # as that depends on the LLM's response.
        result = self.manager.format_code_answer(model_id, code_answer)

        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
