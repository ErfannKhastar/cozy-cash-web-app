/**
 * @file landing.js
 * @description Handles interactions on the Landing Page, specifically smooth scrolling
 * for navigation anchor links.
 */
document.addEventListener("DOMContentLoaded", () => {
  /**
   * Smooth scrolling for anchor links.
   * Intercepts clicks on links starting with "#" to scroll smoothly to the target section.
   */
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const targetId = this.getAttribute("href");

      // If href is just "#", do nothing
      if (targetId === "#") return;

      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: "smooth",
        });
      }
    });
  });

  console.log("CozyCash Landing Page Loaded successfully.");
});
