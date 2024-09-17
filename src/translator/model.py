from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
import torch

class TranslatorModel:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Device used: {self.device}")

        self.models = {
            'english': self.load_model("Helsinki-NLP/opus-mt-it-en"),
            'spanish': self.load_model("Helsinki-NLP/opus-mt-it-es"),
            'french': self.load_model("Helsinki-NLP/opus-mt-it-fr"),
            'german': self.load_model("Helsinki-NLP/opus-mt-it-de")
        }
    
    def load_model(self, model_name):
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        return pipeline("translation", model=model, tokenizer=tokenizer, device=0 if self.device == "cuda" else -1)

    def translate(self, text, target_lang):
        if target_lang not in self.models:
            raise ValueError(f"Unsupported language: {target_lang}")
        
        translation = self.models[target_lang](text, max_length=512)[0]['translation_text']
        return translation