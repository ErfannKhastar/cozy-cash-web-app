document.addEventListener('DOMContentLoaded', () => {
    
    // === Smooth scrolling for anchor links ===
    // This allows clicking "Features" or "Learn More" to scroll down smoothly
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            
            // If href is just "#", do nothing
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    console.log("CozyCash Landing Page Loaded successfully.");
});