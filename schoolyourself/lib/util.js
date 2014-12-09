// Copyright 2014 School Yourself. All Rights Reserved.

/**
 * @fileoverview This file contains a bunch of utility methods that support
 *   player_viewport.js, which mostly are related to DOM manipulation.
 *
 * @author jjl@schoolyourself.org (John Lee)
 */


/**
 * This method returns a function, which, when executed, will simply call
 * method where 'object' is treated as the 'this'.
 */
function bind(object, method) {
  return function() {
    return method.apply(object, arguments);
  };
}


/**
 * This is shorthand for document.createElement(tagName). Returns the
 * newly created element.
 *
 * @param {string} tagName The tag name to give to the new DOM element.
 * @param {?Element=} parentElement If provided, appends the new element as a
 *   child to the given element.
 * @param {?string=} className If provided, assigns this class name.
 */
function createDom(tagName, parentElement, className) {
  var output = document.createElement(tagName);
  if (className) {
    output.setAttribute('class', className);
  }
  if (parentElement) {
    parentElement.appendChild(output);
  }
  return output;
}


/**
 * This is shorthand for document.createElement('div'). Returns the
 * newly created element.
 *
 * @param {?Element=} parentElement If provided, appends the new element as a
 *   child to the given element.
 * @param {?string=} className If provided, assigns this class name.
 */
function createDiv(parentElement, className) {
  return createDom('div', parentElement, className);
}


/**
 * Adds the given class name to the element.
 * @param {Element} element The HTML element to add to.
 * @param {string} cls The class name to add.
 */
function addClassName(element, cls) {
  var classString = element.getAttribute('class');
  if (classString === null) {
    element.setAttribute('class', cls);
    return;
  } else if (!hasClassName(element, cls)) {
    element.setAttribute('class', classString + ' ' + cls);
  }
}


/**
 * Modifies the element to remove the given class name.
 * @param {Element} element The HTML element to check.
 * @param {string} cls The class name to search for.
 */
function removeClassName(element, cls) {
  var classString = element.getAttribute('class');
  if (classString === null) {
    return;
  }

  var classes = classString.split(' ');
  var className = '';
  for (var i = 0; i < classes.length; ++i) {
    if (cls == classes[i]) {
      continue;
    }
    className += classes[i] + ' ';
  }
  className = className.trim();
  element.setAttribute('class', className);
}


/**
 * Returns true if the element has the given class name.
 * @param {Element|EventTarget} element The HTML element to check.
 * @param {string} cls The class name to search for.
 */
function hasClassName(element, cls) {
  var className = element.getAttribute('class');
  if (className !== null) {
    return className.split(' ').indexOf(cls) != -1;
  }
  return false;
}


/**
 * Appends an invisible span to the given element that takes up the full
 * height. This is a convenience method that makes it easier to vertically
 * center something within a variable-height container. Make the contents
 * of the container be an inline-block element with vertical-align:middle
 * and then add this to the container.
 *
 * @param {Element} container The container that contains the
 *   content to be vertically centered, into which we will append
 *   the newly created span.
 */
function addHeightFixSpan(container) {
  var fix = createDom('span');
  fix.style.height = '100%';
  fix.style.display = 'inline-block';
  fix.style.setProperty('vertical-align', 'middle');
  fix.style.setProperty('font-size', '0');
  container.appendChild(fix);
  return fix;
}


/**
 * @const
 * @private
 */
var STYLE_PREFIXES = ['', '-moz-', '-webkit-', '-o-', '-ms-'];

/**
 * Sets a style property that has -webkit, -moz, -ms, and -o variants.
 *
 * @param {Element} element
 * @param {string} property
 * @param {string} value
 */
function setPrefixedStyleProperty(element, property, value) {
  for (var i = 0; i < STYLE_PREFIXES.length; ++i) {
    element.style.setProperty(STYLE_PREFIXES[i] + property, value);
  }
}
