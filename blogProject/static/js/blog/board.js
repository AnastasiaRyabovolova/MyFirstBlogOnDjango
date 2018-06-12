$(function () {

var loadForm = function () {
  var edt = $(this);
  $.ajax({
    url: edt.attr("data-url"),
    type: 'get',
    dataType: 'json',
    beforeSend: function () {
      $("#modal-board").modal("show");
    },
    success: function (data) {
      $("#modal-board .modal-content").html(data.html_form);
    }
  });
  return false
};
var saveForm = function () {
  var form = $(this);
  $.ajax({
    url: form.attr("action"),
    data: form.serialize(),
    type: form.attr("method"),
    dataType: 'json',
    success: function (data) {
      if (data.form_is_valid) {
        $("#board-table").html(data.html_board_list);  // <-- Replace the table body
        $("#modal-board").modal("hide");
        updateHistory();  // <-- Close the modal
      }
      else {
        $("#modal-board .modal-content").html(data.html_form);
      }
    }
  });
  return false
};

var updateHistory = function() {
  $.ajax({
    url: '/get_history/',
    type: 'get',
    dataType: 'json',
    success: function (data) {
      $(".history-table").html(data.history_html);
    }
  });
}

$(document).on('click', ".js-get-create-form", loadForm);
$("#modal-board").on('submit', ".js-create-board", saveForm);

$(document).on("click", ".js-edit-board-form", loadForm);
$("#modal-board").on("submit", ".js-edit-board", saveForm);

$(document).on("click", ".js-delete-board-form", loadForm);
$("#modal-board").on("submit", ".js-delete-board", saveForm);

});
