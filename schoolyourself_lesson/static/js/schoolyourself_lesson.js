function SchoolYourselfLessonXBlock(runtime, element) {
  var viewport = schoolyourself.PlayerViewportBuilder.insert(1024, 768);
  $(function ($) {
    $('button', element).click(function(eventObject) {
      viewport.openFrame(this.getAttribute('data-url'));
    });
  });
}
