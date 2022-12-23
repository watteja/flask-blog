$(document).ready(function () {
  $("#publicCbox").tooltip({
    // add this to avoid rendering problems (according to docs)
    container: "body",
    title: "Public topics can be read by anyone, member or not",
    placement: "left",
  });
});
