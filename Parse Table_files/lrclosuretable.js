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

function LRClosureTable(grammar) {
	// <PUBLIC>
	
	this.grammar = grammar;
	this.kernels = [];
	
	// </PUBLIC>
	
	// <INITIALIZATION>
	
	this.kernels.push(new Kernel(0, [new Item(grammar.rules[0], 0)], grammar));
	
	for (var i = 0; i < this.kernels.length;) {
		var kernel = this.kernels[i];
		
		updateClosure(kernel);
		
		if (addGotos(kernel, this.kernels)) {
			i = 0;
		} else {
			++i;
		}
	}
	
	// </INITIALIZATION>
	
	// <PRIVATE>
	
	/**
	 * @param kernel
	 * <br>Input-output
	 */
	function updateClosure(kernel) {
		for (var i = 0; i < kernel.closure.length; ++i) {
			var newItemsFromSymbolAfterDot = kernel.closure[i].newItemsFromSymbolAfterDot();
			
			for (var j in newItemsFromSymbolAfterDot) {
				newItemsFromSymbolAfterDot[j].addUniqueTo(kernel.closure);
			}
		}
	}
	
	/**
	 * @param kernel
	 * <br>Input-output
	 * @param kernels
	 * <br>Input-output
	 */
	function addGotos(kernel, kernels) {
		var lookAheadsPropagated = false;
		var newKernels = new Object();
		
		for (var i in kernel.closure) {
			var item = kernel.closure[i];
			var newItem = item.newItemAfterShift();
			
			if (newItem != undefined) {
				var symbolAfterDot = item.rule.development[item.dotIndex];
				
				addUnique(symbolAfterDot, kernel.keys);
				newItem.addUniqueTo(getOrCreateArray(newKernels, symbolAfterDot));
			}
		}
		
		for (var i in kernel.keys) {
			var key = kernel.keys[i];
			var newKernel = new Kernel(kernels.length, newKernels[key], grammar);
			var targetKernelIndex = indexOfUsingEquals(newKernel, kernels);
			
			if (targetKernelIndex < 0) {
				kernels.push(newKernel);
				targetKernelIndex = newKernel.index;
			} else {
				for (var j in newKernel.items) {
					lookAheadsPropagated |= newKernel.items[j].addUniqueTo(kernels[targetKernelIndex].items);
				}
			}
			
			kernel.gotos[key] = targetKernelIndex;
		}
		
		return lookAheadsPropagated;
	}
	
	// </PRIVATE>
}

function Kernel(index, items, grammar) {
	// <PUBLIC>
	
	this.index = index;
	this.items = items;
	this.closure = this.items.slice(0);
	this.gotos = new Object();
	this.keys = [];
	
	this.equals = function(that) {
		return includeEachOtherUsingEquals(this.items, that.items);
	};
	
	this.toString = function() {
		return 'closure{' + this.items + '} = {' + this.closure + '}';
	};
	
	// </PUBLIC>
}
