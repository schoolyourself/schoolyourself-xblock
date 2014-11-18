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
  });
}
