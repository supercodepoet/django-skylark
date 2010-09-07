dojo.provide('ChirpTools.Mvc.TemplateManager');

dojo.require('dojox.dtl');
dojo.require('ChirpTools.Error');

// This is our singleton skeleton
dojo.declare('_ChirpTools.Mvc.TemplateManager', null, {
    /**
     * Cache of templates tied to specfic views
     */
    _templates: {},

    /**
     * A DOM Element that temporarily holds nodes for us when performing
     * renderNodeList
     */
    _containerNode: undefined,

    /**
     * The default template object to use if we aren't given one
     */
    _defaultTemplateObject: dojox.dtl.Template,

    /**
     * This is a singleton, so it should only be called once
     *
     * @constructor
     */
    constructor: function() {
        this._containerNode = dojo.create('div');
    },

    /**
     * Creates a template and saves it to the manager based on the data
     * provided
     *
     * @param mvcView
     * @param kwargs
     */
    makeTemplate: function(mvcView, kwargs) {
        var name = kwargs.name;

        if (!name) {
            throw ChirpTools.Error('You need to specify a name when making a chirp template');
        }

        if (this._templates[mvcView] && this._templates[mvcView][kwargs.name]) {
            // It's already made
            return;
        }

        var templateObject = this._defaultTemplateObject;

        if (kwargs.module && kwargs.url) {
            // This is a template we will create from xhrGet'ing it
            if (kwargs.templateObject) {
                templateObject = kwargs.templateObject;
            }
            var template = this._templateFromUrl(templateObject, kwargs.module, kwargs.url);
        } else if (kwargs.source) {
            // This is an interned template, or a template inlined in the JS source
            var template = this._templateFromSource(templateObject, kwargs.source);
        }

        this.register(mvcView, kwargs.name, template);
    },

    /**
     * Initializes the template cache for the specific view
     *
     * This is important.  Our manager supports the ability to assign the
     * templates for a view before they are all created.  Typically upon
     * view creation, there is a call to getTemplatesFor() and later on
     * the call to makeTemplate().  By init'ing our template cache the
     * first time either one is called, we can make sure that things work
     * as expected.
     *
     * @param mvcView
     */
    _initForMvcView: function(mvcView) {
        if (!this._templates[mvcView]) {
            this._templates[mvcView] = {};
        }
    },

    /**
     * Registers a template for a MVC view with the given name
     *
     * This will not overwrite existing templates, this allows us to perform
     * template interning (caching) during a JS file rollup and not need to 
     * fetch the template again.
     *
     * @param mvcView
     * @param name
     * @param template
     */
    register: function(mvcView, name, template) {
        this._initForMvcView(mvcView);

        if (this._templates[mvcView][name]) {
            // We aren't going to re-register a template
            return;
        }

        this._patchTemplate(template);

        this._templates[mvcView][name] = template;
    },

    /**
     * Adds some handy methods to the template so that it can function a bit
     * easier within our framework.
     *
     * @param template
     */
    _patchTemplate: function(template) {
        var scope = { template: template, manager: this };
        template.renderNodeList = dojo.hitch(scope, function(context) {
            var nodeStr = this.template.render(context);

            if (!nodeStr) {
                throw new ChirpTools.Error('Empty template was rendered');
            }

            var container = this.manager._containerNode;
            dojo.place(nodeStr, container, 'only');

            nl = dojo.NodeList.apply(dojo.NodeList, dojo._toArray(container.children));
            return nl;
        });

        template.renderNode = dojo.hitch(scope, function(context) {
            var nodeList = this.template.renderNodeList(context);

            if (nodeList.length == 1) {
                // We have one node inside the list, as expected
                return nodeList[0];
            } else {
                throw new ChirpTools.Error('renderNode expects to find one ' +
                    'node being rendered, we found ' + nodeList.length);
            }
        });
    },

    /**
     * Retrieves a dictionary (objects) for the given MVC view name
     *
     * This is typically called from within the view itself, to assign
     * this.templates equal to the returned results of this method.
     *
     * @param mvcView
     */
    getTemplatesFor: function(mvcView) {
        this._initForMvcView(mvcView);

        return this._templates[mvcView];
    },

    /**
     * Creates a template object using a module path and url
     *
     * @param module
     * @param url
     */
    _templateFromUrl: function(templateObject, module, url) {
        var template = new templateObject(dojo.moduleUrl(module, url));
        return template;
    },

    /**
     * Creates a template directly from source
     *
     * @param source
     */
    _templateFromSource: function(templateObject, source) {
        var template = templateObject(source);
        return template;
    }
});

// Create our singleton instance
dojo.setObject('ChirpTools.Mvc.TemplateManager',
    new _ChirpTools.Mvc.TemplateManager());
