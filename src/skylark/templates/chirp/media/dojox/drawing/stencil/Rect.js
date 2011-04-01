/*
	Copyright (c) 2004-2011, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


if(!dojo._hasResource["dojox.drawing.stencil.Rect"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["dojox.drawing.stencil.Rect"] = true;
dojo.provide("dojox.drawing.stencil.Rect");


dojox.drawing.stencil.Rect = dojox.drawing.util.oo.declare(
	// summary:
	//		Creates a dojox.gfx rectangle based on data or points provided.
	//
	dojox.drawing.stencil._Base,
	function(options){
		// summary:
		//		constructor
		if(this.points.length){
			//this.render();
		}
	},
	{
		type:"dojox.drawing.stencil.Rect",
		anchorType: "group",
		baseRender:true,
		
		dataToPoints: function(/*Object*/d){
			//summary:
			//		Converts data to points.
			d = d || this.data;
			this.points = [
				{x:d.x, y:d.y}, 						// TL
				{x:d.x + d.width, y:d.y},				// TR
				{x:d.x + d.width, y:d.y + d.height},	// BR
				{x:d.x, y:d.y + d.height}				// BL
			];
			return this.points;
		},
		
		pointsToData: function(/*Array*/p){
			// summary:
			//		Converts points to data
			p = p || this.points;
			var s = p[0];
			var e = p[2];
			this.data = {
				x: s.x,
				y: s.y,
				width: e.x-s.x,
				height: e.y-s.y,
				r:this.data.r || 0
			};
			return this.data;
			
		},
		
		_create: function(/*String*/shp, /*StencilData*/d, /*Object*/sty){
			// summary:
			//		Creates a dojox.gfx.shape based on passed arguments.
			//		Can be called many times by implementation to create
			//		multiple shapes in one stencil.
			//
			//console.log("render rect", d)
			//console.log("rect sty:", sty)
			this.remove(this[shp]);
			this[shp] = this.container.createRect(d)
				.setStroke(sty)
				.setFill(sty.fill);
			
			this._setNodeAtts(this[shp]);
		},
		
		render: function(){
			// summary:
			//		Renders the 'hit' object (the shape used for an expanded
			//		hit area and for highlighting) and the'shape' (the actual
			//		display object).
			//
			this.onBeforeRender(this);
			this.renderHit && this._create("hit", this.data, this.style.currentHit);
			this._create("shape", this.data, this.style.current);
		}
	}
);

dojox.drawing.register({
	name:"dojox.drawing.stencil.Rect"
}, "stencil");

}
