const currentType = document.body.dataset.currentType;

const sections = document.querySelectorAll("section[id^='scroll']");
const navLinks = document.querySelectorAll(".nav-link");

// 滾動更改 class:active
window.addEventListener("scroll", () => {

  // 只有 index 頁面才根據滾動改變 active
  if (currentType !== "index") {
    return;
  }

  let current = "";

  sections.forEach(section => {
    const top = section.offsetTop - 120;

    if (window.scrollY >= top) {
      current = section.id;
    }
  });

  navLinks.forEach(link => {
    link.classList.remove("active");

    if (link.getAttribute("href") === "#" + current) {
      link.classList.add("active");
    }
  });
});


// 點擊更改 class:active
navLinks.forEach(link => {
  link.addEventListener("click", function () {

    navLinks.forEach(item => item.classList.remove("active"));

    this.classList.add("active");
  });
});