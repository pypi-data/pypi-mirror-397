#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   compiler.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK compiler module.
"""

import xgrammar as xgr
from pydantic import BaseModel
from transformers import AutoProcessor


def compile_grammar(processor: AutoProcessor, AssistantSchema: type[BaseModel]):
    """Compile a JSON schema grammar for structured generation.

    This function creates an xgrammar-compiled grammar from a Pydantic schema
    and HuggingFace processor, enabling structured output generation
    according to the schema constraints.

    Args:
        processor: HuggingFace processor with a tokenizer instance.
        AssistantSchema: Pydantic BaseModel representing the schema to enforce.

    Returns:
        CompiledGrammar: An xgrammar CompiledGrammar object usable for
        constrained decoding.

    """
    full_vocab_size = len(processor.tokenizer.get_vocab())
    config_vocab_size = processor.tokenizer.vocab_size
    actual_vocab_size = max(full_vocab_size, config_vocab_size)

    vocab_size = actual_vocab_size
    tokenizer_info = xgr.TokenizerInfo.from_huggingface(
        processor.tokenizer, vocab_size=vocab_size
    )
    compiler = xgr.GrammarCompiler(tokenizer_info, max_threads=8)
    compiled_grammar = compiler.compile_json_schema(AssistantSchema)
    return compiled_grammar


def compile_grammar_str(tokenizer, grammar_str: str):
    """Compile a custom grammar string into an xgrammar compiled grammar.

    This function takes a tokenizer and a grammar definition string, maps the
    vocabulary, and compiles the grammar for use in constrained decoding.

    Args:
        tokenizer: HuggingFace tokenizer instance.
        grammar_str: Grammar definition string in xgrammar syntax.

    Returns:
        CompiledGrammar: An xgrammar CompiledGrammar object usable for
        constrained decoding.

    """
    full_vocab_size = len(tokenizer.get_vocab())
    config_vocab_size = tokenizer.vocab_size
    actual_vocab_size = max(full_vocab_size, config_vocab_size)

    vocab_size = actual_vocab_size
    tokenizer_info = xgr.TokenizerInfo.from_huggingface(
        tokenizer, vocab_size=vocab_size
    )
    compiler = xgr.GrammarCompiler(tokenizer_info, max_threads=8)
    compiled_grammar = compiler.compile_grammar(grammar_str)
    return compiled_grammar
