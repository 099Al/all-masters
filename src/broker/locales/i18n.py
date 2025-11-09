from fluent_compiler.bundle import FluentBundle

from fluentogram import FluentTranslator, TranslatorHub

from src.config import settings


def create_translator_hub() -> TranslatorHub:
    root_path = settings.path_root
    translator_hub = TranslatorHub(
        {
            "ru": ("ru", "en"),
            "en": ("en", "ru")
        },
        [
            FluentTranslator(
                locale="ru",
                translator=FluentBundle.from_files(
                    locale="ru-RU",
                    filenames=[f"{root_path}/src/broker/locales/ru/txt.ftl"])),
            FluentTranslator(
                locale="en",
                translator=FluentBundle.from_files(
                    locale="en-US",
                    filenames=[f"{root_path}/src/broker/locales/en/txt.ftl"]))
        ],
    )
    return translator_hub