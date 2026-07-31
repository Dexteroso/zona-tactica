document.addEventListener("DOMContentLoaded", () => {
    const csrfToken = document.querySelector(
        "#view-counter-config input[name='csrfmiddlewaretoken']"
    )?.value;

    if (!csrfToken) {
        return;
    }

    document.querySelectorAll("video[data-view-url]").forEach((video) => {
        let vistaRegistrada = false;

        video.addEventListener("play", async () => {
            if (vistaRegistrada) {
                return;
            }

            vistaRegistrada = true;

            try {
                const response = await fetch(video.dataset.viewUrl, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    credentials: "same-origin",
                });

                if (!response.ok) {
                    throw new Error("No se pudo registrar la vista.");
                }

                const data = await response.json();
                const target = document.getElementById(video.dataset.viewTarget);

                if (target) {
                    target.textContent = `${data.vistas} ${
                        data.vistas === 1 ? "reproducción" : "reproducciones"
                    }`;
                }
            } catch (error) {
                vistaRegistrada = false;
            }
        });
    });

    document.querySelectorAll(".share-button").forEach((button) => {
        button.addEventListener("click", async () => {
            const url = new URL(button.dataset.shareUrl, window.location.origin).href;
            const shareData = { url };

            try {
                if (navigator.share) {
                    await navigator.share(shareData);
                } else {
                    await navigator.clipboard.writeText(url);
                    button.setAttribute("aria-label", "Enlace copiado");
                }
            } catch (error) {
                if (error.name !== "AbortError") {
                    button.setAttribute("aria-label", "No se pudo compartir");
                }
            }
        });
    });
});
