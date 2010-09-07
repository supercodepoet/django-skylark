import copy
import yaml

from django import template


class StringWithSourcefile(object):
    """
    A string that include the source file from whence it came
    """
    def __init__(self, s, sourcefile):
        self.value = s
        self.sourcefile = sourcefile

    def __str__(self):
        return self.value.__str__()

    def __call__(self, f):
        return self.value.__call__(f)


class PageInstructions(object):
    """
    Object to contain the page instructions that come from our YAML files
    """
    def __init__(self, **kwargs):
        self.render_full_page = kwargs.get('render_full_page', True)
        self.context = kwargs.get('context_instance', template.Context())

        """
        These are the ones we expect, these are all the possible kinds of
        instructions that can be handled
        """
        self.root_yaml = None
        self.doctype = None
        self.body = None
        self.title = None
        self.uses_yaml = []
        self.other_yaml = []
        self.piped_yaml = []
        self.js = []
        self.css = []
        self.meta = []
        self.chirp = []

    def part_exists(self, part):
        """
        Withing our existing page instruction for javascript and css, we look
        to see if the part already has been added.  There is no reason to
        duplicate either one of these.
        """
        instructions = []
        instructions.extend(self.js)
        instructions.extend(self.css)
        instructions.extend(self.chirp)

        for instruction in instructions:
            if self._get_source_attribute(instruction) == \
               self._get_source_attribute(part):
                return True

        return False

    def _get_source_attribute(self, part):
        """
        Looks through a part of the yaml file and pulls out the location it
        references.

        Since the parts can have a variety of keys (url, render, static,
        namespace) this method is used to get whichever of the keys is set
        """
        for attr in ('url', 'inline', 'static', 'namespace'):
            if attr in part:
                return part[attr]

        return None

    def pipe_media_to(self, destination_instructions):
        """
        Push all the media into the destination_instructions
        """
        for attr in ('js', 'css', 'chirp',):
            media = getattr(self, attr)
            to_remove = []
            dest_media = getattr(destination_instructions, attr)

            if not media:
                continue

            for part in media:
                # We are piping all the media, so remove it from this one
                to_remove.append(part)
                if destination_instructions.part_exists(part):
                    continue
                if part['sourcefile'] not in destination_instructions.yaml:
                    destination_instructions.piped_yaml.append(
                        part['sourcefile'])
                dest_media.append(part)

            for part in to_remove:
                media.remove(part)

    @property
    def yaml(self):
        if self.root_yaml:
            yield self.root_yaml

        for uses in self.uses_yaml:
            yield uses

        for other in self.other_yaml:
            yield other

        for piped in self.piped_yaml:
            yield piped

    def __get_object(self, yamlfile, context):
        source = template.loader.get_template(yamlfile)
        assert source, 'The template loader found the template but it is ' + \
            'completely empty'

        sourcerendered = source.render(context)
        assert sourcerendered, 'yamlfile needs to contain something'

        return yaml.load(sourcerendered)

    def add(self, instructions, sourcefile, **kwargs):
        if not self.root_yaml:
            # If this is the first time we see this, it's got to be the root
            self.root_yaml = sourcefile

        if not sourcefile == self.root_yaml:
            # This must be coming from someone who is invoking the add method
            # through PageAssembly.add_page_instruction.  We need to put this
            # in the proper spot, so make sure we aren't adding this to the
            # other_yaml dictionary if it's already in the uses_yaml dictionary
            if not sourcefile in self.uses_yaml:
                self.other_yaml.append(sourcefile)

        """
        Adds the instructions from one YAML file to this object, combining
        it with what's already here
        """
        if not isinstance(instructions, list) or not \
           isinstance(instructions, tuple):
            instructions = (instructions, )

        for instruction in instructions:
            if 'uses' in instruction:
                for uses in instruction['uses']:
                    if uses['file'] == self.root_yaml or \
                       uses['file'] in self.other_yaml or \
                       uses['file'] in self.uses_yaml:
                        # We've already seen this guy, there is no reason to
                        # add this YAML again
                        continue
                    self.uses_yaml.append(uses['file'])
                    self.add(
                        self.__get_object(uses['file'], self.context),
                        uses['file'])

            for attr in ('doctype', 'js', 'css', 'body', 'title', 'meta',
                         'chirp'):
                if attr in instruction:
                    pi_object = getattr(self, attr)
                    i_object = instruction[attr]

                    if isinstance(pi_object, list):
                        for part in i_object:
                            if attr in ('js', 'css', 'chirp',):
                                if self.part_exists(part):
                                    continue

                            part['sourcefile'] = sourcefile
                            pi_object.append(part)
                    else:
                        str_plus_source = StringWithSourcefile(
                            i_object, sourcefile)
                        setattr(self, attr, str_plus_source)
