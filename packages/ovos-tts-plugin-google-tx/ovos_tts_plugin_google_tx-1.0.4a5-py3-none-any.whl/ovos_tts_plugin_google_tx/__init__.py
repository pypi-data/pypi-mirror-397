from gtts import gTTS
from gtts.lang import tts_langs
from ovos_plugin_manager.templates.tts import TTS
from ovos_utils import classproperty
from ovos_utils.lang import standardize_lang_tag

# https://gtts.readthedocs.io/en/latest/module.html#localized-accents
REGIONAL_CONFIGS = {
    "en-AU": {"lang": "en", "tld": "com.au"},
    "en-GB": {"lang": "en", "tld": "co.uk"},
    "en-US": {"lang": "en", "tld": "us"},
    "en-CA": {"lang": "en", "tld": "ca"},
    "en-IN": {"lang": "en", "tld": "co.in"},
    "en-IE": {"lang": "en", "tld": "ie"},
    "en-ZA": {"lang": "en", "tld": "co.za"},
    "en-NG": {"lang": "en", "tld": "com.ng"},
    "fr-FR": {"lang": "fr", "tld": "fr"},
    "fr-CA": {"lang": "fr", "tld": "ca"},
    "pt-PT": {"lang": "pt-PT", "tld": "pt"},
    "pt-BR": {"lang": "pt", "tld": "com.br"},
    "es-ES": {"lang": "es", "tld": "es"},
    "es-US": {"lang": "es", "tld": "us"},
    "es-MX": {"lang": "es", "tld": "com.mx"},
    "zh-CN": {"lang": "zh-CN"},
    "zh-TW": {"lang": "zh-TW"}
}


class GoogleTranslateTTS(TTS):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, audio_ext="mp3")

    @classproperty
    def available_languages(cls) -> set:
        return set(tts_langs().keys())

    def get_tts(self, sentence, wav_file,
                lang=None, voice=None):
        """Fetch tts audio using gTTS.

        Args:
            sentence (str): Sentence to generate audio for
            wav_file (str): output file path
            lang (str): language of sentence
            voice (str): unsupported by this plugin
        Returns:
            Tuple ((str) written file, None)
        """
        lang = lang or self.lang
        lang = standardize_lang_tag(lang, macro=True)
        tld = self.config.get("tld", "com")
        if lang in REGIONAL_CONFIGS:
            tld = REGIONAL_CONFIGS[lang].get("tld", "com")
            lang = REGIONAL_CONFIGS[lang]["lang"]
        elif lang not in tts_langs():
            lang = lang.split("-")[0]
        tts = gTTS(text=sentence, lang=lang, tld=tld,
                   slow=self.config.get("slow", False),
                   lang_check=self.config.get("lang_check", False))
        tts.save(wav_file)
        return (wav_file, None)  # No phonemes


if __name__ == "__main__":
    e = GoogleTranslateTTS()
    ssml = "wakker worden"
    e.get_tts(ssml, f"nl-NL.mp3", lang="nl-NL")

    ssml = """Hello world"""
    for l in REGIONAL_CONFIGS:
        if l.startswith("en-"):
            e.get_tts(ssml, f"{l}.mp3", lang=l)

    ssml = """Olá Mundo! Bom dia alegria"""
    for l in REGIONAL_CONFIGS:
        if l.startswith("pt-"):
            e.get_tts(ssml, f"{l}.mp3", lang=l)
