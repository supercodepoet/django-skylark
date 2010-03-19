dojo.provide('ribt');

// These are the utility function that are used a lot throughout the framework
dojo.setObject('ribt', {
    /**
     * Makes events and hooks into dojo.provide to make sure that dependencies
     * still work as expected.  Use it like this:
     *
     *    dojo.provide(ribt.makeEvents('MyProject.AppName.Page.Events', [
     *        'SomeCrazyEvent']))
     *
     */
    makeEvents: function(name, evs) {
        var lower = function(str) { return str.toLowerCase(); }

        if (!dojo.isArray(evs)) {
            throw new RibtTools.Error('Second argument to make events is not valid');
        }

        var nameParts = name.split('.');

        for (var i in evs) {
            var e = evs[i]; if (dojo.isFunction(e)) { continue; }

            eventParts = nameParts.concat(e.split('.'));
            dojo.setObject(eventParts.join('.'), dojo.map(eventParts, lower).join('::'));
        }

        return name;
    },
    
    /**
     * Piggybacking on the dojo.publish method to ensure we have a valid topic to publish to
     */
    publish: function(/*String*/ topic, /*Array*/ args) {
        if (topic != undefined) {
            dojo.publish(topic, args);
        } else {
            
            try {
                throw new Error();
            } catch (err) {
                if (err.stack) {
                    var trace = err.stack;
                }
            }
            
            var initialMsg = 'It appears you are trying to publish to an undefined topic'
            
            if (trace) {
                errorMsg = initialMsg + ', stack trace is\n' + trace;
            } else {
                errorMsg = initialMsg;
            }
            
            throw new RibtTools.Error(errorMsg);
        }
        
    },
    
    /**
     * Piggybacking on the dojo.subscribe method to ensure we have a valid topic to subscribe to
     */
    subscribe: function(/*String*/ topic, /*Object|null*/ context, /*String|Function*/ method) {
        if (topic != undefined) {
            dojo.subscribe(topic, context, method);
        } else {
            
            try {
                throw new Error();
            } catch (err) {
                if (err.stack) {
                    var trace = err.stack;
                }
            }
            
            var initialMsg = 'It appears you are trying to subscribe to an undefined topic'
            
            if (trace) {
                errorMsg = initialMsg + ', stack trace is\n' + trace;
            } else {
                errorMsg = initialMsg;
            }
            
            throw new RibtTools.Error(errorMsg);
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
    },

    /**
     * Uses the MVC template manager to create and register a template for use with a given
     * view
     */
    makeTemplate: function() {
        dojo.require('RibtTools.Mvc.TemplateManager');

        RibtTools.Mvc.TemplateManager.makeTemplate.apply(
            RibtTools.Mvc.TemplateManager, arguments);
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
