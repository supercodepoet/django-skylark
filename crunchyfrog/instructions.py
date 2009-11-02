import yaml

class PageInstructions(object):
    """
    Object to contain the page instructions that come from our YAML files
    """
    def __init__(self, instructions = None, **kwargs):
        self.render_full_page = kwargs.get('render_full_page', True)
        self.yaml = []

        """
        These are the ones we expect, these are all the possible kinds of
        instructions that can be handled
        """
        self.doctype = None
        self.uses    = []
        self.js      = []
        self.css     = []
        self.body    = None
        self.title   = None
        self.meta    = []
        self.dojo    = []

        if instructions:
            self.add(instructions)

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

    def add(self, instructions, sourcefile):
        """
        Adds the instructions from one YAML file to this object, combining
        it with what's already here
        """
        if not isinstance(instructions, list) or not isinstance(instructions, tuple):
            instructions = (instructions, )

        self.yaml.append(sourcefile)

        for instruction in instructions:
            for attr in ('doctype', 'js', 'css', 'body', 'title', 'meta',
                         'uses', 'dojo'):
                if instruction.has_key(attr):
                    pi_object = getattr(self, attr)
                    i_object  = instruction[attr]

                    if isinstance(pi_object, list):
                        for part in i_object:
                            if attr in ('js', 'css', 'meta', 'dojo',):
                                if self._part_exists(part):
                                    continue

                            pi_object.append(part)
                    else:
                        setattr(self, attr, i_object)
