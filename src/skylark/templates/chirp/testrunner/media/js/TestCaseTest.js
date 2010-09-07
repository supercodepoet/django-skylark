dojo.provide('ChirpTools.TestRunner.TestCaseTest');

dojo.require('ChirpTools.Error');
dojo.require('ChirpTools.SyncTimer.Unit');
dojo.require('ChirpTools.TestRunner.Action.When');
dojo.require('ChirpTools.TestRunner.Action.Wait');
dojo.require('ChirpTools.TestRunner.Action.Then');
dojo.require('ChirpTools.TestRunner.Action.Exists');

/**
 * A test case test is a single test like (testShouldAlwaysReturn) within a
 * larger test case object (something that extends the TestCase object).
 *
 * This provides the glue between the test case and making the actual
 * assertion calls like this.exists('div.tab').
 */
dojo.declare('ChirpTools.TestRunner.TestCaseTest', ChirpTools.SyncTimer.Unit, {
    /**
     * The test function we will call to actually perform the actions
     */
    _test: undefined,

    /**
     * The parent test case for this one test
     */
    _testCase: undefined,

    /**
     * An array that builds with each action in this test
     */
    _actions: undefined,

    /**
     * @constructor
     */
    constructor: function(test, testCase) {
        this._test = test;
        this._testCase = testCase;
        this._actions = [];

        // Tie into our assertion and log method
        this.assert = testCase.assert;
        this.log = testCase.log;

        // Call our test with the scope of this TestCaseTest
        this._test.call(this);
    },

    /**
     * @returns Array
     */
    getActions: function() {
        return this._actions;
    },

    /**
     * Get's an mvc obect that is present on the page somewhere
     *
     * @param name The name of the object to get as a string
     */
    _getMvcObject: function(name) {
        if (typeof name == 'object') {
            throw new ChirpTools.Error('Cannot use an object to retrive an MVC instance, use the string version of the name instead');
        }

        var context = { scope: this, name: name, toReturn: [] };

        dojo.forEach(this._testCase._mvcInstances, function(instance) {
            if (this.name == instance.declaredClass) {
                // We have a winner
                this.toReturn.push(instance);
            }
        }, context);

        return context.toReturn;
    },

    /**
     * Convenience method for using _getMvcObject
     *
     * @param name
     */
    getController: function(name) {
        return this._getMvcObject(name);
    },

    /**
     * Convenience method for using _getMvcObject
     *
     * @param name
     */
    getView: function(name) {
        return this._getMvcObject(name);
    },

    /**
     * Used by the test case test actions to place a sync timer unit
     * onto the stack for running later.  Whenever a method like 
     * this.exists runs, it places an element onto the end of this array
     * to be executed by the test case.
     *
     * @param action An instance of ChirpTools.SyncTimer.Unit
     */
    addAction: function(action) {
        // Tie the log and assertion object to the unit
        action.log = this.log;
        action.assert = this.assert;

        this._actions.push(action);
    },

    /**
     * Glue to the When action
     */
    when: function(query) {
        this.addAction(
            new ChirpTools.TestRunner.Action.When(query));
    },

    /**
     * Glue to the Wait action
     */
    wait: function(ms) {
        this.addAction(
            new ChirpTools.TestRunner.Action.Wait(ms));
    },

    /**
     * Glue to the Then action
     */
    then: function(callback) {
        callback = dojo.hitch(this, callback);
        this.addAction(
            new ChirpTools.TestRunner.Action.Then(callback));
    },

    /**
     * Make sure that an item exists
     */
    exists: function(query) {
        this.addAction(
            new ChirpTools.TestRunner.Action.Exists(query));
    }
});
