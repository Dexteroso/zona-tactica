document.addEventListener("DOMContentLoaded", () => {
    const menuButton = document.querySelector(".menu-toggle");
    const navigation = document.getElementById("primary-navigation");

    if (!menuButton || !navigation) {
        return;
    }

    const closeMenu = () => {
        menuButton.setAttribute("aria-expanded", "false");
        menuButton.setAttribute("aria-label", "Abrir menú de navegación");
        navigation.classList.remove("is-open");
    };

    menuButton.addEventListener("click", () => {
        const isOpen = menuButton.getAttribute("aria-expanded") === "true";
        menuButton.setAttribute("aria-expanded", String(!isOpen));
        menuButton.setAttribute(
            "aria-label",
            isOpen ? "Abrir menú de navegación" : "Cerrar menú de navegación"
        );
        navigation.classList.toggle("is-open", !isOpen);
    });

    navigation.addEventListener("click", (event) => {
        if (event.target.closest("a")) {
            closeMenu();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && navigation.classList.contains("is-open")) {
            closeMenu();
            menuButton.focus();
        }
    });

    document.addEventListener("click", (event) => {
        if (
            navigation.classList.contains("is-open") &&
            !navigation.contains(event.target) &&
            !menuButton.contains(event.target)
        ) {
            closeMenu();
        }
    });

    window.addEventListener("resize", () => {
        if (window.innerWidth >= 768) {
            closeMenu();
        }
    });
});
