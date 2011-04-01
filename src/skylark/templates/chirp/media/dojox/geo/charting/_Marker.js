/*
	Copyright (c) 2004-2011, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


if(!dojo._hasResource["dojox.geo.charting._Marker"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["dojox.geo.charting._Marker"] = true;
dojo.provide("dojox.geo.charting._Marker");

dojo.declare("dojox.geo.charting._Marker", null, {
	constructor: function(markerData, map){
		var mapObj = map.mapObj;
		this.features = mapObj.features;
		this.markerData = markerData;
	},

	show: function(featureId){
		this.markerText = this.features[featureId].markerText || this.markerData[featureId] || featureId;
		this.currentFeature = this.features[featureId];
		dojox.geo.charting.showTooltip(this.markerText, this.currentFeature.shape, "before");
	},

	hide: function(){
		dojox.geo.charting.hideTooltip(this.currentFeature.shape);
	},

	_getGroupBoundingBox: function(group){
		var shapes = group.children;
		var feature = shapes[0];
		var bbox = feature.getBoundingBox();
		this._arround = dojo.clone(bbox);
		dojo.forEach(shapes, function(item){
			var _bbox = item.getBoundingBox();
			this._arround.x = Math.min(this._arround.x, _bbox.x);
			this._arround.y = Math.min(this._arround.y, _bbox.y);
		},this);
	},

	_toWindowCoords: function(arround, coords, containerSize){
		var toLeft = (arround.x - this.topLeft[0]) * this.scale;
		var toTop = (arround.y - this.topLeft[1]) * this.scale
		if (dojo.isFF == 3.5) {
			arround.x = coords.x;
			arround.y = coords.y;
		}
		else if (dojo.isChrome) {
			arround.x = containerSize.x + toLeft;
			arround.y = containerSize.y + toTop;
		}
		else {
			arround.x = coords.x + toLeft;
			arround.y = coords.y + toTop;
		}
		arround.width = (this.currentFeature._bbox[2]) * this.scale;
		arround.height = (this.currentFeature._bbox[3]) * this.scale;
		arround.x += arround.width / 6;
		arround.y += arround.height / 4;
	}
});

}
