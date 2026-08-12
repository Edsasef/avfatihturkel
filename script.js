// Gerekli HTML elementlerini seç
const hamburger = document.querySelector(".hamburger");
const navMenu = document.querySelector(".navbar-menu");

// Hamburger ikonuna tıklandığında olay dinleyicisi çalıştır
hamburger.addEventListener("click", () => {
    // Hem menüye hem de butona 'active' class'ını ekle/çıkar
    hamburger.classList.toggle("active");
    navMenu.classList.toggle("active");
});

// Navigasyon çubuğunu seç
const navbar = document.querySelector(".navbar");

// Sayfa kaydırma (scroll) olayını dinle
window.addEventListener("scroll", () => {
    // Eğer sayfa 50 pikselden fazla aşağı kaydırıldıysa
    if (window.scrollY > 50) {
        navbar.classList.add("scrolled"); // Şeffaf sınıfını ekle
    } else {
        navbar.classList.remove("scrolled"); // En üste çıkıldıysa sınıfı kaldır, eski haline dön
    }
});