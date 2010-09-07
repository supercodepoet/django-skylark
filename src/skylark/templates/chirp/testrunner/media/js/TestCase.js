dojo.provide('ChirpTools.TestRunner.TestCase');

dojo.require('ChirpTools.SyncTimer.Timer');
dojo.require('ChirpTools.SyncTimer.Unit');
dojo.require('ChirpTools.SyncTimer.UnitFunction');
dojo.require('ChirpTools.TestRunner.Logger');
dojo.require('ChirpTools.TestRunner.TestCaseTest');
dojo.require('ChirpTools.TestRunner.TestCaseAssertions');

dojo.declare('ChirpTools.TestRunner.TestCase', ChirpTools.SyncTimer.Unit, {
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
    _logger: ChirpTools.TestRunner.Logger,

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

        this._mvcInstances = ChirpTools.TestRunner.TestCaseMvcInstances.instances;

        this.assert = new ChirpTools.TestRunner.TestCaseAssertions();
        this.assert.testcase = this;
    },

    /**
     * Run the test case actions
     */
    run: function() {
        var actions = [];

        actions.push(new ChirpTools.SyncTimer.UnitFunction(function() {
            this.setUp();
        }, this));

        for (var member in this) {
            if (member.indexOf('test') == 0) {
                if (!dojo.isFunction(this[member])) { continue; }
                // We will add all the actions we get back from the test
                // case test to our actions list
                var testCaseTest = new ChirpTools.TestRunner.TestCaseTest(this[member], this);
                var testActions = testCaseTest.getActions();

                if (testActions.length == 0) { continue; }

                // Combine the actions together
                actions = actions.concat(testActions);
            }
        }

        actions.push(new ChirpTools.SyncTimer.UnitFunction(function() {
            this.tearDown();
        }, this));

        this._syncTimer = new ChirpTools.SyncTimer.Timer(actions);

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
