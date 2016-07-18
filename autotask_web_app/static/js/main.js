$(document).on('submit', 'form.search-account', function(form) {
  var $form = $(form);
  $.ajax({
    type: form.method,
    url: form.action,
    data:{
      account-name:$('#account-name').val(),
      csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()
    },
    success: function(data) {
      alert("Test");
    }
  });
});
