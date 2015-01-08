// Copyright 2014 School Yourself. All Rights Reserved.

/**
 * @fileoverview This is a viewport that sits on top of a curtain. It is
 *   meant to be injected as a direct child of the <body> element. The
 *   builder takes care of creating the full-screen curtain.
 *
 * The viewport will automatically resize itself so that it fits in the
 * window, while preserving the aspect ratio specified by the maxWidth
 * and maxHeight parameters that you pass in.
 *
 * The PlayerViewportBuilder class is defined at the bottom of this
 * file, which just has a single static method which creates any
 * necessary elements in the DOM, injects it into the body, and
 * returns a PlayerViewport object.
 *
 * @author jjl@schoolyourself.org (John Lee)
 */

schoolyourself = window.schoolyourself || {};

/**
 * @param {Element} curtainElement The dark curtain that sits on top of
 *   everything. The actual content sits on top of this curtain.
 * @param {Element} contentContainer This is simply a container that
 *   holds the X button and the actual content div.
 * @param {Element} scaler This is the div that actually contains the
 *   real content. It will have the necessary CSS transformations applied
 *   to it so that it fits in the user's window.
 * @param {number} maxWidth The maximum width of the content, in pixels,
 *   if the user's viewport is big enough.
 * @param {number} maxHeight The maximum height of the content, in pixels,
 *   if the user's viewport is big enough.
 * @constructor
 * @export
 */
schoolyourself.PlayerViewport = function(curtainElement, contentContainer,
                                         scaler, maxWidth, maxHeight) {
  this.curtain_ = curtainElement;
  this.contentContainer_ = contentContainer;
  this.scaler_ = scaler;
  this.maxWidth_ = maxWidth;
  this.maxHeight_ = maxHeight;

  this.isOpen_ = false;

  /**
   * The function to call when the user closes the viewport.
   * This function should return a boolean: true to continue with the
   * closing, and false otherwise.
   *
   * @type {?function():boolean}
   */
  this.onClose_ = null;

  /**
   * The functions to call when when the viewport actually gets closed.
   *
   * @type {Array.<function()>}
   */
  this.afterClose_ = [];

  /**
   * When the frame is open, this holds the iframe element. Null when
   * the iframe is closed.
   * @type {?Element}
   */
  this.currentFrame_ = null;
};


schoolyourself.PlayerViewport.prototype.resize = function() {
  if (!this.isOpen_) {
    return;
  }

  // Compute the size that we should scale to. First, let's see what the
  // maximum possible widths and heights are.
  var width = Math.min(this.curtain_.offsetWidth, this.maxWidth_);
  var height = Math.min(this.curtain_.offsetHeight, this.maxHeight_);

  // Now, if the resulting width/height doesn't match the desired
  // aspect ratio, we'll adjust either the width or height (whichever
  // is too big).
  var desiredAspectRatio = this.maxWidth_ / this.maxHeight_;

  // If the proposed size is too tall, we'll adjust the height to be a
  // function of the width.
  if ((width / height) < desiredAspectRatio) {
    height = width / desiredAspectRatio;
  } else {
    // If the proposed size is too wide, we'll adjust the width to be a
    // function of the height.
    width = desiredAspectRatio * height;
  }

  width = Math.floor(width);
  height = Math.floor(height);
  this.contentContainer_.style.width = width + 'px';
  this.contentContainer_.style.height = height + 'px';

  var scaleWidthFactor = this.maxWidth_ / width;
  var scaleHeightFactor = this.maxHeight_ / height;
  var transformString = '';
  if (scaleWidthFactor <= 1 && scaleHeightFactor <= 1) {
    transformString = '';
  } else if (scaleWidthFactor > scaleHeightFactor) {
    transformString = 'scale(' + (1/scaleWidthFactor) + ')';
  } else {
    transformString = 'scale(' + (1/scaleHeightFactor) + ')';
  }

  setPrefixedStyleProperty(this.scaler_, 'transform', transformString);
  setPrefixedStyleProperty(this.scaler_, 'transform-origin', '0 0');
};


schoolyourself.PlayerViewport.prototype.isOpen = function() {
  return this.isOpen_;
};


schoolyourself.PlayerViewport.prototype.open = function() {
  this.resize();
  addClassName(this.curtain_, 'open');
  this.isOpen_ = true;
};


/**
 * This is another version of open() which creates an iframe pointing
 * at the given url and places it into the scaler.
 * @param {string} url
 * @export
 */
schoolyourself.PlayerViewport.prototype.openFrame = function(url) {
  var iframe = createDom('iframe', this.scaler_, 'player-viewport-frame');
  iframe.setAttribute('tabindex', 0);
  iframe.focus();
  iframe.src = url;
  iframe.scrolling = 'no';
  this.currentFrame_ = iframe;

  addClassName(this.curtain_, 'open');
  this.isOpen_ = true;
  this.resize();
};


/**
 * If we have an onclose handler, this will call that first, and we will
 * only actually close the window if it returns true.
 *
 * If we don't have an onclose handler, we just close the window
 * immediately.
 */
schoolyourself.PlayerViewport.prototype.close = function() {
  if (this.onClose_) {
    var reallyShouldClose = this.onClose_();
    if (!reallyShouldClose) {
      return;
    }
  }

  this.isOpen_ = false;
  this.scaler_.innerHTML = '';
  removeClassName(this.curtain_, 'open');
  this.currentFrame_ = null;
  for (var i = 0; i < this.afterClose_.length; ++i) {
    this.afterClose_[i]();
  }
};


/**
 * @param {function():boolean} fn The function to call when the user
 *   clicks on the close button. It should return true if we actually
 *   want to close the window. Returning false prevents the window
 *   from closing.
 */
schoolyourself.PlayerViewport.prototype.setCloseHandler = function(fn) {
  this.onClose_ = fn;
};


/**
 * @param {function()} fn The function to call after the window
 *   gets closed.
 * @export
 */
schoolyourself.PlayerViewport.prototype.addAfterCloseHandler = function(fn) {
  this.afterClose_.push(fn);
};

/**
 * Return a handle to the open frame, or null if there isn't one open.
 * @return {?Element}
 * @export
 */
schoolyourself.PlayerViewport.prototype.frame = function() {
  return this.currentFrame_;
};



/**
 * @constructor
 */
schoolyourself.PlayerViewportBuilder = function() {};


/**
 * This method will insert a new viewport into the DOM, directly under
 * the <body> element, and then return the PlayerViewport object that
 * controls it.
 *
 * It will scale the content so that it is always centered and fits in
 * the window, above a semitransparent curtain. The maxWidth and
 * maxHeight parameters control the maximum size of the centered
 * element.
 *
 * @param {number} maxWidth The max width of the content after
 *   scaling, in pixels.
 * @param {number} maxHeight The max width of the content after
 *   scaling, in pixels.
 *
 * @return {schoolyourself.PlayerViewport}
 * @export
 */
schoolyourself.PlayerViewportBuilder.insert = function(maxWidth, maxHeight) {
  var schoolyourselfContainer = createDiv(
    document.body,
    'schoolyourself player-viewport-container');
  var curtain = createDiv(schoolyourselfContainer,
                          'player-viewport-curtain');
  var contentContainer = createDiv(curtain, 'player-viewport-content');

  var xButton = createDom('a', curtain, 'player-viewport-x');
  xButton.href = '#';
  var scaler = createDiv(contentContainer, 'player-viewport-scaler');

  contentContainer.style.width = maxWidth + 'px';
  contentContainer.style.height = maxHeight + 'px';

  scaler.style.width = maxWidth + 'px';
  scaler.style.height = maxHeight + 'px';

  addHeightFixSpan(curtain);

  var viewport = new schoolyourself.PlayerViewport(curtain, contentContainer,
                                                   scaler,
                                                   maxWidth, maxHeight);
  xButton.onclick = bind(viewport, viewport.close);
  window.addEventListener('resize', bind(viewport, viewport.resize), false);
  return viewport;
};
