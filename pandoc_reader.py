import os

import pypandoc
import frontmatter

from pelican import signals
from pelican.readers import BaseReader, logger


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

        logger.info('pandoc_reader reading file %s.', filename)

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

            if not os.path.exists(bib_file):
                logger.warn('Missing bibliography file %s for article %s.', bib_file, filename)
            else:
                logger.info('Bibliography file %s found for article %s.', bib_file, filename)

            extra_args = extra_args + ['--bibliography={}'.format(bib_file)]

            if bib_header is not None:
                extra_args = extra_args + [
                    '--metadata=reference-section-title="{}"'.format(
                        bib_header)]
        else:
            logger.info('Bibliography not specified for file %s', filename)

        output = pypandoc.convert_file(filename,
                                       to=self.output_format,
                                       format="markdown" + extensions,
                                       extra_args=extra_args,
                                       filters=filters
                                       )

        # Just in case, let's make sure we don't lose Pelican template
        # parameters.
        output = output.replace('%7Battach%7D', '{attach}')\
                       .replace('%7Bfilename%7D', '{filename}')\
                       .replace('%7Btag%7D', '{tag}')\
                       .replace('%7Bcategory%7D', '{category}')

        return output, metadata


def add_reader(readers):
    for ext in PandocReader.file_extensions:
        readers.reader_classes[ext] = PandocReader


def register():
    signals.readers_init.connect(add_reader)
