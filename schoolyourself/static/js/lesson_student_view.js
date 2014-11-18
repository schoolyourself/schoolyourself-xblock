function SchoolYourselfLessonStudentView(runtime, element) {
  var viewport = schoolyourself.PlayerViewportBuilder.insert(1024, 768);
  $(function ($) {
    $('.schoolyourself-lesson-player', element).click(function(eventObject) {
      viewport.openFrame(this.getAttribute('data-url'));
    });
  });
}
