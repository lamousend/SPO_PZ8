
from whitenoise.storage import CompressedManifestStaticFilesStorage


class StaticFilesStorage(CompressedManifestStaticFilesStorage):
    support_js_module_import_aggregation = False

    def url_converter(self, name, hashed_files, template=None, *args, **kwargs):
        converter = super().url_converter(
            name, hashed_files, template, *args, **kwargs
        )

        def convert(match):
            url = match.group("url")
            if url.endswith(".map"):
                return match.group(0)
            return converter(match)

        return convert
