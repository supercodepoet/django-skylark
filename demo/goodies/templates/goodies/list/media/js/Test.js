dojo.provide('Whizzo.Goodies.List.Test');

dojo.require('RibtTools.TestRunner.TestCase');

dojo.declare('Whizzo.Goodies.List.Test', RibtTools.TestRunner.TestCase, {
    testCanSeeJQueryTabs: function() {
        this.exists('div.ui-tabs');

        this.then(function() {
            var view = this.getController('Whizzo.Goodies.List.View')[0];

            view.numberFrogsEaten.value = '5';

            view.tellUsAboutFrogsOnClick(undefined);
        });
    }
});
