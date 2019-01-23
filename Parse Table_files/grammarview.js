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

function formatGrammar(grammar) {
	var result = '';
	if (typeof(Item) != 'undefined') {
		result += "<div>" + Item.prototype.grammarType + " grammar ('' is &epsilon;):</div>";
	}
	result += "<table><tbody><tr>";
	result += "<td><textarea style=\"text-align: right; border: 0; color: green; background-color: #F0F0F0\" id=\"ruleIndices\" rows=\"25\" cols=\"3\" readonly=\"true\">";
	result += "</textarea></td>";
	result += "<td><textarea id=\"grammar\" rows=\"25\" cols=\"20\" onfocus=\"$('ruleIndices').value = ''\" onblur=\"displayRuleIndices();\" onchange=\"grammarChanged();\">";
	
	for (var i in grammar.rules) {
		result += grammar.rules[i] + "\n";
	}
	
	result += "</textarea></td>";
	result += "</tr></tbody></table>";
	
	return result;
}

function displayRuleIndices() {
	var rules = $element('grammar').value.split('\n');
	var ruleIndex = 0;
	
	$element('ruleIndices').value = "";
	
	for (var i in rules) {
		if (rules[i].trim() != '') {
			$element('ruleIndices').value += "(" + (ruleIndex++) + ")";
		}
		
		$element('ruleIndices').value += "\n";
	}
}

function formatFirstFollow(grammar) {
	var result = "<table border=\"1\">";
	
	if (Item.prototype.grammarType == 'SLR') {
		result += "<thead><tr><th colspan=\"3\">FIRST / FOLLOW table</th></tr><tr><th>Nonterminal</th><th>FIRST</th><th>FOLLOW</th></thead>"
		result += "<tbody>";
		
		for (var i in grammar.nonterminals) {
			var nonterminal = grammar.nonterminals[i];
			
			result += "<tr><td>" + nonterminal + "</td><td>{" + grammar.firsts[nonterminal] + "}</td><td>{" + grammar.follows[nonterminal] + "}</td></tr>";
		}
	} else {
		result += "<thead><tr><th colspan=\"2\">FIRST table</th></tr><tr><th>Nonterminal</th><th>FIRST</th></thead>"
		result += "<tbody>";
		
		for (var i in grammar.nonterminals) {
			var nonterminal = grammar.nonterminals[i];
			
			result += "<tr><td>" + nonterminal + "</td><td>{" + grammar.firsts[nonterminal] + "}</td></tr>";
		}
	}
	
	result += "</tbody>"
	result += "</table>";
	
	return result;
}
