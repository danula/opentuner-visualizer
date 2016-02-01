jQuery(function() {
  jQuery(".navbar-expand-toggle").click(function() {
    jQuery(".app-container").toggleClass("expanded");
    return jQuery(".navbar-expand-toggle").toggleClass("fa-rotate-90");
  });
  return jQuery(".navbar-right-expand-toggle").click(function() {
    jQuery(".navbar-right").toggleClass("expanded");
    return jQuery(".navbar-right-expand-toggle").toggleClass("fa-rotate-90");
  });
});

jQuery(function() {
  return jQuery('select').select2();
});

jQuery(function() {
  return jQuery('.toggle-checkbox').bootstrapSwitch({
    size: "small"
  });
});

jQuery(function() {
  return jQuery('.match-height').matchHeight();
});

jQuery(function() {
  return jQuery('.datatable').DataTable({
    "dom": '<"top"fl<"clear">>rt<"bottom"ip<"clear">>'
  });
});

jQuery(function() {
  return jQuery(".side-menu .nav .dropdown").on('show.bs.collapse', function() {
    return jQuery(".side-menu .nav .dropdown .collapse").collapse('hide');
  });
});
