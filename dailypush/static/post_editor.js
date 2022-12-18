function togglePreviewBtn(btn) {
    btn.classList.toggle("bi-eye-slash");
    btn.classList.toggle("bi-eye");

    btn.innerHTML = (btn.innerHTML == " Hide preview" ? " Preview" : " Hide preview");
}

function toggleMdGuideBtn(btn) {
    btn.classList.toggle("active");
}