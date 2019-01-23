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

var EPSILON = '\'\'';

function Grammar(text) {
	// <PUBLIC>
	
	this.alphabet = [];
	this.nonterminals = [];
	this.terminals = [];
	this.rules = [];
	this.firsts = new Object();
	this.follows = new Object();
	
	this.toString = function() {
		return this.rules.join('\n');
	};
	
	this.getRulesForNonterminal = function(nonterminal) {
		var result = [];
		
		for (var i in this.rules) {
			var rule = this.rules[i];
			
			if (nonterminal == rule.nonterminal) {
				result.push(rule);
			}
		}
		
		return result;
	};
	
	/**
	 * @param sequence
	 * <br>Array of symbols
	 * @result
	 * <br>Array of terminal symbols
	 * <br>New
	 */
	this.getSequenceFirsts = function(sequence) {
		var result = [];
		var epsilonInSymbolFirsts = true;
		
		for (var j in sequence) {
			var symbol = sequence[j];
			epsilonInSymbolFirsts = false;
			
			if (isElement(symbol, this.terminals)) {
				addUnique(symbol, result);
				
				break;
			}
			
			for (var k in this.firsts[symbol]) {
				var first = this.firsts[symbol][k];
				
				epsilonInSymbolFirsts |= first == EPSILON;
				
				addUnique(first, result);
			}
			
			epsilonInSymbolFirsts |= this.firsts[symbol] == undefined || this.firsts[symbol].length == 0;
			
			if (!epsilonInSymbolFirsts) {
				break;
			}
		}
		
		if (epsilonInSymbolFirsts) {
			addUnique(EPSILON, result);
		}
		
		return result;
	};
	
	// </PUBLIC>
	
	// <INITIALIZATION>
	
	initializeRulesAndAlphabetAndNonterminals(this);
	initializeAlphabetAndTerminals(this);
	initializeFirsts(this);
	initializeFollows(this);
	
	// </INITIALIZATION>
	
	// <PRIVATE>
	
	/**
	 * @param grammar
	 * <br>Input-output
	 */
	function initializeRulesAndAlphabetAndNonterminals(grammar) {
		var lines = text.split('\n');
		
		for (var i in lines) {
			var line = lines[i].trim();
			
			if (line != '') {
				var rule = new Rule(grammar, line);
				
				grammar.rules.push(rule);
				
				if (grammar.axiom == undefined) {
					grammar.axiom = rule.nonterminal;
				}
				
				addUnique(rule.nonterminal, grammar.alphabet);
				addUnique(rule.nonterminal, grammar.nonterminals);
			}
		}
	}
	
	/**
	 * @param grammar
	 * <br>Input-output
	 */
	function initializeAlphabetAndTerminals(grammar) {
		for (var i in grammar.rules) {
			var rule = grammar.rules[i];
			
			for (var j in rule.development) {
				var symbol = rule.development[j];
				
				if (symbol != EPSILON && !isElement(symbol, grammar.nonterminals)) {
					addUnique(symbol, grammar.alphabet);
					addUnique(symbol, grammar.terminals);
				}
			}
		}
	}
	
	/**
	 * @param grammar
	 * <br>Input-output
	 */
	function initializeFirsts(grammar) {
		var notDone;
		
		do {
			notDone = false;
			
			for (var i in grammar.rules) {
				var rule = grammar.rules[i];
				var nonterminalFirsts = getOrCreateArray(grammar.firsts, rule.nonterminal);
				
				if (rule.development.length == 1 && rule.development[0] == EPSILON) {
					notDone |= addUnique(EPSILON, nonterminalFirsts);
				} else {
					notDone |= collectDevelopmentFirsts(grammar, rule.development, nonterminalFirsts);
				}
			}
		} while (notDone);
	}
	
	/**
	 * @param grammar
	 * <br>Input-output
	 * @param development
	 * <br>Array of symbols
	 * @param nonterminalFirsts
	 * <br>Array of symbols
	 * <br>Input-output
	 * @return <code>true</code> If <code>nonterminalFirsts</code> has been modified
	 */
	function collectDevelopmentFirsts(grammar, development, nonterminalFirsts) {
		var result = false;
		var epsilonInSymbolFirsts = true;
		
		for (var j in development) {
			var symbol = development[j];
			epsilonInSymbolFirsts = false;
	
			if (isElement(symbol, grammar.terminals)) {
				result |= addUnique(symbol, nonterminalFirsts);
				
				break;
			}
			
			for (var k in grammar.firsts[symbol]) {
				var first = grammar.firsts[symbol][k];
				
				epsilonInSymbolFirsts |= first == EPSILON;
				
				result |= addUnique(first, nonterminalFirsts);
			}
			
			if (!epsilonInSymbolFirsts) {
				break;
			}
		}
		
		if (epsilonInSymbolFirsts) {
			result |= addUnique(EPSILON, nonterminalFirsts);
		}
		
		return result;
	}
	
	/**
	 * @param grammar
	 * <br>Input-output
	 */
	function initializeFollows(grammar) {
		var notDone;
		
		do {
			notDone = false;
			
			for (var i in grammar.rules) {
				var rule = grammar.rules[i];
				
				if (i == 0) {
					var nonterminalFollows = getOrCreateArray(grammar.follows, rule.nonterminal);
					
					notDone |= addUnique('$', nonterminalFollows);
				}
				
				for (var j in rule.development) {
					var symbol = rule.development[j];
					
					if (isElement(symbol, grammar.nonterminals)) {
						var symbolFollows = getOrCreateArray(grammar.follows, symbol);
						var afterSymbolFirsts = grammar.getSequenceFirsts(rule.development.slice(parseInt(j) + 1));
						
						for (var k in afterSymbolFirsts) {
							var first = afterSymbolFirsts[k];
							
							if (first == EPSILON) {
								var nonterminalFollows = grammar.follows[rule.nonterminal];
								
								for (var l in nonterminalFollows) {
									notDone |= addUnique(nonterminalFollows[l], symbolFollows);
								}
							} else {
								notDone |= addUnique(first, symbolFollows);
							}
						}
					}
				}
			}
		} while (notDone);
	}
	
	// </PRIVATE>
}

function Rule(grammar, text) {
	// <PUBLIC>
	
	this.grammar = grammar;
	this.index = grammar.rules.length;
	
	var split = text.split('->');
	
	this.nonterminal = split[0].trim();
	
	this.pattern = trimElements(this.nonterminal.split(' '));
	
	this.development = trimElements(split[1].trim().split(' '));
	
	this.toString = function() {
		return this.nonterminal + ' -> ' + this.development.join(' ');
	};

	this.equals = function(that) {
		if (this.nonterminal != that.nonterminal) {
			return false;
		}
		
		if (parseInt(this.development.length) != parseInt(that.development.length)) {
			return false;
		}
		
		for (var i in this.development) {
			if (this.development[i] != that.development[i]) {
				return false;
			}
		}
		
		return true;
	};
	
	// </PUBLIC>
}

function BasicItem(rule, dotIndex) {
	// <PUBLIC>
	
	this.rule = rule;
	
	this.dotIndex = dotIndex;
	
	this.lookAheads = [];
	
	this.addUniqueTo = function(items) {
		return addUniqueUsingEquals(this, items);
	};
	
	this.newItemsFromSymbolAfterDot = function() {
		var result = [];
		var nonterminalRules = this.rule.grammar.getRulesForNonterminal(this.rule.development[this.dotIndex]);
		
		for (var j in nonterminalRules) {
			addUniqueUsingEquals(new Item(nonterminalRules[j], 0), result);
		}
		
		return result;
	};
	
	this.newItemAfterShift = function() {
		if (this.dotIndex < this.rule.development.length && this.rule.development[this.dotIndex] != EPSILON) {
			return new Item(this.rule, this.dotIndex + 1);
		}
		
		return undefined;
	}
	
	this.equals = function(that) {
		return this.rule.equals(that.rule) && (parseInt(this.dotIndex) == parseInt(that.dotIndex));
	};

	this.toString = function() {
		return this.rule.nonterminal + ' -> ' + this.rule.development.slice(0, this.dotIndex).join(' ') + '.' +
				(isElement(EPSILON, this.rule.development) ? '' : this.rule.development.slice(this.dotIndex).join(' '));
	};
	
	// </PUBLIC>
}

function BasicLR1Item(rule, dotIndex) {
	// <PUBLIC>
	
	extend(this, new BasicItem(rule, dotIndex));
	
	var zuper = this.zuper;
	
	this.lookAheads = rule.index == 0 ? ['$'] : [];
	
	this.newItemsFromSymbolAfterDot = function() {
		var result = this.zuper.newItemsFromSymbolAfterDot();
		
		if (result.length == 0) {
			return result;
		}
		
		var newLookAheads = [];
		var epsilonPresent = false;
		var firstsAfterSymbolAfterDot = this.rule.grammar.getSequenceFirsts(this.rule.development.slice(this.dotIndex + 1));
		
		for (var i in firstsAfterSymbolAfterDot) {
			var first = firstsAfterSymbolAfterDot[i];
			if (EPSILON == first) {
				epsilonPresent = true;
			} else {
				addUnique(first, newLookAheads);
			}
		}
		
		if (epsilonPresent) {
			for (var i in this.lookAheads) {
				addUnique(this.lookAheads[i], newLookAheads);
			}
		}
		
		for (var i in result) {
			result[i].lookAheads = newLookAheads.slice(0);
		}
		
		return result;
	};
	
	this.newItemAfterShift = function() {
		var result = zuper.newItemAfterShift();
		
		if (result != undefined) {
			result.lookAheads = this.lookAheads.slice(0);
		}
		
		return result;
	}
	
	this.addUniqueTo = function(items) {
		var result = false;
		
		for (var i in items) {
			var item = items[i];
			
			if (zuper.equals(item)) {
				for (var i in this.lookAheads) {
					result |= addUnique(this.lookAheads[i], item.lookAheads);
				}
				
				return result;
			}
		}
		
		items.push(this);
		
		return true;
	};
	
	this.equals = function(that) {
		return zuper.equals(that) && includeEachOther(this.lookAheads, that.lookAheads);
	}

	this.toString = function() {
		return '[' + zuper.toString() + ', ' + this.lookAheads.join('/') + ']';
	};
	
	// </PUBLIC>
}
