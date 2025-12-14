from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, NllbTokenizer
import torch
from language_manager import LanguageManager


class Translator:
    def __init__(self, config):
        trans_conf = config.get("translator", {})
        model_id = trans_conf.get("model_id", "facebook/nllb-200-distilled-600M")
        cpu_only = trans_conf.get("cpu_only", False)
        
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        if cpu_only:
             self.device = torch.device("cpu")
        else:
             self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
             
        self.model = self.model.to(self.device)
        self.language_manager = LanguageManager(config)

    # source_lang and target_lang are BCP47 format
    def translate_text(self, text, source_lang, target_lang):
        src = self.language_manager.validate_source_lang(text, source_lang)
        tgt = self.language_manager.validate_target_lang(target_lang)

        self.tokenizer.src_lang = src
        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
        translated_tokens = self.model.generate(
            **inputs, forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(tgt), max_length=30,
        )
        return self.tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
