document.addEventListener("DOMContentLoaded", () => {

  // Check if fullscreenbackground already exists; ensure it's attached to <html> (not the filtered body)
  const existingBg = document.querySelector(".fullscreenbackground");
  if (existingBg) {
    if (existingBg.parentElement !== document.documentElement) {
      document.documentElement.appendChild(existingBg);
    }
  } else {
    const bg = document.createElement("div");
    bg.className = "fullscreenbackground";
    document.documentElement.appendChild(bg);
  }

  // Parse boolean-like query parameter values with default=true
  function parseBooleanParam(value, defaultValue = true) {
    if (value === null || value === undefined) return defaultValue;
    const v = String(value).trim().toLowerCase();
    if (v === "") return defaultValue;
    if (["1", "true", "yes", "on", "y", "t"].includes(v)) return true;
    if (["0", "false", "no", "off", "n", "f"].includes(v)) return false;
    return defaultValue;
  }

  // Extract hash id and optional query string present inside the hash (malformed URLs like #id?grasple-fullscreen=true)
  function getHashParts() {
    const raw = window.location.hash || "";
    const hash = raw.startsWith("#") ? raw.slice(1) : raw;
    if (!hash) return { id: "", hashQuery: "" };
    const qIndex = hash.indexOf("?");
    const id = qIndex >= 0 ? hash.slice(0, qIndex) : hash;
    const hashQuery = qIndex >= 0 ? hash.slice(qIndex + 1) : "";
    return { id: decodeURIComponent(id), hashQuery };
  }

  // Build a unified URLSearchParams from normal search and any params found inside the hash
  function getUnifiedParams() {
    const normal = new URLSearchParams(window.location.search || "");
    const { hashQuery } = getHashParts();
    if (!hashQuery) return normal;
    const inHash = new URLSearchParams(hashQuery);
    // Merge: params in hash override normal ones
    inHash.forEach((val, key) => normal.set(key, val));
    return normal;
  }

  // Scroll to the element referenced by the hash id (supports malformed hashes with query after id)
  function scrollToHashId() {
    const { id } = getHashParts();
    if (!id) return;
    const el = document.getElementById(id);
    if (!el) return;
    // Use native anchor jump if possible, else ensure scroll
    try {
      el.scrollIntoView({ behavior: "auto", block: "start" });
      // Assist focus for accessibility
      if (typeof el.focus === "function") el.focus({ preventScroll: true });
    } catch (_) {
      // Fallback
      el.scrollIntoView();
    }
  }

  // Scroll helper for arbitrary elements
  function scrollToElement(el) {
    if (!el) return;
    try {
      el.scrollIntoView({ behavior: "auto", block: "start" });
      if (typeof el.focus === "function") el.focus({ preventScroll: true });
    } catch (_) {
      el.scrollIntoView();
    }
  }

  // Ensure background reflects global fullscreen state across all admonitions
  function syncFullscreenBackground() {
    const bg = document.querySelector(".fullscreenbackground");
    const anyFullscreen = document.querySelector(".admonition.grasple.fullscreenable.fullscreen");
    if (!bg) return;
    if (anyFullscreen) {
      bg.classList.add("active");
    } else {
      bg.classList.remove("active");
    }
  }

  function updateFullscreenButtons() {

    document.querySelectorAll(".admonition.grasple.fullscreenable").forEach(admonition => {
      const header = admonition.querySelector("p.admonition-title");
      if (!header) return;

      // Remove existing button(s)
      header.querySelectorAll(".fullscreen-btn").forEach(btn => btn.remove());
      
      // Reusable helpers to toggle fullscreen state
      const enterFullscreen = (admon) => {
        const bg = document.querySelector(".fullscreenbackground");
        const details = admon.querySelector("section details");
        const headerBtn = admon.querySelector("p.admonition-title .fullscreen-btn");
        if (admon.classList.contains("fullscreen")) return;
        admon.classList.add("fullscreen");
        if (headerBtn) headerBtn.innerHTML = '<i class="fas fa-minimize"></i>';
        if (details && !details.hasAttribute("open")) details.setAttribute("open", "");
        if (details) {
          requestAnimationFrame(() => {
            const detailsRect = admon.getBoundingClientRect();
            const summary = details.querySelector("summary");
            const summaryRect = summary ? summary.getBoundingClientRect() : { bottom: 0 };
            const remainder = detailsRect.height - summaryRect.bottom;
            const grasple = details.querySelector(".grasplecontainer");
            if (grasple) grasple.style.height = `calc(${remainder}px + 1.5rem)`;
          });
        }
        if (bg) bg.classList.add("active");
      };

      const exitFullscreen = (admon) => {
        const bg = document.querySelector(".fullscreenbackground");
        const details = admon.querySelector("section details");
        const headerBtn = admon.querySelector("p.admonition-title .fullscreen-btn");
        if (!admon.classList.contains("fullscreen")) return;
        admon.classList.remove("fullscreen");
        const grasple = details ? details.querySelector(".grasplecontainer") : null;
        if (grasple) grasple.style.height = `400px`;
        if (headerBtn) headerBtn.innerHTML = '<i class="fas fa-maximize"></i>';
        if (bg) bg.classList.remove("active");
      };

      // Always add button
      const btn = document.createElement("button");
      btn.className = "fullscreen-btn";
      btn.innerHTML = '<i class="fas fa-maximize"></i>';

      // Toggle via button (no URL mutation)
      btn.onclick = function () {
        if (admonition.classList.contains("fullscreen")) {
          exitFullscreen(admonition);
        } else {
          document.querySelectorAll(".admonition.grasple.fullscreenable.fullscreen").forEach(other => {
            if (other !== admonition) exitFullscreen(other);
          });
          enterFullscreen(admonition);
          scrollToElement(admonition); // ensure scroll when entering fullscreen
        }
        scrollToHashId();
        syncFullscreenBackground();
      };

      // Style the button into the title bar
      header.style.position = "relative";
      btn.style.position = "absolute";
      btn.style.right = "0.5em";
      btn.style.top = "0.2em";
      header.appendChild(btn);

      // Apply URL-driven fullscreen if requested and this admonition matches the hash
      const applyFullscreenFromURL = () => {
        const params = getUnifiedParams();
        const hasParam = params.has("grasple-fullscreen");
        const { id: hashId } = getHashParts();

        // If malformed/absent: no param or no hash => exit all
        if (!hasParam || !hashId) {
          if (admonition.classList.contains("fullscreen")) exitFullscreen(admonition);
          // After each instance updates, sync background
          syncFullscreenBackground();
          return;
        }

        const shouldFullscreen = parseBooleanParam(params.get("grasple-fullscreen"), true);

        // Resolve target admonition from hash id
        const target = document.getElementById(hashId);
        const targetAdmon = target
          ? (target.matches(".admonition.grasple.fullscreenable")
              ? target
              : target.closest(".admonition.grasple.fullscreenable"))
          : null;

        // If this instance is the target, apply according to param; otherwise ensure it's not fullscreen
        if (targetAdmon && targetAdmon === admonition) {
          if (shouldFullscreen) {
            enterFullscreen(admonition);
            scrollToElement(admonition); // ensure scroll when entering via URL
          } else {
            exitFullscreen(admonition);
          }
        } else {
          if (admonition.classList.contains("fullscreen")) exitFullscreen(admonition);
        }

        // After per-admonition adjustments, make background match global state
        syncFullscreenBackground();
      };

      // Initial URL check
      applyFullscreenFromURL();
      scrollToHashId();

      // Re-apply on navigation changes
      window.addEventListener("hashchange", () => {
        applyFullscreenFromURL();
        scrollToHashId();
      });
      window.addEventListener("popstate", () => {
        applyFullscreenFromURL();
        scrollToHashId();
      });
    });
  }

  // Initial setup
  updateFullscreenButtons();

});