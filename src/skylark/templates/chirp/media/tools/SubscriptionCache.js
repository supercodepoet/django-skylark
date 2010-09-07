dojo.provide('ChirpTools.Mvc.SubscriptionCache');

/**
 * A cache to record what subscriptions have been made, usefull for a controller
 * to track existing subscriptions and handle some error condititions that would
 * cause problems for the developer
 */
dojo.declare('ChirpTools.Mvc.SubscriptionCache', null, {
    _cache: [],

    _getFunction: function(context, method) {
        // Try to match the style in which Dojo allows you to specify context
        // and method objects.  Makes this more flexible (debatable if this is a
        // good idea but we want to match our parent framework because
        // developers will be accustomed to it)
        if (dojo.isFunction(context)) {
            // Our context IS the function
            return context;
        } else if (dojo.isFunction(method)) {
            return method;
        } else {
            return context[method];
        }
    },

    /**
     * Adds a function to the cache
     */
    add: function(context, method) {
        this._cache.push(this._getFunction(context, method));
    },

    /**
     * See if the function is contained in the cache
     *
     * Returns a true or false
     */
    contains: function(context, method) {
        var func = this._getFunction(context, method);

        return dojo.indexOf(this._cache, func) != -1;
    }
});
