"""
Unit tests for LlamaGenerator (engine/generator/llm.py).
Follows TDD principles — testing public interface and contracts.
"""

import os
import pytest
from unittest.mock import MagicMock, patch
from engine.config import EngineConfig, LLMConfig
from engine.generator.llm import LlamaGenerator


class TestLlamaGeneratorPromptBuilding:
    """Test prompt formatting according to Llama 3 Chat Template."""

    def test_build_prompt_zero_shot(self):
        generator = LlamaGenerator(lazy_load=True)
        prompt = generator.build_prompt(
            question="How to configure ODBCINI for Streams?"
        )
        assert "<|start_header_id|>system<|end_header_id|>" in prompt
        assert "<|start_header_id|>user<|end_header_id|>" in prompt
        assert "How to configure ODBCINI for Streams?" in prompt
        assert "<|start_header_id|>assistant<|end_header_id|>" in prompt
        assert "Technical Support" in prompt or "technical" in prompt.lower()

    def test_build_prompt_with_context(self):
        generator = LlamaGenerator(lazy_load=True)
        context = "Technote swg21996508: Set environment variables with streamtool setproperty."
        prompt = generator.build_prompt(
            question="How to set application environment variables?",
            context=context
        )
        assert context in prompt
        assert "How to set application environment variables?" in prompt
        assert "<|start_header_id|>assistant<|end_header_id|>" in prompt


class TestLlamaGeneratorModelResolution:
    """Test model source resolution (Local folder vs Hugging Face Hub)."""

    def test_resolve_source_prefers_existing_local_dir(self, tmp_path):
        # Create a fake local model directory
        fake_model_dir = tmp_path / "fake_llama_techqa"
        fake_model_dir.mkdir()

        config = EngineConfig(
            llm=LLMConfig(
                model_path=str(fake_model_dir),
                model_name="AQUABOT/Llama-3.2-3B-TechQA"
            )
        )
        generator = LlamaGenerator(config=config, lazy_load=True)
        assert generator.model_source == str(fake_model_dir)
        assert generator.is_local is True

    def test_resolve_source_falls_back_to_huggingface(self):
        config = EngineConfig(
            llm=LLMConfig(
                model_path="non_existent_folder_path_xyz",
                model_name="AQUABOT/Llama-3.2-3B-TechQA"
            )
        )
        generator = LlamaGenerator(config=config, lazy_load=True)
        assert generator.model_source == "AQUABOT/Llama-3.2-3B-TechQA"
        assert generator.is_local is False


class TestLlamaGeneratorInference:
    """Test generate method with mock pipeline."""

    @patch("engine.generator.llm.AutoTokenizer.from_pretrained")
    @patch("engine.generator.llm.AutoModelForCausalLM.from_pretrained")
    def test_generate_returns_clean_response(self, mock_model, mock_tokenizer):
        # Setup mocks
        mock_tok_inst = MagicMock()
        mock_tok_inst.apply_chat_template.return_value = "<formatted_prompt>"
        mock_tok_inst.decode.return_value = "Run streamtool setproperty to set variables."
        mock_tokenizer.return_value = mock_tok_inst

        mock_mod_inst = MagicMock()
        mock_mod_inst.generate.return_value = MagicMock()
        mock_model.return_value = mock_mod_inst

        generator = LlamaGenerator(lazy_load=False)
        generator._tokenizer = mock_tok_inst
        generator._model = mock_mod_inst

        answer = generator.generate(
            question="How to configure variables?",
            context="Use streamtool command."
        )

        assert isinstance(answer, str)
        assert len(answer) > 0
        assert "streamtool" in answer
