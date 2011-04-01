/*
	Copyright (c) 2004-2011, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


if(!dojo._hasResource["dojox.grid.enhanced.plugins.Dialog"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["dojox.grid.enhanced.plugins.Dialog"] = true;
dojo.provide("dojox.grid.enhanced.plugins.Dialog");

dojo.require("dijit.Dialog");
dojo.require("dojo.window");

dojo.declare("dojox.grid.enhanced.plugins.Dialog", dijit.Dialog, {
	refNode: null,
	_position: function(){
		if(this.refNode && !this._relativePosition){
			var refPos = dojo.position(dojo.byId(this.refNode)),
				thisPos = dojo.position(this.domNode),
				viewPort = dojo.window.getBox();
			if(refPos.x < 0){
				refPos.x = 0;
			}
			if(refPos.x + refPos.w > viewPort.w){
				refPos.w = viewPort.w - refPos.x;
			}
			if(refPos.y < 0){
				refPos.y = 0;
			}
			if(refPos.y + refPos.h > viewPort.h){
				refPos.h = viewPort.h - refPos.y;
			}
			refPos.x = refPos.x + refPos.w / 2 - thisPos.w / 2;
			refPos.y = refPos.y + refPos.h / 2 - thisPos.h / 2;
			if(refPos.x >= 0 && refPos.x + thisPos.w <= viewPort.w &&
				refPos.y >= 0 && refPos.y + thisPos.h <= viewPort.h){
				this._relativePosition = refPos;
			}
		}
		this.inherited(arguments);
	}
});

}
