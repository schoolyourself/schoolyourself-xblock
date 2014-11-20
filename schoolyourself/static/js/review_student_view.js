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
  var right = (100 - (mastery * 100)) + '%';

  var bg = '#ddd';
  if (!mastery) {
    var text = 'Get started!';
    var color = '#fcd380';
  } else if (mastery < 0.35) {
    var text = 'Keep practicing!';
    var color = '#fcd380';
  } else if (mastery < 0.7) {
    var text = 'Almost there!';
    var color = '#f0b300';
  } else if (mastery < 1) {
    var text = 'Full credit!';
    var color = '#6eb535';
    var bg = '#a1d775';
  } else {
    var text = 'Mastered!';
    var color = '#6eb535';
    var bg = '#a1d775';
  }

  $('.schoolyourself-review-mastery-text').html(text);
  $('.schoolyourself-review-mastery-bar-filler').css('right', right);
  $('.schoolyourself-review-mastery-bar-filler').css('background', color);
  $('.schoolyourself-review-mastery-bar').css('background', bg);
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
