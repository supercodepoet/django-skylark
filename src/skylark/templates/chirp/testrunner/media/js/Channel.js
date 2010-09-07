dojo.provide('ChirpTools.TestRunner.Channel');

dojo.require('dojox.timing');
dojo.require('ChirpTools.Error');
dojo.require('ChirpTools.TestRunner.Events');

dojo.declare('_ChirpTools.TestRunner.Channel', null, {
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
     * Has this channel been wired up before?
     */
    _neverBeenWired: true,

    /**
     * Fixes up the publish to use the queue
     */
    constructor: function() {
        this.publish = this._publishQueue
        this.localDojo = dojo;
    },

    /**
     * Tell the channel where the remote communications will go
     *
     * @param subjectFrame An iframe DOM element
     */
    setSubject: function(subjectFrame) {
        this.subjectFrame = subjectFrame;

        this.onRemoteDojoLoad(dojo.hitch(this, function() {
            this._wire();

            this.subjectFrame.contentWindow.dojo.addOnWindowUnload(dojo.hitch(this, function() {
                this._unwire();
                this.setSubject(this.subjectFrame);
            }));
        }));
    },

    /**
     * Move the subject frame's location to another URL
     *
     * @param url
     */
    navigate: function(url) {
        this.subjectFrame.contentWindow.location = url;

        this._unwire();
    },

    /**
     * Monitors the subjects dojo object, when it detects a change it calls
     * the callback provided
     *
     * @param callback Must be a function
     */
    onRemoteDojoLoad: function(callback) {
        if (this.subjectFrame.contentWindow.dojo && this._neverBeenWired) {
            this._neverBeenWired = false;
            callback();
            return;
        }

        if (!this.subjectFrame.contentWindow.dojo) {
            var checkForDojo = dojo.hitch(this, function() {
                if (this.subjectFrame.contentWindow.dojo) {
                    callback();
                    return;
                }
                setTimeout(checkForDojo, this._waitInterval);
            });
            checkForDojo();
        } else {
            this.subjectFrame.contentWindow.dojo._fingerprint = chirp.time(); 

            var checkFingerprint = dojo.hitch(this, function() {
                try {
                    if (this.subjectFrame.contentWindow.dojo._fingerprint == undefined) {
                        callback();
                        return;
                    }
                } catch (e) {
                    // pass
                }
                setTimeout(checkFingerprint, this._waitInterval);
            });
            checkFingerprint();
        }
    },

    /**
     * Waits for an object to exist on the subject, then calls func
     *
     * @param objectName What we are looking for, must be a string
     * @param func Callable function when the object is found
     */
    whenObject: function(objectName, func) {
        // We have to wait until everything is wired
        if (!this._wired) {
            setTimeout(dojo.hitch(this, function() {
                this.whenObject(objectName, func);
            }), this._waitInterval);
            return;
        }

        var timer = new dojox.timing.Timer(this._waitInterval);

        timer.started = chirp.time();

        var context = {
            timer: timer,
            timeout: 5000,
            objectName: objectName,
            object: undefined,
            func: func,
            scope: this
        };

        timer.onTick = dojo.hitch(context, function() {
            if (chirp.time() > (this.timer.started + this.timeout)) {
                // Timeout
                this.timer.stop();
                return;
            }

            if (!this.scope.subjectFrame.contentWindow.dojo) {
                // Let the timer continue
                return;
            }

            var object = this.scope.subjectFrame.contentWindow.dojo.getObject(this.objectName);

            if (dojo.isObject(object)) {
                // We found it
                this.object = object;
                this.timer.stop();
            }
        });

        timer.onStop = dojo.hitch(context, function() {
            if (this.object) {
                this.func(this.object);
            }
        });

        timer.start();
    },

    /**
     * Once the remote dojo is present, we can connect both sides
     */
    _wire: function() {
        this.publish = this._publishWired;

        // Everything that gets published to the remote dojo, we also want to receive
        this.localDojo.connect(this.subjectFrame.contentWindow.dojo, 'publish', dojo, 'publish');

        this.publish(ChirpTools.TestRunner.Events.Channel.RemoteReady, [ true ]);
        this.dumpQueue();

        this._wired = true;
    },

    /**
     * Disconnect
     */
    _unwire: function() {
        this._wired = false;

        this.publish = this._publishQueue;
    },

    /**
     * If we were not wired, and a call to publish was made we have an event
     * in the queue that was waiting to be published.
     *
     * This publishes the topics in the queue
     */
    dumpQueue: function() {
        for (var i in this.queue.publish) {
            var pair = this.queue.publish[i];
            if (dojo.isFunction(pair)) { continue; }
            this.publish(pair[0], pair[1]);
        }
        this.queue.publish = [];
    },

    /**
     * By default, this is what comes with the nekked' object
     */
    publish: function() {
        throw new ChirpTools.Error('Channel has not been initialized yet');
    },

    /**
     * Is the topic we are publishing real?
     *
     * @param topic String
     */
    _checkTopic: function(topic) {
        if (!topic) {
            throw new ChirpTools.Error('You are publishing an event that is undefined, check you spelling');
        }
    },

    /**
     * Once the user sets the nodes, this is used
     *
     * It pushes all stuff into a queue that will wait until things are ready
     *
     * @param topic String
     * @param args
     */
    _publishQueue: function(topic, args) {
        this._checkTopic(topic);
        this.queue.publish.push([topic, args]);
    },

    /**
     * Once everything is setup, now we can start publishing real events
     *
     * @param topic String
     * @param args
     */
    _publishWired: function(topic, args) {
        this._checkTopic(topic);
        this.localDojo.publish(topic, args);

        if (this.subjectFrame.contentWindow.dojo) {
            this.subjectFrame.contentWindow.dojo.publish(topic, args);
        }
    }
});

dojo.setObject('ChirpTools.TestRunner.Channel', new _ChirpTools.TestRunner.Channel());
