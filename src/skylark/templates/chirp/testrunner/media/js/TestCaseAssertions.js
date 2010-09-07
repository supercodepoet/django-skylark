dojo.provide('ChirpTools.TestRunner.TestCaseAssertions');

/**
 * Object that is used to make assertions while testing
 */
dojo.declare('ChirpTools.TestRunner.TestCaseAssertions', null, {
    /**
     * The assertions that fail
     */
    _failures: [],

    /**
     * The assertions that pass
     */
    _passes: [],

    /**
     * Handler for dealing with exceptions that pop up duing testing
     */
    exception: function(e) {
        this.fail(e.message);
        this.testcase.log('Exception on ' + e.fileName + ' line ' + e.lineNumber, true);
    },

    /**
     * Fail
     *
     * @param message String
     */
    fail: function(message) {
        this.testcase.log(message, true);
        this._failures.push(message);
    },

    /**
     * Pass
     *
     * @param message String
     */
    pass: function(message) {
        this.testcase.log(message);
        this._passes.push(message);
    }
});
