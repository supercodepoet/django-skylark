/*
	Copyright (c) 2004-2011, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


if(!dojo._hasResource["dojox.gfx"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["dojox.gfx"] = true;
dojo.provide("dojox.gfx");

dojo.require("dojox.gfx.matrix");
dojo.require("dojox.gfx._base");

dojo.loadInit(function(){
	// Since loaderInit can be fired before any dojo.provide/require calls,
	// make sure the dojox.gfx object exists and only run this logic if dojox.gfx.renderer
	// has not been defined yet.
	var gfx = dojo.getObject("dojox.gfx", true), sl, flag, match;
	while(!gfx.renderer){
		// Have a way to force a GFX renderer, if so desired.
		// Useful for being able to serialize GFX data in a particular format.
		if(dojo.config.forceGfxRenderer){
			dojox.gfx.renderer = dojo.config.forceGfxRenderer;
			break;
		}
		var renderers = (typeof dojo.config.gfxRenderer == "string" ?
			dojo.config.gfxRenderer : "svg,vml,canvas,silverlight").split(",");
		for(var i = 0; i < renderers.length; ++i){
			switch(renderers[i]){
				case "svg":
					// the next test is from https://github.com/phiggins42/has.js
					if("SVGAngle" in dojo.global){
						dojox.gfx.renderer = "svg";
					}
					break;
				case "vml":
					if(dojo.isIE){
						dojox.gfx.renderer = "vml";
					}
					break;
				case "silverlight":
					try{
						if(dojo.isIE){
							sl = new ActiveXObject("AgControl.AgControl");
							if(sl && sl.IsVersionSupported("1.0")){
								flag = true;
							}
						}else{
							if(navigator.plugins["Silverlight Plug-In"]){
								flag = true;
							}
						}
					}catch(e){
						flag = false;
					}finally{
						sl = null;
					}
					if(flag){
						dojox.gfx.renderer = "silverlight";
					}
					break;
				case "canvas":
					if(dojo.global.CanvasRenderingContext2D){
						dojox.gfx.renderer = "canvas";
					}
					break;
			}
			if(gfx.renderer){
				break;
			}
		}
		break;
	}
	
	if(dojo.config.isDebug){
		console.log("gfx renderer = " + gfx.renderer);
	}

	// load & initialize renderer
	if(gfx[gfx.renderer]){
		// already loaded
		gfx.switchTo(gfx.renderer);
	}else{
		// load
		gfx.loadAndSwitch = gfx.renderer;
		dojo["require"]("dojox.gfx." + gfx.renderer);
	}
});

}
