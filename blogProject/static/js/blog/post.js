$(document).on('submit', ".js-create-post-form", function (event) {
    var form = $(this);
    $.ajax({
      url: form.attr('data-url'),
      data: form.serialize(),
      type: form.attr('method'),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          simplemde.value('');
          $("#all_post").html(data.html_new_posts);
        }
        $(".ajax_form").html(data.html_form);
        simplemde = new SimpleMDE();
       },
  });
    return false
 }
);
    var infinite = new Waypoint.Infinite({
      element: $('.infinite-container')[0],
      onBeforePageLoad: function () {
        $('.loading').show();
      },
      onAfterPageLoad: function ($items) {
        $('.loading').hide();
      }
    });
