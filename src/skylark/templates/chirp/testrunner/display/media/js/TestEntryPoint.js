dojo.provide('ChirpTools.TestRunner.Display.TestEntryPoint');

dojo.require('ChirpTools.SyncTimer.Unit');
dojo.require('ChirpTools.TestRunner.Events');

dojo.declare('ChirpTools.TestRunner.Display.TestEntryPoint', ChirpTools.SyncTimer.Unit, {
    /**
     * List of test cases collected after the tests run
     */
    _testCases: undefined,

    /**
     * A way to talk to the subject frame (what we are testing)
     */
    _channel: undefined,

    /**
     * Are we finished running?
     */
    finished: false,

    /**
     * URL for where this test entry point should navigate to when it runs
     */
    url: '',

    /**
     * What is the cosmetic name of this?
     */
    name: '',

    /**
     * @constructor
     */
    constructor: function(url, name) {
        this.url = url;
        this.name = name;
    },

    /**
     * Set's the channel
     */
    channel: function(channel) {
        this._channel = channel;
    },

    /**
     * Set's the node, or the DOM Element within the top bar that represents this
     * test entry point
     */
    setNode: function(node) {
        this.node = node;
    },

    /**
     * Navigate to the URL and let the tests run
     */
    run: function() {
        this._channel.navigate(this.url);

        this._channel.whenObject('ChirpTools.TestRunner.TestCaseCollector', dojo.hitch(this, function() {
            this._channel.publish(ChirpTools.TestRunner.Events.Running, [ this ]);
        }));
    },

    /**
     * When all the tests run, we will arrive back here with a array of
     * test cases that were ran
     *
     * @param testCases 
     */
    collectedTestCases: function(testCases) {
        if (arguments.length > 0) {
            this._testCases = testCases;
            this.finished = true;
        } else {
            return this._testCases;
        }
    }
});
