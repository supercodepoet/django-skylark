dojo.provide('RibtTools.TestRunner.Display.TestEntryPoint');

dojo.declare('RibtTools.TestRunner.Display.TestEntryPoint', null, {
    constructor: function(url, name) {
        this.url = url;
        this.name = name;
    },

    setNode: function(node) {
        this.node = node;
    }
});
