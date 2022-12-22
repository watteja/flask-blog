function toggleShowMore(btn) {
    btn.classList.toggle("bi-plus");
    btn.classList.toggle("bi-dash");

    btn.innerHTML = (btn.innerHTML == "&nbsp;Show more" ? "&nbsp;Show less" : "&nbsp;Show more");
}
