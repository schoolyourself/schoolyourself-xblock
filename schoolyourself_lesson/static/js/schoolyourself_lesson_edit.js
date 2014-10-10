function SchoolYourselfLessonEditor(runtime, element) {
  $('.save-button').bind('click', function() {
    var data = {
      'module_id': $('#module-id').val(),
      'player_type': $('#player-type').val(),
    };

    var handlerUrl = runtime.handlerUrl(element, 'studio_submit');
    $.post(handlerUrl, JSON.stringify(data)).complete(function() {
      window.location.reload(false);
    });
  });

  $('.cancel-button').bind('click', function() {
    runtime.notify('cancel', {});
  });
}
