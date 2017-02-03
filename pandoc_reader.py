import os

import pypandoc
import frontmatter

from pelican import signals
from pelican.readers import BaseReader


class PandocReader(BaseReader):
    enabled = True
    file_extensions = ['md', 'markdown', 'mkd', 'mdown']
    output_format = 'html5'

    # Inspired by https://github.com/kdheepak/pelican_pandoc/blob/master/__init__.py
    METADATA_TEMPLATE = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'metadata.template')

    def read_metadata(self, path, format=None):

        metadata = frontmatter.load(path)
        metadata_res = dict()
        for key, value in metadata.to_dict().items():
            if key != "content":
                try:
                    value_, = value
                except:
                    value_ = value
                metadata_res[key] = self.process_metadata(key, str(value_))

        return metadata_res

    def read(self, filename):
        metadata = self.read_metadata(filename)

        bib_dir = self.settings.get('PANDOC_BIBDIR', '')
        bib_header = self.settings.get('PANDOC_BIBHEADER', None)
        extra_args = self.settings.get('PANDOC_ARGS', [])
        filters = self.settings.get('PANDOC_FILTERS', [])
        extensions = self.settings.get('PANDOC_EXTENSIONS', '')
        if isinstance(extensions, list):
            extensions = ''.join(extensions)

        if "bibliography" in metadata.keys():
            bib_file = os.path.join(bib_dir, metadata['bibliography'])
            extra_args = extra_args + ['--bibliography={}'.format(bib_file)]

            if bib_header is not None:
                extra_args = extra_args + [
                    '--metadata=reference-section-title="{}"'.format(
                        bib_header)]

        output = pypandoc.convert_file(filename,
                                       to=self.output_format,
                                       format="markdown" + extensions,
                                       extra_args=extra_args,
                                       filters=filters
                                       )

        return output, metadata


def add_reader(readers):
    for ext in PandocReader.file_extensions:
        readers.reader_classes[ext] = PandocReader


def register():
    signals.readers_init.connect(add_reader)
