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

/**
 * Use formatInitialParseView() to create a parse view before calling this function.
 */
function parseInput() {
	// TODO refactoring
	var stack = [0];
	
	function stateIndex() {
		return stack[2 * ((stack.length - 1) >> 1)];
	}
	
	var tokens = ($element('input').value.trim() + ' $').split(' ');
	var maximumStepCount = parseInt($element('maximumStepCount').value);
	var tokenIndex = 0;
	var token = tokens[tokenIndex];
	var state = lrTable.states[stateIndex()];
	var action = state[token];
	var actionElement = chooseActionElement(state, token);
	var rows = "<tr><td>1</td><td>" + formatStack(stack) + "</td><td>" + tokens.slice(tokenIndex).join(' ') + "</td><td>" + formatAction(state, token, false) + "</td><td id=\"tree\" style=\"vertical-align: top;\"></td></tr>\n";
	var i = 2;
	
	while (i <= maximumStepCount && action != undefined && actionElement != 'r0') {
		if (actionElement.actionType == 's') {
			stack.push(tokens[tokenIndex++]);
			stack.push(parseInt(actionElement.actionValue));
		} else if (actionElement.actionType == 'r') {
			var ruleIndex = actionElement.actionValue;
			var rule = lrTable.grammar.rules[ruleIndex];
			var removeCount = isElement(EPSILON, rule.development) ? 0 : rule.development.length * 2;
			var removedElements = stack.splice(stack.length - removeCount, removeCount);
			var node = new Tree(rule.nonterminal, []);
			
			for (var j = 0; j < removedElements.length; j += 2) {
				node.children.push(removedElements[j]);
			}
			
			stack.push(node);
		} else {
			stack.push(parseInt(actionElement));
		}
		
		var state = lrTable.states[stateIndex()];
		var token = stack.length % 2 == 0 ? stack[stack.length - 1] : tokens[tokenIndex];
		action = state[token];
		actionElement = chooseActionElement(state, token);
		
		rows += "<tr><td>" + i + "</td><td>" + formatStack(stack) + "</td><td>" + tokens.slice(tokenIndex).join(' ') + "</td><td>" + formatAction(state, token, false) + "</td></tr>\n";
		++i;
	}
	
	$element('traceAndTreeRows').innerHTML = rows;
	$element('tree').rowSpan = i + 1;
	$element('tree').innerHTML = "&nbsp";
	
	$element('maximumStepCount').style.color = 'black';
	
	if (action == 'r0') {
		$element('input').style.color = 'green';
		$element('tree').innerHTML = formatTree(stack[1]);
	} else if (action == undefined) {
		$element('input').style.color = 'red';
	} else {
		$element('input').style.color = 'orange';
		$element('maximumStepCount').style.color = 'orange';
	}
}

function formatInitialParseView(input, maximumStepCount) {
	var result = "<p>Input (tokens): <input id=\"input\" type=\"text\" size=\"" + input.length + "\" onkeyup=\"resize(this, 1);\" onchange=\"parseInput();\" value=\"" + input + "\"></p>";
	result += "<p>Maximum number of steps: <input id=\"maximumStepCount\" type=\"text\" size=\""+ maximumStepCount.toString().length + "\" onkeyup=\"resize(this, 1);\" onchange=\"parseInput();\" value=\"" + maximumStepCount + "\"></p>";
	result += "<p><input type=\"button\" value=\"PARSE\"></p>";
	result += "<br>";
	result += "<table border=\"6\">";
	result += "<thead>";
	result += "<tr><th colspan=\"4\">Trace</th><th rowspan=\"2\">Tree</th></tr>";
	result += "<tr><th>Step</th><th>Stack</th><th>Input</th><th>Action</th></tr>";
	result += "</thead>";
	result += "<tbody id=\"traceAndTreeRows\">";
	result += "</tbody>";
	result += "</table>";
	result += "</div>";
	result += "</td></tr></tbody></table>";
	
	return result;
}

function formatStack(stack) {
	var result = stack.slice(0);
	
	for (var i = 0; i < result.length; i += 2) {
		result[i] = "<span style=\"color: blue;\">" + result[i] + "</span>";
	}
	
	return result.join(' ');
}
