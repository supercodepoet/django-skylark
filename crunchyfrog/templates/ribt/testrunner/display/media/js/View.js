dojo.provide('RibtTools.TestRunner.Display.View');

dojo.require('RibtTools.Mvc.View');

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
     *
     */
    showAll: function() {
        dojo.style(this.testRunner, 'display', 'block');
        dojo.style(this.subject, 'display', 'block');
    },

    /**
     *
     */
    showTestEntryPoints: function(teps) {
        dojo.forEach(teps, function(tep) {
            node = dojo.create('li', { innerHTML: tep.name }, this.testEntryPoints, 'last');
            tep.setNode(node);
        }, this);
    },

    /**
     * When the run button is clicked
     */
    runOnClick: function(event) {
        this.publish(RibtTools.TestRunner.Events.Display.RunClick);
    }
});
