/*
 *  The MIT License
 * 
 *  Copyright 2011 Greg.
 * 
 *  Permission is hereby granted, free of charge, to any person obtaining a copy
 *  of this software and associated documentation files (the "Software"), to deal
 *  in the Software without restriction, including without limitation the rights
 *  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 *  copies of the Software, and to permit persons to whom the Software is
 *  furnished to do so, subject to the following conditions:
 * 
 *  The above copyright notice and this permission notice shall be included in
 *  all copies or substantial portions of the Software.
 * 
 *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 *  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 *  THE SOFTWARE.
 */

function LRTable(closureTable) {
	// <PUBLIC>
	
	this.grammar = closureTable.grammar;
	this.states = [];
	
	// </PUBLIC>
	
	// <INITIALIZATION>
	
	for (var i in closureTable.kernels) {
		var kernel = closureTable.kernels[i];
		var state = new State(this.states);
		
		for (var j in kernel.keys) {
			var key = kernel.keys[j];
			var nextStateIndex = kernel.gotos[key];
			
			getOrCreateArray(state, key).push(new LRAction((isElement(key, closureTable.grammar.terminals) ? 's' : ''), nextStateIndex));
		}
		
		for (var j in kernel.closure) {
			var item = kernel.closure[j];
			
			if (item.dotIndex == item.rule.development.length || item.rule.development[0] == EPSILON) {
				for (var k in item.lookAheads) {
					var lookAhead = item.lookAheads[k];

					getOrCreateArray(state, lookAhead).push(new LRAction('r', item.rule.index));
				}
			}
		}
	}
	
	// </INITIALIZATION>
}

/**
 * @param states
 * <br>Input-output
 */
function State(states) {
	// <PUBLIC>
	
	this.index = states.length;
	
	// </PUBLIC>
	
	// <INITIALIZATION>
	
	states.push(this);

	// <//INITIALIZATION>
}

function LRAction(actionType, actionValue) {
	// <PUBLIC>
	
	this.actionType = actionType;
	this.actionValue = actionValue;
	
	this.toString = function() {
		return this.actionType + this.actionValue;
	};
	
	// </PUBLIC>
}

function chooseActionElement(state, token) {
	var action = state[token];
	
	if (action == undefined) {
		return undefined;
	}
	
	var radios = document.getElementsByName(state.index + "_" + token);
	
	for (var i = 0; i < radios.length; ++i) {
		if (radios[i].checked) {
			return action[i];
		}
	}

	return action[0];
}
