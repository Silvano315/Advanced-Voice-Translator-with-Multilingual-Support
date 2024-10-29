from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
import torch
from typing import Dict, List, Set, Tuple, Union


class TranslatorModel:
    """
    A translation model class that handles multiple language pairs using pre-trained models.
    Supports dynamic model loading and GPU acceleration when available.
    """

    def __init__(self) -> None:
        """
        Initialize the translator model with device detection and language pair mappings.
        Models are loaded dynamically when needed to optimize memory usage.
        """

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Device used: {self.device}")
        
        self.language_pairs = {
            ('italian', 'english'): "Helsinki-NLP/opus-mt-it-en",
            ('english', 'italian'): "Helsinki-NLP/opus-mt-en-it",
            ('italian', 'spanish'): "Helsinki-NLP/opus-mt-it-es",
            ('spanish', 'italian'): "Helsinki-NLP/opus-mt-es-it",
            ('italian', 'french'): "Helsinki-NLP/opus-mt-it-fr",
            ('french', 'italian'): "Helsinki-NLP/opus-mt-fr-it",
            ('italian', 'german'): "Helsinki-NLP/opus-mt-it-de",
            ('german', 'italian'): "Helsinki-NLP/opus-mt-de-it"
        }
        
        self.loaded_models = {}

    def load_model(self, source_lang: str, target_lang: str) -> pipeline:
        """
        Load a translation model for a specific language pair if not already loaded.

        Args:
            source_lang: Source language name
            target_lang: Target language name

        Returns:
            Translation pipeline for the requested language pair

        Raises:
            ValueError: If the language pair is not supported
        """

        pair = (source_lang.lower(), target_lang.lower())
        if pair not in self.language_pairs:
            raise ValueError(f"Unsupported language pair: {pair}")
            
        if pair not in self.loaded_models:
            model_name = self.language_pairs[pair]
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.loaded_models[pair] = pipeline(
                "translation", 
                model=model, 
                tokenizer=tokenizer, 
                device=0 if self.device == "cuda" else -1
            )
        
        return self.loaded_models[pair]

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text from source language to target language.

        Args:
            text: Text to translate
            source_lang: Source language name
            target_lang: Target language name

        Returns:
            Translated text or error message if translation fails
        """

        try:
            translator = self.load_model(source_lang, target_lang)
            translation = translator(text, max_length=512)[0]['translation_text']
            return translation
        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Translation error: {str(e)}"
            
    def get_supported_languages(self) -> List[str]:
        """
        Get a sorted list of all supported languages.

        Returns:
            Sorted list of language names
        """
        languages = set()
        for source, target in self.language_pairs.keys():
            languages.add(source)
            languages.add(target)
        return sorted(list(languages))