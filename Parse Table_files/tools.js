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

function extend(objekt, zuper) {
	_.extend(objekt, zuper);
	
	objekt.zuper = zuper;
}

function newObject(prototype) {
	function F() {
		// Deliberatley left empty
	}
	
	F.prototype = prototype;
	
	return new F();
}

function includes(array1, array2) {
	for (var i in array1) {
		if (array2.indexOf(array1[i]) < 0) {
			return false;
		}
	}
	
	return true;
}

function includeEachOther(array1, array2) {
	return includes(array1, array2) && includes(array2, array1);
}

function includesUsingEquals(array1, array2) {
	for (var i in array1) {
		if (indexOfUsingEquals(array1[i], array2) < 0) {
			return false;
		}
	}
	
	return true;
}

function includeEachOtherUsingEquals(array1, array2) {
	return includesUsingEquals(array1, array2) && includesUsingEquals(array2, array1);
}

function getOrCreateArray(dictionary, key) {
	var result = dictionary[key];
	
	if (result == undefined) {
		result = [];
		dictionary[key] = result;
	}
	
	return result;
}

/**
 * @return
 * <br>Array
 * <br>New
 */
function trimElements(array) {
	var result = [];
	
	for (var i in array) {
		result[i] = array[i].trim();
	}
	
	return result;
}

function isElement(element, array) {
	for (var i in array) {
		if (element == array[i]) {
			return true;
		}
	}
	
	return false;
}

/**
 * @param array
 * <br>Input-output
 * @return <code>true</code> iff <code>array</code> has been modified
 */
function addUnique(element, array) {
	if (!isElement(element, array)) {
		array.push(element);
		
		return true;
	}
	
	return false;
}

function isElementUsingEquals(element, array) {
	for (var i in array) {
		if (element.equals(array[i])) {
			return true;
		}
	}
	
	return false;
}

/**
 * @param array
 * <br>Input-output
 * @return <code>true</code> iff <code>array</code> has been modified
 */
function addUniqueUsingEquals(element, array) {
	if (!isElementUsingEquals(element, array)) {
		array.push(element);
		
		return true;
	}
	
	return false;
}

/**
 * @return
 * <br>Range: <code>[-1 .. array.length - 1]</code>
 */
function indexOfUsingEquals(element, array) {
	for (var i in array) {
		if (element.equals(array[i])) {
			return i;
		}
	}
	
	return -1;
}

function $element(id) {
	return document.getElementById(id);
}

function assertEquality(expected, actual) {
	if (expected != actual) {
		throw 'Assertion failed: expected ' + expected + ' but was ' + actual;
	}
}
	
function assertEquals(expected, actual) {
	if (!expected.equals(actual)) {
		throw 'Assertion failed: expected ' + expected + ' but was ' + actual;
	}
}

function resize(textInput, minimumSize) {
	textInput.size = Math.max(minimumSize, textInput.value.length);
}
