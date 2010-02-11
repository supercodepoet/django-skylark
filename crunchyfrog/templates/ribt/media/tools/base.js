dojo.provide('ribt');

dojo.setObject('RibtToolsError', Error);

// These are the utility function that are used a lot throughout the framework
dojo.setObject('ribt', {
    makeEvents: function(name, evs) {
        var lower = function(str) { return str.toLowerCase(); }

        if (!dojo.isArray(evs)) {
            throw new RibtToolsError('Second argument to make events is not valid');
        }

        var nameParts = name.split('.');

        for (var i in evs) {
            var e = evs[i]; if (typeof e == 'function') { continue; }

            eventParts = nameParts.concat(e.split('.'));
            dojo.setObject(eventParts.join('.'), dojo.map(eventParts, lower).join('::'));
        }
    },

    /**
     * Get the current timestamp in milliseconds
     */
    time: function() {
        var time = Date.now || function() {
            return +new Date;
        };

        return time();
    }
});

dojo.addOnLoad(function() {
    // When the page loads, we need to create a parse and search through the
    var parser = new RibtTools.Mvc.Parser();

    // Setup some shortcuts to our public methods
    ribt.parse   = dojo.hitch(parser, parser.parse);
    ribt.str2obj = dojo.hitch(parser, parser.str2obj);
    ribt.place   = dojo.hitch(parser, parser.place);

    ribt.parse();
});
