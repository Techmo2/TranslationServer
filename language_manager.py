from lingua import Language, LanguageDetectorBuilder
from flores_codes import VALID_FLORES_CODES, ISO_TO_FLORES, FLORES_TO_ISO

class LanguageManager:
    def __init__(self, config):
        lingua_conf = config.get("lingua", {})
        builder = LanguageDetectorBuilder.from_all_languages()
        
        if lingua_conf.get("use_preloaded_language_models", True):
            builder.with_preloaded_language_models()
        if lingua_conf.get("use_low_accuracy_mode", False):
            builder.with_low_accuracy_mode()
            
        self.detector = builder.build()

    def validate_source_lang(self, text, source_lang):
        if source_lang == "auto":
            detection = self.detector.detect_language_of(text)
            if detection is None:
                raise ValueError("Could not detect language from text")
            iso_code = detection.iso_code_639_3.name.lower()
            if iso_code in ISO_TO_FLORES:
                return ISO_TO_FLORES[iso_code]
            # Try 639-1
            iso_code_1 = detection.iso_code_639_1.name.lower()
            if iso_code_1 in ISO_TO_FLORES:
                return ISO_TO_FLORES[iso_code_1]
            raise ValueError(f"Detected language {detection.name} is not supported")

        if source_lang in VALID_FLORES_CODES:
            return source_lang
        if source_lang in ISO_TO_FLORES:
            return ISO_TO_FLORES[source_lang]
        
        raise ValueError(f"Invalid source language: {source_lang}")

    def validate_target_lang(self, target_lang):
        if target_lang in VALID_FLORES_CODES:
            return target_lang
        if target_lang in ISO_TO_FLORES:
            return ISO_TO_FLORES[target_lang]
        
        raise ValueError(f"Invalid target language: {target_lang}")

    def flores_to_iso(self, flores_code):
        if flores_code in FLORES_TO_ISO:
            return FLORES_TO_ISO[flores_code]
        if flores_code in VALID_FLORES_CODES:
             return flores_code.split('_')[0]
        return flores_code

    def detect_language(self, text):
        confidence_values = self.detector.compute_language_confidence_values(text)
        # Return list of (language_code, confidence)
        results = []
        for cv in confidence_values:
            lang = cv.language
            conf = cv.value
            # Map back to ISO
            iso3 = lang.iso_code_639_3.name.lower()
            iso1 = lang.iso_code_639_1.name.lower() if lang.iso_code_639_1 else None
            
            # Prefer ISO1
            code = iso1 if iso1 else iso3
            results.append((code, conf))
        return results
