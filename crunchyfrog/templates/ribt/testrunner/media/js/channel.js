dojo.provide('RibtTools.TestRunner.Channel');

dojo.require('dojox.timing');

dojo.declare('_RibtTools.TestRunner.Channel', null, {
    /**
     * Holds events that are waiting for the remote side to initialize
     */
    queue: { publish: [] },

    /**
     * How much time between ticks when we are waiting for the remote channel to
     * open up.
     */
    _waitInterval: 50,

    /**
     * Fixes up the publish to use the queue
     */
    constructor: function() {
        this.publish = this._publishQueue
        this.localDojo = dojo;
    },

    /**
     *
     */
    setSubject: function(subjectFrame) {
        this.subjectFrame = subjectFrame;

        this.subjectWaitForLoad();
    },

    /**
     *
     */
    navigate: function(url) {
        this.subjectFrame.contentWindow.location = url;

        this.subjectWaitForLoad();
    },

    /**
     * 
     */
    subjectWaitForLoad: function() {
        this.remoteDojo = undefined;

        var timer = new dojox.timing.Timer(this._waitInterval);

        // When we began?
        timer.started = ribt.time();

        // We need to wait until dojo shows up on the client
        var context = { scope: this, timer: timer };
        timer.onTick = dojo.hitch(context, function(millSinceTick) {
            if ((ribt.time() - this.timer.started) > ribtConfig.testRunner.loadingTimeout) {
                this.localDojo.publish(RibtTools.TestRunner.Events.Channel.RemoteReady, [ false ]);
                throw new RibtToolsError('Could not attach to dojo library in the remote window (the subject).  Have you included the Dojo toolkit there?');
                timer.stop();
            }
            this.scope.remoteDojo = this.scope.subjectFrame.contentWindow.dojo;
            if (this.scope.remoteDojo) {
                this.timer.stop();
                this.scope.publish = this.scope._publishWired;
                this.scope._patchRemoteChannel();
                this.scope.publish(RibtTools.TestRunner.Events.Channel.RemoteReady, [ true ]);
                this.scope.dumpQueue();
            }
        });

        timer.start();
    },

    /**
     *
     */
    dumpQueue: function() {
        for (var i in this.queue.publish) {
            var pair = this.queue.publish[i];
            if (typeof pair == 'function') { continue; }
            this.publish(pair[0], pair[1]);
        }
        this.queue.publish = [];
    },

    /**
     * By default, this is what comes with the nekked' object
     */
    publish: function() {
        throw new RibtToolsError('Channel has not been initialized yet');
    },

    /**
     *
     */
    _checkTopic: function(topic) {
        if (!topic) {
            throw new RibtToolsError('You are publishing an event that is undefined, check you spelling');
        }
    },

    /**
     * Once the user sets the nodes, this is used
     *
     * It pushes all stuff into a queue that will wait until things are ready
     */
    _publishQueue: function(topic, args) {
        this._checkTopic(topic);
        this.queue.publish.push([topic, args]);
    },

    /**
     * Once everything is setup, now we can start publishing real events
     */
    _publishWired: function(topic, args) {
        this._checkTopic(topic);
        this.localDojo.publish(topic, args);
        if (this.remoteDojo) {
            this.remoteDojo.publish(topic, args);
        }
    },

    /**
     * Takes the remote Channel object and patches it to work correctly
     */
    _patchRemoteChannel: function() {
        this.remoteDojo.addOnLoad(dojo.hitch(this, function() {
            if (!this.subjectFrame.contentWindow.RibtTools.TestRunner.Channel) {
                debugger;
                throw new RibtToolsError('Cannot reach the remote (subject) Channel object, is it using Ribt tools?');
            }

            var remoteChannel = this.subjectFrame.contentWindow.RibtTools.TestRunner.Channel

            remoteChannel.publish = remoteChannel._publishWired;
            // Flip the dojo's on the remote end
            remoteChannel.remoteDojo = this.localDojo;
            remoteChannel.localDojo = this.remoteDojo;

            remoteChannel.dumpQueue();
        }));
    }
});

dojo.setObject('RibtTools.TestRunner.Channel', new _RibtTools.TestRunner.Channel());
