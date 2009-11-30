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
        self.uses_yaml = []
        self.doctype   = None
        self.js        = []
        self.css       = []
        self.body      = None
        self.title     = None
        self.meta      = []
        self.dojo      = []

    def _part_exists(self, part):
        """
        Withing our existing page instruction for javascrip and css, we look to see
        if the part already has been added.  There is no reason to duplicate either
        one of these.
        """
        instructions = []
        instructions.extend(self.js)
        instructions.extend(self.css)
        instructions.extend(self.meta)
        instructions.extend(self.dojo)

        for instruction in instructions:
            if self._get_source_attribute(instruction) == self._get_source_attribute(part):
                return True

        return False

    def _get_source_attribute(self, part):
        """
        Looks through a part of the yaml file and pulls out the location it references.

        Since the parts can have a variety of keys (url, render, static,
        namespace) this method is used to get whichever of the keys is set
        """
        for attr in ('url', 'inline', 'static', 'namespace'):
            if attr in part:
                return part[attr]

        return None

    def filter(self, **kwargs):
        filtered = copy.copy(self) 
        for kw in kwargs:
            try:
                attr = getattr(filtered, '_PageInstructions__filter_%s' % kw)
                attr()
            except TypeError:
                pass
            except AttributeError:
                pass

        return filtered

    def __filter_only_uses(filtered, **kwargs):
        for attr in ('js', 'css', 'meta', 'dojo'):
            subject = getattr(filtered, attr)
            cleaned = [ i for i in subject if i['sourcefile'] in
                       filtered.uses_yaml ]
            setattr(filtered, attr, cleaned)

    def __filter_exclude_uses(filtered, **kwargs):
        for attr in ('js', 'css', 'meta', 'dojo'):
            subject = getattr(filtered, attr)
            cleaned = [ i for i in subject if i['sourcefile'] in
                       filtered.root_yaml ]
            setattr(filtered, attr, cleaned)

    @property
    def yaml(self):
        if self.root_yaml:
            yield self.root_yaml

        for uses in self.uses_yaml:
            yield uses

    def __get_object(self, yamlfile, context):
        source, origin = template.loader.find_template_source(yamlfile)
        assert source, 'The template loader found the template but it is completely empty'

        sourcerendered = template.Template(source).render(context)
        assert sourcerendered, 'yamlfile needs to contain something'

        return yaml.load(sourcerendered)

    def add(self, instructions, sourcefile, **kwargs):
        if not self.root_yaml:
            # If this is the first time we see this, it's got to be the root
            self.root_yaml = sourcefile

        """
        Adds the instructions from one YAML file to this object, combining
        it with what's already here
        """
        if not isinstance(instructions, list) or not isinstance(instructions, tuple):
            instructions = (instructions, )

        for instruction in instructions:
            if instruction.has_key('uses'):
                for uses in instruction['uses']:
                    self.uses_yaml.append(uses['file'])
                    self.add(
                        self.__get_object(uses['file'], self.context),
                        uses['file']
                    )

            for attr in ('doctype', 'js', 'css', 'body', 'title', 'meta',
                         'dojo'):
                if instruction.has_key(attr):
                    pi_object = getattr(self, attr)
                    i_object  = instruction[attr]

                    if isinstance(pi_object, list):
                        for part in i_object:
                            if attr in ('js', 'css', 'meta', 'dojo',):
                                if self._part_exists(part):
                                    continue

                            part['sourcefile'] = sourcefile
                            pi_object.append(part)
                    else:
                        str_plus_source = StringWithSourcefile(
                            i_object, sourcefile)
                        setattr(self, attr, str_plus_source)
