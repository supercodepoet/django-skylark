dojo.provide('RibtTools.TestRunner.TestCase');

/**
 * A collection of MVC objects on the current page
 */
dojo.setObject('RibtTools.TestRunner.TestCaseMvcInstances', {
    /**
     * Adds an instance to the instances array
     *
     * @param instance Either a RibtTools.Mvc.Controller or RibtTools.Mvc.View
     */
    addMvcInstance: function(instance) {
        RibtTools.TestRunner.TestCaseMvcInstances.instances.push(instance);
    },

    /**
     * Array to hold the instances
     */
    instances: []
});

dojo.subscribe(RibtTools.Mvc.Events.New.Controller, RibtTools.TestRunner.TestCaseMvcInstances.addMvcInstance);
dojo.subscribe(RibtTools.Mvc.Events.New.View, RibtTools.TestRunner.TestCaseMvcInstances.addMvcInstance);

dojo.declare('RibtTools.TestRunner.TestCase', RibtTools.SyncTimer.Unit, {
    /**
     * A list of actions that need to be ran to complete the test
     */
    _actions: [],

    /**
     * A shortcut to the list of available MVC Controllers and Views
     */
    _mvcInstances: [],

    /**
     * Message that this test has generated while running
     */
    _logger: RibtTools.TestRunner.Logger,

    /**
     * If a test runner is controlling us, we'll have a test entry point to talk to
     */
    _testEntryPoint: undefined,

    /**
     * Are we through running all of our tests?
     */
    finished: false,

    /**
     * Set up method, ran once before the tests start
     */
    setUp: function() {
        // Implement your own to do something useful
    },

    /**
     * Tear down ran at the very end
     */
    tearDown: function() {
        // Implement your own to do something useful
    },

    /**
     * @constructor
     */
    constructor: function() {
        if (arguments.length > 0) {
            // This is our test entry point
            this._testEntryPoint = arguments[0] || undefined;
        }

        this._mvcInstances = RibtTools.TestRunner.TestCaseMvcInstances.instances;

        this.assert = new RibtTools.TestRunner.TestCaseAssertions();
        this.assert.testcase = this;
    },

    /**
     * Run the test case actions
     */
    run: function() {
        var actions = [];

        actions.push(new RibtTools.SyncTimer.UnitFunction(function() {
            this.setUp();
        }, this));

        for (var member in this) {
            if (member.indexOf('test') == 0) {
                if (!dojo.isFunction(this[member])) { continue; }
                // We will add all the actions we get back from the test
                // case test to our actions list
                var testCaseTest = new RibtTools.TestRunner.TestCaseTest(this[member], this);
                var testActions = testCaseTest.getActions();

                if (testActions.length == 0) { continue; }

                // Combine the actions together
                actions = actions.concat(testActions);
            }
        }

        actions.push(new RibtTools.SyncTimer.UnitFunction(function() {
            this.tearDown();
        }, this));

        this._syncTimer = new RibtTools.SyncTimer(actions);

        this._syncTimer.onException = dojo.hitch(this, this.onException);
        this._syncTimer.onStop = dojo.hitch(this, this.onStop);

        this._syncTimer.start();
    },

    /**
     * Once everything is done we set our timer to finished so that we 
     * can move on to the next test case
     */
    onStop: function() {
        this.finished = true;
    },

    /**
     * When running a test, we can get the exception object most of the 
     * time by capturing what happens from the run() method on the test
     * case.  If we do capture it, we can fail the test here
     *
     * @param e Exception
     */
    onException: function(e) {
        this.assert.exception(e);
        this._syncTimer.fullStop(true);
    },

    /**
     * Used by the individual test case actions and the test case, allows for 
     * messages that are more thant "pass" / "fail".  This can record things
     * like "Found element div.something" or "Receiving AJAX data"
     *
     * @param message A string with the message
     */
    log: function(message, isFailure) {
        isFailure = isFailure || false;
        if (isFailure) {
            this._logger.error(message);
        } else {
            this._logger.info(message);
        }
    }
});

/**
 * A test case test is a single test like (testShouldAlwaysReturn) within a
 * larger test case object (something that extends the TestCase object).
 *
 * This provides the glue between the test case and making the actual
 * assertion calls like this.exists('div.tab').
 */
dojo.declare('RibtTools.TestRunner.TestCaseTest', RibtTools.SyncTimer.Unit, {
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
            throw new RibtToolsError('Cannot use an object to retrive an MVC instance, use the string version of the name instead');
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
     * @param action An instance of RibtTools.SyncTimer.Unit
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
            new RibtTools.TestRunner.Action.When(query));
    },

    /**
     * Glue to the Wait action
     */
    wait: function(ms) {
        this.addAction(
            new RibtTools.TestRunner.Action.Wait(ms));
    },

    /**
     * Glue to the Then action
     */
    then: function(callback) {
        callback = dojo.hitch(this, callback);
        this.addAction(
            new RibtTools.TestRunner.Action.Then(callback));
    },

    /**
     * Make sure that an item exists
     */
    exists: function(query) {
        this.addAction(
            new RibtTools.TestRunner.Action.Exists(query));
    }
});

/**
 * Object that is used to make assertions while testing
 */
dojo.declare('RibtTools.TestRunner.TestCaseAssertions', null, {
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
