const categoryTitleLinks = document.querySelectorAll(".categoryTitleLink");

categoryTitleLinks.forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();

    const title = link.getAttribute("data-title");

    document.getElementById("categoryTitle").value = title;
  });
});
