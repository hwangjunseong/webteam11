const categoryTitleLinks = document.querySelectorAll(".categoryTitleLink");

categoryTitleLinks.forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();

    const title = link.getAttribute("data-title");

    document.getElementById("categoryTitle").value = title;
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const radioButtons = document.querySelectorAll('input[name="btnradio"]');
  const rows = document.querySelectorAll(".category-row");

  function filterRows() {
    const selectedCategory = document.querySelector(
      'input[name="btnradio"]:checked'
    ).value;
    rows.forEach((row) => {
      if (row.dataset.category === selectedCategory) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    });
  }

  radioButtons.forEach((radio) => {
    radio.addEventListener("change", filterRows);
  });

  filterRows(); // 초기 호출로 기본 선택된 라디오 버튼에 따라 행 필터링
});
