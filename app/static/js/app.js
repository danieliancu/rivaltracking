/* Alpine registrations and htmx glue for the RivalTracking shell.
   Kept deliberately small: HTMX owns data fetching, Alpine owns purely
   client-side state (menus, overlays, timers). */

document.addEventListener("alpine:init", () => {
  // Mobile offcanvas sidebar.
  Alpine.store("ui", {
    sidebarOpen: false,
  });

  // Generic dropdown menu (row actions, avatar, run-scan picker).
  Alpine.data("menu", () => ({
    open: false,
    toggle() {
      this.open = !this.open;
    },
    close() {
      this.open = false;
    },
  }));

  // Dropdown that must escape a clipping/scrolling ancestor (e.g. a table's
  // overflow-x-auto). The menu markup is teleported to <body> and positioned
  // fixed, anchored to the trigger's right edge — so it is never clipped.
  Alpine.data("anchoredMenu", () => ({
    open: false,
    top: 0,
    left: 0,
    toggle() {
      this.open ? this.close() : this.show();
    },
    show() {
      const r = this.$refs.trigger.getBoundingClientRect();
      this.top = r.bottom + 4;
      this.left = r.right;
      this.open = true;
    },
    close() {
      this.open = false;
    },
    get menuStyle() {
      return (
        "position:fixed;top:" +
        this.top +
        "px;left:" +
        this.left +
        "px;transform:translateX(-100%);z-index:60;"
      );
    },
  }));

  // Drawer/dialog fragment lifecycle: animates in on load, removes itself
  // from #drawer-root / #modal-root on close.
  Alpine.data("overlay", () => ({
    open: false,
    init() {
      this.$nextTick(() => (this.open = true));
    },
    close() {
      this.open = false;
      setTimeout(() => this.$root.remove(), 250);
    },
  }));

  // Header search palette: visibility only; results come from HTMX.
  Alpine.data("searchPalette", () => ({
    q: "",
    open: false,
    close() {
      this.open = false;
      this.q = "";
    },
  }));

  // Staged progress checklist used by add-competitor / discovery / report
  // dialogs: advances one stage per `interval` ms, then reveals the done
  // phase (the server already performed the mutation when this renders).
  Alpine.data("stagedProgress", (stageCount, interval, doneEvent) => ({
    stage: 0,
    done: false,
    timer: null,
    init() {
      this.timer = setInterval(() => {
        this.stage += 1;
        if (this.stage >= stageCount) {
          clearInterval(this.timer);
          this.done = true;
          if (doneEvent) htmx.trigger(document.body, doneEvent);
        }
      }, interval);
    },
    destroy() {
      if (this.timer) clearInterval(this.timer);
    },
  }));
});

/* Close any open drawer/dialog content after a successful boosted nav. */
document.addEventListener("htmx:afterSwap", (event) => {
  if (event.detail.target.id === "drawer-root" || event.detail.target.id === "modal-root") {
    // Focus the first focusable element inside newly-opened overlays.
    const focusable = event.detail.target.querySelector(
      "input, select, textarea, button, [tabindex]"
    );
    if (focusable) focusable.focus({ preventScroll: true });
  }
});
