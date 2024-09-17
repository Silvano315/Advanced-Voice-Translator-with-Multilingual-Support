from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
import torch

class TranslatorModel:
    def __init__(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Device used: {device}")

        self.model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-it-en").to(device)
        self.tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-it-en")
        self.translator = pipeline("translation", model=self.model, tokenizer=self.tokenizer, device=0 if device == "cuda" else -1)

    def translate(self, text):
        translation = self.translator(text, max_length=512)[0]['translation_text']
        return translation