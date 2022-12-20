function togglePreviewBtn(btn) {
    btn.classList.toggle("bi-eye-slash");
    btn.classList.toggle("bi-eye");

    btn.innerHTML = (btn.innerHTML == "&nbsp;Hide preview" ? "&nbsp;Preview" : "&nbsp;Hide preview");
}

function toggleMdGuideBtn(btn) {
    btn.classList.toggle("active");
}