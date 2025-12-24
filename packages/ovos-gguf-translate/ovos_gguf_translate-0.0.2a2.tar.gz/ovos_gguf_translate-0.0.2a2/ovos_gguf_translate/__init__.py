from typing import Optional, Dict

from langcodes import Language
from ovos_gguf_solver import GGUFSolver

from ovos_plugin_manager.templates.language import LanguageTranslator


class GGUFTranslator(LanguageTranslator):
    def __init__(self, config: Optional[Dict[str, str]] = None):
        super().__init__(config)
        cfg = {
            "model": "TheBloke/TowerInstruct-7B-v0.1-GGUF",
            "remote_filename": "*Q4_K_M.gguf",
            "n_gpu_layers": -1,
            "persona": "you are a professional translator"
        }
        self.solver = GGUFSolver(cfg)

    def translate(self, text: str, target: Optional[str] = None, source: Optional[str] = None) -> str:
        """
        Translate the given text from the source language to the target language.

        Args:
            text (str): The text to translate.
            target (Optional[str]): The target language code. If None, the internal language is used.
            source (Optional[str]): The source language code. If None, the default language is used.

        Returns:
            str: The translated text.
        """
        target = target or self.default_language
        tgt = Language.get(target).display_name('en')
        if source:
            src = Language.get(source).display_name('en')
            prompt = f"""Translate the following text from {src} into {tgt}.\n{src}: {text}\n{tgt}: """
        else:
            prompt = f"""Translate the following text into {tgt}.\nOriginal: {text}\nTranslated to {tgt}: """
        return self.solver.get_spoken_answer(prompt)


if __name__ == "__main__":
    tx = GGUFTranslator()
    print(tx.translate(
        "The easiest way for anyone to contribute is to help with translations! You can help without any programming knowledge via the translation portal",
        target="es-es"))
