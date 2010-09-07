dojo.provide('ChirpTools.TestRunner.Logger');

/**
 * Generic logger for any object in the TestRunner
 *
 * This object is a singleton, so we will create a new instance of it
 * after it's defined.
 */
dojo.declare('_ChirpTools.TestRunner.Logger', null, {
    /**
     * Do we also output logged messages to the console?
     */
    sendToConsole: true,

    /**
     * Internal array to hold all the logged messages
     */
    _log: [],

    /**
     * Logs a message, and optionally sends it to the console
     *
     * @param message The body of the log
     * @param level What prefix place at the beginning of the message
     * @param consoleMethod Method on the console object that will be used
     */
    _logMessage: function(message, level, consoleMethod) {
        if (this.sendToConsole && console) {
            console[consoleMethod](message);
        }
        this._log.push(level.toUpperCase() + ' ' + message);
    },

    // Log levels
    debug: function(message) {
        this._logMessage(message, 'debug', 'debug');
    },
    info: function(message) {
        this._logMessage(message, 'info', 'info');
    },
    warning: function(message) {
        this._logMessage(message, 'warning', 'warn');
    },
    error: function(message) {
        this._logMessage(message, 'error', 'error');
    },
    critical: function(message) {
        this._logMessage(message, 'critical', 'error');
    }
});

// Create the actual object from the singleton
dojo.setObject('ChirpTools.TestRunner.Logger',
    new _ChirpTools.TestRunner.Logger());
