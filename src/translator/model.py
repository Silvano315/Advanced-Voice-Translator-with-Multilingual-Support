from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
import torch

class TranslatorModel:
    def __init__(self):
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

    def load_model(self, source_lang, target_lang):
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

    def translate(self, text, source_lang, target_lang):
        try:
            translator = self.load_model(source_lang, target_lang)
            translation = translator(text, max_length=512)[0]['translation_text']
            return translation
        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Translation error: {str(e)}"
            
    def get_supported_languages(self):
        languages = set()
        for source, target in self.language_pairs.keys():
            languages.add(source)
            languages.add(target)
        return sorted(list(languages))