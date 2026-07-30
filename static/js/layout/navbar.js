const sections = document.querySelectorAll("section[id^='scroll']");
const navLinks = document.querySelectorAll(".nav-link");

// 滾動更改class:active，
window.addEventListener("scroll", () => {
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

// 點擊更改class:active，之後停用
navLinks.forEach(link => {
    link.addEventListener("click", function () {

        // 先移除所有 active
        navLinks.forEach(item => item.classList.remove("active"));

        // 再加到目前點擊的
        this.classList.add("active");
    });
});