dojo.provide('ChirpTools.Mvc.View');

dojo.require('dojo.NodeList-traverse');
dojo.require('ChirpTools.Error');
dojo.require('ChirpTools.Mvc.TemplateManager');
dojo.require('ChirpTools.Mvc.Dom');

/**
 * Base View
 */
dojo.declare('ChirpTools.Mvc.View', null, {
    /**
     * Constructor
     */
    constructor: function(domNode) {
        if ($CF.INSTRUMENTED) {
            dojo.publish(ChirpTools.Mvc.Events.New.View, [ this ]);
        }

        // Find our view hook
        if (domNode) {
            this._setDomNode(domNode);
        }

        this.templates = ChirpTools.Mvc.TemplateManager.getTemplatesFor(this.declaredClass);
    },

    /**
     * Convenience method
     */
    _setDomNode: function(domNode) {
        this.domNode = domNode;
        this._bind(this.domNode);
    },

    /**
     * Binds to any element within the panel that has an chirpBind attribute
     */
    _bind: function(panel, removeExisting) {
        this._bindHandles = this._bindHandles || {};
        this._bindNames = this._bindNames || {};

        removeExisting = (removeExisting == undefined) ? true : removeExisting;
        if (removeExisting) {
            this._unbind();
        }

        this._connectHandlersToView();

        dojo.query('*[chirpBind], *[chirpBindGroup]', panel).forEach(function(element) {
            if (!this._bindBelongsTo(element, panel)) { return; }

            var attr = dojo.attr(element, 'chirpBind') || dojo.attr(element, 'chirpBindGroup');

            if (dojo.attr(element, 'chirpBind')) {
                this[attr] = element;
            } else {
                this[attr] = this[attr] || []
                this[attr].push(element);
            }

            this._bindNames[attr] = element;

            var handlers = this._getHandlersForName(attr);
            if (!handlers) { return; }

            for (i in handlers) {
                var handler  = handlers[i]; if (dojo.isFunction(handler)) { continue; }
                var funcName = handler.funcName;
                var context  = {'scope': this, 'name': funcName, 'func': handler.func};

                if (!this._bindHandles[funcName]) {
                    this._bindHandles[funcName] = [];
                }
                this._bindHandles[funcName].push(dojo.connect(element, handler.eventType, context, this._connectHandler));
            }
        }, this);
    },

    /**
     * Unbinds all the events that have been bound to this view
     */
    _unbind: function() {
        for (var i in this._bindHandles) {
            var bindHandle = this._bindHandles[i]; if (dojo.isFunction(bindHandle)) { continue; }
            dojo.forEach(bindHandle, function(eventHandle) {
                dojo.disconnect(eventHandle);
            });
        }

        for (var key in this._bindNames) {
            delete this[key];
        }

        this._bindHandles = {};
    },

    /**
     * Connect root handlers to the domNode
     */
    _connectHandlersToView: function() {
        for (var funcName in this) {
            var func = this[funcName];

            if (!dojo.isFunction(func) || funcName.indexOf('_') == 0) {
                continue;
            }

            if (ChirpTools.Mvc.Dom.containsEvent(funcName)) {
                this._bindHandles[funcName] = [];
                this._bindHandles[funcName].push(dojo.connect(
                    this.domNode, funcName.toLowerCase(), this, func));
            }
        }
    },

    /**
     * Looks for view handlers that match the bind name
     */
    _getHandlersForName: function(bindName) {
        var handlers = [];
        for (var funcName in this) {
            var func = this[funcName];

            if (!dojo.isFunction(func) || funcName.indexOf('_') == 0) {
                continue
            }

            var funcPrefix = funcName.substring(0, funcName.toLowerCase().lastIndexOf('on'));
            if (bindName == funcPrefix) {
                var eventType = funcName.toLowerCase().replace(bindName.toLowerCase(), '');
                
                if (ChirpTools.Mvc.Dom.containsEvent(eventType)) {
                    handlers.push({ 'funcName': funcName, 'func': func, 'eventType': eventType });
                }
            }
        }

        return (handlers.length == 0) ? false : handlers;
    },

    /**
     * Connects to a handler, for example
     *
     *    chirpBind="button"
     *
     *    this.buttonOnClick = function() {
     *        // do whatever
     *    }
     *
     */
    _connectHandler: function() {
        var args = arguments;
        args[0].handle = this.scope._bindHandles[this.name];
        args[0].funcName = this.name;
        this.func.apply(this.scope, args);
    },

    /**
     * Looks at an element that has an chirpBind attribute and determines if it
     * belongs to a specific chirpTypeElement
     */
    _bindBelongsTo: function(bindElement, chirpTypeElement) {
        var firstLbType = dojo.query(bindElement).closest('*[chirpType]')[0];

        // If we don't have a chirpType, we'll assume that it all applies to us
        if (!firstLbType) { return true; }
        if (firstLbType == chirpTypeElement) { return true; }

        return false;
    },

    /**
     * Publishes an event for others to listen for
     *
     * This is going to include the "this"
     */
    publishLocal: function(topic, args) {
        if (!topic) {
            throw new ChirpTools.Error('Trying to publish a topic from instance of ' +
                this.declaredClass + ' that has no value, did you misspell it?');
        }

        args = args || [];

        args.unshift(this);

        dojo.publish(topic, args);
    },

    /**
     * Convenience method to publish events from the view to the world
     */
    publishGlobal: function(topic, args) {
        chirp.publish(topic, args);
    },

    /**
     * Takes an event and disables any further handlers to it
     *
     * This is typically used where you want to disable a button for an AJAX
     * action or form submission
     */
    disable: function(event) {
        dojo.forEach(this._bindHandles[event.funcName], function(eventHandle) {
            dojo.disconnect(eventHandle);
        });
        this._bindHandles[event.funcName] = dojo.connect(event.currentTarget, 'onclick', this, function(event) {
            dojo.stopEvent(event);
        });
    },

    /**
     * Destroys this view, and any events that were bound to it
     */
    destroy: function() {
        this._unbind();

        if (this.domNode) {
            dojo.destroy(this.domNode);
        }

        dojo.publish(ChirpTools.Mvc.Events.ViewDestruction, [ this ]);
    }
})
