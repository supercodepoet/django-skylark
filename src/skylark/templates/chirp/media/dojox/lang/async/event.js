/*
	Copyright (c) 2004-2011, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


if(!dojo._hasResource["dojox.lang.async.event"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["dojox.lang.async.event"] = true;
dojo.provide("dojox.lang.async.event");

// Source of Deferred for events

(function(){
	var d = dojo, event = dojox.lang.async.event;

	event.from = function(src, name){
		return function(){
			var h, cancel = function(){
					if(h){
						d.disconnect(h);
						h = null;
					}
				},
				x = new d.Deferred(cancel);
			h = d.connect(src, name, function(evt){
				cancel();
				x.callback(evt);
			});
			return x;
		};
	};

	event.failOn = function(src, name){
		return function(){
			var h, cancel = function(){
					if(h){
						d.disconnect(h);
						h = null;
					}
				},
				x = new d.Deferred(cancel);
			h = d.connect(src, name, function(evt){
				cancel();
				x.errback(new Error(evt));
			});
			return x;
		};
	};
})();

}
