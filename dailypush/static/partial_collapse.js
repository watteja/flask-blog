function toggleShowMore(btn) {
  btn.classList.toggle("bi-plus");
  btn.classList.toggle("bi-dash");
  btn.classList.toggle("mt-3");

  btn.innerHTML =
    btn.innerHTML == "&nbsp;Show more" ? "&nbsp;Show less" : "&nbsp;Show more";
}

function makeExpandable(post) {
  /**
   * Makes long blog entries expandable on a button click.
   */
  post_body = post.querySelector(".card-body");
  font_size = parseFloat(getComputedStyle(post_body)["font-size"]);
  height = post_body.offsetHeight / font_size;

  // if the entry is too long
  if (height > 25) {
    // make the surrounding div collapsible
    post_body.parentNode.classList.add("collapse");
    // make expand bar visible
    post.querySelector(".expand-bar").hidden = false;
  }
}

document.querySelectorAll(".post").forEach(makeExpandable);
