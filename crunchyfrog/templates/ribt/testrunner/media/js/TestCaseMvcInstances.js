dojo.provide('RibtTools.TestRunner.TestCaseMvcInstances');

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
