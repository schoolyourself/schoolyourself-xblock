function SchoolYourselfReviewStudentView(runtime, element) {
  var viewport = schoolyourself.PlayerViewportBuilder.insert(1024, 768);
  $(function ($) {
    $('.schoolyourself-lesson-player', element).click(function(eventObject) {
      viewport.openFrame(this.getAttribute('data-url'));
    });

    window.addEventListener('message', function(event) {
      if (event.source != viewport.frame().contentWindow) {
        return;
      }
      var handlerUrl = runtime.handlerUrl(element, 'handle_grade');
      $.post(handlerUrl, JSON.stringify(event.data));
    }, false);

    var masteryUrl = $('.schoolyourself-lesson-player', element)[0].getAttribute('data-mastery-url');
    updateMastery(masteryUrl);
    viewport.addAfterCloseHandler(function(){updateMastery(masteryUrl)});
  });
}

function renderMastery(masteries) {
  var mastery = masteries[0][1];

  // A mastery level of 0.7 gives full credit -- anything beyond that
  // doesn't count toward anything. So we should show a full, green bar
  // when scaledMastery >= 0.7.
  var scaledMastery = mastery / 0.7;

  var right = (100 - (scaledMastery * 100)) + '%';

  var color = '#fcd380';
  if (!scaledMastery) {
    var text = 'Get started!';
  } else if (scaledMastery < 0.5) {
    var text = 'Keep practicing!';
  } else if (scaledMastery < 1) {
    var text = 'Almost there!';
    var color = '#f0b300';
  } else {
    var text = 'Complete!';
    var color = '#6eb535';
  }

  $('.schoolyourself-review-mastery-text').html(text);
  $('.schoolyourself-review-mastery-bar-filler').css('right', right);
  $('.schoolyourself-review-mastery-bar-filler').css('background', color);
}

  function updateMastery(masteryUrl) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', masteryUrl, true);
  xhr.withCredentials = true;
  xhr.send();
  xhr.onreadystatechange = function(event) {
    if (xhr.readyState === 4 &&
        xhr.status === 200) {
      renderMastery($.parseJSON(xhr.responseText));
    }
  };
}
