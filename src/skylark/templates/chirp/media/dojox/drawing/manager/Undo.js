/*
	Copyright (c) 2004-2011, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


if(!dojo._hasResource["dojox.drawing.manager.Undo"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["dojox.drawing.manager.Undo"] = true;
dojo.provide("dojox.drawing.manager.Undo");

dojox.drawing.manager.Undo = dojox.drawing.util.oo.declare(
	// summary
	//	Handles the Undo in drawing.
	//	NOTE: Only partially implemented!!! There is very
	//		little actual undo functionality!
	//
	function(options){
		this.keys = options.keys;
		this.undostack = [];
		this.redostack = [];
		dojo.connect(this.keys, "onKeyDown", this, "onKeyDown");
	},
	{
		onKeyDown: function(evt){
			if(!evt.cmmd){ return; }
			
			if(evt.keyCode==90 && !evt.shift){
				this.undo();
			}else if((evt.keyCode == 90 && evt.shift) || evt.keyCode==89){
				this.redo();
			}
			
		},
		add: function(stack){
			//console.log("undo add", stack)
			stack.args = dojo.mixin({}, stack.args);
			this.undostack.push(stack);
		},
		apply: function(scope, method, args){
			dojo.hitch(scope, method)(args);
		},
		undo: function(){
			
			var o = this.undostack.pop();
			console.log("undo!", o);
			if(!o){ return; }
			
			o.before();
			
			this.redostack.push(o);
		},
		redo: function(){
			console.log("redo!");
			var o = this.redostack.pop();
			if(!o){ return; }
			if(o.after){
				o.after();
			}else{
				o.before(); ///??????
			}
			
			this.undostack.push(o);
		}
	}
);

}
