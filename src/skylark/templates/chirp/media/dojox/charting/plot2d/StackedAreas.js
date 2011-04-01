/*
	Copyright (c) 2004-2011, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


if(!dojo._hasResource["dojox.charting.plot2d.StackedAreas"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["dojox.charting.plot2d.StackedAreas"] = true;
dojo.provide("dojox.charting.plot2d.StackedAreas");

dojo.require("dojox.charting.plot2d.Stacked");

dojo.declare("dojox.charting.plot2d.StackedAreas", dojox.charting.plot2d.Stacked, {
	//	summary:
	//		A convenience object to set up a stacked area plot.
	constructor: function(){
		//	summary:
		//		Force our Stacked plotter to include both lines and areas.
		this.opt.lines = true;
		this.opt.areas = true;
	}
});

}
