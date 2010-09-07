dojo.provide('ChirpTools.TestRunner.TestCaseMvcInstances');

/**
 * A collection of MVC objects on the current page
 */
dojo.setObject('ChirpTools.TestRunner.TestCaseMvcInstances', {
    /**
     * Adds an instance to the instances array
     *
     * @param instance Either a ChirpTools.Mvc.Controller or ChirpTools.Mvc.View
     */
    addMvcInstance: function(instance) {
        ChirpTools.TestRunner.TestCaseMvcInstances.instances.push(instance);
    },

    /**
     * Array to hold the instances
     */
    instances: []
});

dojo.subscribe(ChirpTools.Mvc.Events.New.Controller, ChirpTools.TestRunner.TestCaseMvcInstances.addMvcInstance);
dojo.subscribe(ChirpTools.Mvc.Events.New.View, ChirpTools.TestRunner.TestCaseMvcInstances.addMvcInstance);
