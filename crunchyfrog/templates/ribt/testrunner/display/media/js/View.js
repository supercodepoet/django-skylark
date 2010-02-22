dojo.provide('RibtTools.TestRunner.Display.View');

dojo.require('RibtTools.Mvc.View');
dojo.require('RibtTools.TestRunner.Events');

dojo.declare('RibtTools.TestRunner.Display.View', RibtTools.Mvc.View, {
    /**
     * The portion at the top of the page that let's you see what tests are
     * running and the current status
     */
    testRunnerNode: undefined,

    /**
     * The iframe that contains the page being tested
     */
    subjectNode: undefined,

    /**
     * The iframe itself
     */
    subjectFrame: undefined,

    /**
     * Sets the size of the frame where the subject of all our tests will occur
     */
    setSubjectSize: function() {
        var fullHeight = document.documentElement.clientHeight;
        var testRunnerPosition = dojo.position(this.testRunner);
        dojo.style(this.subjectFrame, 'height', (fullHeight - testRunnerPosition.h) + 'px');
    },

    /**
     * Show the test runner and the subject frame
     */
    showAll: function() {
        dojo.style(this.testRunner, 'display', 'block');
        dojo.style(this.subject, 'display', 'block');
    },

    /**
     * Shows the test entry points we are preparing to test
     *
     * @param teps Array of test entry points
     */
    showTestEntryPoints: function(teps) {
        dojo.forEach(teps, function(tep) {
            node = dojo.create('li', { innerHTML: tep.name }, this.testEntryPoints, 'last');
            tep.setNode(node);
        }, this);
    },

    /**
     * All tests are done, show the results
     *
     * @params results An array of results from all the tests for all test entry points
     */
    displayResults: function(results) {
        dojo.forEach(results, dojo.hitch(this, function(result) {
            if (result.failures.length > 0) {
                dojo.style(result.testEntryPoint.node, 'color', '#FF0000');
            }
        }));
    },

    /**
     * When the run button is clicked
     */
    runOnClick: function(event) {
        this.publish(RibtTools.TestRunner.Events.Display.RunClick);
    }
});
