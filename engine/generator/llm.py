"""
Fine-tuned Llama LLM Wrapper & Generator.

Loads and runs inference with the fine-tuned Llama 3.2-3B model.
Supports both local model weights (models/Llama_TechQA) and HuggingFace Hub loading (AQUABOT/Llama-3.2-3B-TechQA).

Usage:
    from engine.generator.llm import LlamaGenerator

    generator = LlamaGenerator()
    answer = generator.generate(
        question="How to configure ODBCINI for Streams?",
        context="Retrieved technote text..."
    )
"""

import os
import logging
from typing import Optional, Generator, Union
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
import torch


from engine.config import EngineConfig, LLMConfig, default_config

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = (
    "You are a technical support assistant specialized in IBM products. "
    "Answer the user's technical question accurately and concisely "
    "based on your knowledge of IBM technotes and documentation."
)

RAG_SYSTEM_PROMPT = (
    "You are a technical support assistant specialized in IBM products. "
    "Answer the user's technical question accurately and concisely "
    "based on the provided IBM technote reference context. "
    "If the context does not contain enough information to resolve the issue, state clearly what is known and what is missing."
)


class LlamaGenerator:
    """Wrapper for fine-tuned Llama 3.2-3B model inference."""

    def __init__(
        self,
        config: Optional[Union[EngineConfig, LLMConfig]] = None,
        model_name_or_path: Optional[str] = None,
        device: Optional[str] = None,
        lazy_load: bool = True,
    ):
        """
        Initialize the generator.

        Args:
            config: Master EngineConfig or LLMConfig instance.
            model_name_or_path: Override model path or HuggingFace repo ID.
            device: Override compute device ('cuda', 'cpu', 'mps').
            lazy_load: If True, defer model weights loading until first generate() call.
        """
        self.config = config or default_config
        if isinstance(self.config, LLMConfig):
            self.llm_config = self.config
        elif hasattr(self.config, "llm"):
            self.llm_config = self.config.llm
        else:
            self.llm_config = default_config.llm

        self.device = device or self.llm_config.device
        if self.device == "cuda" and not torch.cuda.is_available():
            self.device = "cpu"

        # Resolve model source: Local folder vs Hugging Face Hub
        self.model_source, self.is_local = self._resolve_model_source(model_name_or_path)

        self._tokenizer = None
        self._model = None

        if not lazy_load:
            self._load_model()

    def _resolve_model_source(self, override_source: Optional[str] = None) -> tuple[str, bool]:
        """
        Resolve whether to load from local directory or Hugging Face Hub.

        Returns:
            (model_source_path_or_id, is_local_bool)
        """
        if override_source:
            is_local = os.path.exists(override_source) and os.path.isdir(override_source)
            return override_source, is_local

        # 1. Check if local model directory exists
        local_path = self.llm_config.model_path
        if local_path and os.path.exists(local_path) and os.path.isdir(local_path):
            logger.info(f"Using local model weights: {local_path}")
            return local_path, True

        # 2. Fallback to Hugging Face Hub
        hf_repo = self.llm_config.model_name
        logger.info(f"Local model not found. Using Hugging Face Hub model: {hf_repo}")
        return hf_repo, False


    def _load_model(self):
        """Load tokenizer and model weights into memory/VRAM."""
        if self._model is not None and self._tokenizer is not None:
            return

        logger.info(f"Loading tokenizer from: {self.model_source}")
        self._tokenizer = AutoTokenizer.from_pretrained(
            self.model_source,
            use_fast=True,
            trust_remote_code=True,
        )

        logger.info(f"Loading model weights from: {self.model_source} (device: {self.device})")
        torch_dtype = torch.bfloat16 if (self.device == "cuda" and torch.cuda.is_bf16_supported()) else (
            torch.float16 if self.device == "cuda" else torch.float32
        )

        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_source,
            torch_dtype=torch_dtype,
            device_map="auto" if self.device == "cuda" else None,
            trust_remote_code=True,
        )

        if self.device != "cuda" and hasattr(self._model, "to"):
            self._model = self._model.to(self.device)

        self._model.eval()
        logger.info("Model loaded successfully.")

    def build_prompt(self, question: str, context: Optional[str] = None) -> str:
        """
        Format user question and optional retrieval context into Llama 3 Chat Template.

        Args:
            question: The user's technical support query.
            context: Retrieved reference technotes (optional).

        Returns:
            Formatted chat template string ready for tokenization.
        """
        system_prompt = RAG_SYSTEM_PROMPT if context else DEFAULT_SYSTEM_PROMPT

        user_content = question.strip()
        if context and context.strip():
            user_content = (
                f"### Reference Context:\n{context.strip()}\n\n"
                f"### Question:\n{question.strip()}"
            )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        if self._tokenizer and hasattr(self._tokenizer, "apply_chat_template"):
            return self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )

        # Fallback manual Llama 3 chat template format
        formatted = (
            f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            f"{system_prompt}<|eot_id|>"
            f"<|start_header_id|>user<|end_header_id|>\n\n"
            f"{user_content}<|eot_id|>"
            f"<|start_header_id|>assistant<|end_header_id|>\n\n"
        )
        return formatted

    def generate(
        self,
        question: str,
        context: Optional[str] = None,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ) -> str:
        """
        Generate answer for a technical question.

        Args:
            question: Technical query string.
            context: Optional context from technotes.
            max_new_tokens: Maximum tokens to generate (default from config).
            temperature: Sampling temperature (default from config).
            top_p: Nucleus sampling probability (default from config).

        Returns:
            Clean text answer string.
        """
        self._load_model()

        prompt = self.build_prompt(question=question, context=context)
        inputs = self._tokenizer(prompt, return_tensors="pt")

        if self.device == "cuda":
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        elif hasattr(inputs, "to"):
            inputs = inputs.to(self.device)

        llm_cfg = self.config.llm if hasattr(self.config, "llm") else (self.config if hasattr(self.config, "max_new_tokens") else self.llm_config)
        gen_tokens = max_new_tokens or getattr(llm_cfg, "max_new_tokens", 256) or self.llm_config.max_new_tokens
        gen_temp = temperature if temperature is not None else getattr(llm_cfg, "temperature", 0.7)
        gen_top_p = top_p if top_p is not None else getattr(llm_cfg, "top_p", 0.9)


        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=gen_tokens,
                temperature=gen_temp,
                top_p=gen_top_p,
                do_sample=gen_temp > 0,
                pad_token_id=self._tokenizer.eos_token_id,
            )

        input_len = inputs["input_ids"].shape[1]
        new_tokens = outputs[0][input_len:]
        answer = self._tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        return answer

    def generate_stream(
        self,
        question: str,
        context: Optional[str] = None,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ) -> Generator[str, None, None]:
        """
        Generate answer token-by-token as a streaming generator.
        """
        self._load_model()

        import threading

        prompt = self.build_prompt(question=question, context=context)
        inputs = self._tokenizer(prompt, return_tensors="pt")
        if self.device == "cuda":
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        elif hasattr(inputs, "to"):
            inputs = inputs.to(self.device)

        streamer = TextIteratorStreamer(self._tokenizer, skip_prompt=True, skip_special_tokens=True)

        gen_tokens = max_new_tokens or self.config.llm.max_new_tokens
        gen_temp = temperature if temperature is not None else self.config.llm.temperature
        gen_top_p = top_p if top_p is not None else self.config.llm.top_p

        generation_kwargs = dict(
            **inputs,
            streamer=streamer,
            max_new_tokens=gen_tokens,
            temperature=gen_temp,
            top_p=gen_top_p,
            do_sample=gen_temp > 0,
            pad_token_id=self._tokenizer.eos_token_id,
        )

        thread = threading.Thread(target=self._model.generate, kwargs=generation_kwargs)
        thread.start()

        for new_text in streamer:
            yield new_text

        thread.join()
