function SchoolYourselfStudioView(runtime, element) {
  $('.save-button').bind('click', function() {
    var data = {
      'module_id': $('.module-id', element).val(),
      'module_title': $('.module-title', element).val(),
      'module_description': $('.module-description', element).val(),
      'player_type': $('.player-type', element).val(),
      'shared_key': $('.shared-key', element).val(),
      'base_url': $('.base-url', element).val(),
      'partner_id': $('.partner-id', element).val()
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
