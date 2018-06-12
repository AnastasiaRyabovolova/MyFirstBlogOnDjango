$(function () {
  var loadCities = function () {
    var url = $("#userSignupForm").attr("data-cities-url");  // get the url of the `load_cities` view
    var countryId = $(this).val();
    $.ajax({                       // initialize an AJAX request
      url: url,                    // set the url of the request (= localhost:8000/hr/ajax/load-cities/)
      data: {
        'country': countryId       // add the country id to the GET parameters
      },
      success: function (data) {   // `data` is the return of the `load_cities` view function
        $("#id_city").html(data);  // replace the contents of the city input with the data that came from the server
      }
    });
  };

  $(document).on('change', "#id_country", loadCities);
  $("#id_country").on('change', loadCities);
});
