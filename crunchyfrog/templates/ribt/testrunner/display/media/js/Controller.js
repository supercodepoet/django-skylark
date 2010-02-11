dojo.provide('RibtTools.TestRunner.Display.Controller');

dojo.require('RibtTools.Mvc.Controller');

dojo.declare('RibtTools.TestRunner.Display.Controller', RibtTools.Mvc.Controller, {
    // The number of tests we plan on running
    testCount: 0,

    /**
     *
     */ 
    constructor: function(domNode) {
        this.view = new RibtTools.TestRunner.Display.View(domNode);
        this.view.setSubjectSize();
        this.view.showAll();

        // The channel is how we communicate with the other frame
        this.channel = RibtTools.TestRunner.Channel;
        this.channel.setSubject(this.view.subjectFrame);

        dojo.subscribe(RibtTools.TestRunner.Events.SubjectFrame.Ready, this, this.notifyTestCount);

        this.initTestEntryPoints(RibtTools.TestRunner.TestEntryPoints.items);

        this.view.showTestEntryPoints(this.testEntryPoints);

        this.subscribe(RibtTools.TestRunner.Events.Display.RunClick, this, this.kickoffTestEntryPoints);
    },

    /**
     *
     */ 
    initTestEntryPoints: function(data) {
        var teps = []

        dojo.forEach(data, function(rawTep) {
            var tepInstance = new RibtTools.TestRunner.Display.TestEntryPoint(
                rawTep.url, rawTep.name);
            this.teps.push(tepInstance);
        }, { scope: this, teps: teps });

        this.testEntryPoints = teps;
    },

    /**
     *
     */
    kickoffTestEntryPoints: function() {
        teps = this.testEntryPoints;

        dojo.forEach(teps, function(tep) {
            this.scope.channel.navigate(tep.url);
            this.scope.channel.publish(RibtTools.TestRunner.Events.Running, [ tep ]);
        }, { scope: this, teps: teps });
    },

    /**
     *
     */ 
    notifyTestCount: function() {
        this.channel.publish(RibtTools.TestRunner.Events.TestCount, [ this.testCount ]);
    }
});
