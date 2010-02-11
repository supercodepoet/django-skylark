dojo.provide('RibtTools.TestRunner.TestCaseCollector');

dojo.declare('_RibtTools.TestRunner.TestCaseCollector', null, {
    /**
     * Just the test names, as registered when the page loaded in
     */
    _testCaseNames: [],

    /**
     * Actual instances of tests cases
     */
    _testCases: [],

    /**
     * Create the test case instances
     */
    kickoff: function() {
        dojo.forEach(this._testCaseNames, function(testCaseName) {
            var cls = dojo.getObject(testCaseName);
            if(!dojo.isFunction(cls)){
                throw new RibtToolsError("Could not load test case class '" + className);
            }
            this._testCases.push(new cls());
        }, this);
    },

    /**
     * Add a string test case name to be tested
     */
    add: function(testCaseName) {
        this._testCaseNames.push(testCaseName);
    }
});

dojo.setObject('RibtTools.TestRunner.TestCaseCollector',
    new _RibtTools.TestRunner.TestCaseCollector);
