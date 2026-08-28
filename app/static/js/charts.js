/* Chart.js bootstrapping for canvas[data-chart] mounts.
   Each mount has a sibling <script type="application/json" id="<chart-id>">
   payload produced by the {% chart %} tag. Colors are token NAMES
   ("chart-1", "success", ...) resolved from the CSS custom properties so
   charts always match the design system. Re-inits after HTMX swaps. */
(function () {
  const instances = new WeakMap();

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue("--" + name).trim();
  }

  // oklch(l c h) → oklch(l c h / a%) — canvas has no color-mix support.
  function withAlpha(color, alphaPct) {
    if (color.endsWith(")")) return color.slice(0, -1) + " / " + alphaPct + "%)";
    return color;
  }

  function baseDefaults() {
    Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
    Chart.defaults.font.size = 10;
    Chart.defaults.color = cssVar("muted-foreground");
    Chart.defaults.animation = false;
    Chart.defaults.plugins.legend.display = false;
  }

  const tooltipStyle = () => ({
    backgroundColor: cssVar("background"),
    borderColor: cssVar("border"),
    borderWidth: 1,
    titleColor: cssVar("foreground"),
    bodyColor: cssVar("foreground"),
    titleFont: { weight: "600", size: 11 },
    bodyFont: { size: 11 },
    padding: 8,
    cornerRadius: 8,
    boxWidth: 8,
    boxHeight: 8,
    boxPadding: 4,
    usePointStyle: true,
  });

  // Donut center total (replaces Recharts' absolutely-positioned label).
  const centerText = {
    id: "centerText",
    afterDraw(chart) {
      const opts = chart.$rivalOptions || {};
      if (!opts.centerTotal) return;
      const { ctx } = chart;
      const area = chart.chartArea;
      const x = (area.left + area.right) / 2;
      const y = (area.top + area.bottom) / 2;
      ctx.save();
      ctx.textAlign = "center";
      ctx.font = "700 21px " + Chart.defaults.font.family;
      ctx.fillStyle = cssVar("foreground");
      ctx.fillText(opts.centerTotal, x, y - 2);
      ctx.font = "500 10px " + Chart.defaults.font.family;
      ctx.fillStyle = cssVar("muted-foreground");
      ctx.fillText(opts.centerLabel || "Total", x, y + 14);
      ctx.restore();
    },
  };

  function build(canvas) {
    const id = canvas.getAttribute("data-chart");
    const script = document.getElementById(id);
    if (!script || typeof Chart === "undefined") return;
    const payload = JSON.parse(script.textContent);
    const o = payload.options || {};
    const pct = (v) => v + "%";

    baseDefaults();
    let config;

    if (payload.type === "line") {
      config = {
        type: "line",
        data: {
          labels: payload.labels,
          datasets: payload.series.map((s) => ({
            label: s.label,
            data: s.data,
            borderColor: cssVar(s.color),
            backgroundColor: cssVar(s.color),
            borderWidth: 2.5,
            borderDash: s.dashed ? [6, 4] : [],
            pointRadius: 0,
            pointHoverRadius: 3,
            tension: 0.4, // Recharts type="monotone"
          })),
        },
        options: {
          maintainAspectRatio: false,
          interaction: { mode: "index", intersect: false },
          plugins: { tooltip: tooltipStyle(), datalabels: { display: false } },
          scales: {
            x: { grid: { display: false }, border: { display: false }, ticks: { padding: 6 } },
            y: {
              min: o.yMin,
              max: o.yMax,
              grid: { color: withAlpha(cssVar("border"), 50), tickBorderDash: [3, 3] },
              border: { display: false, dash: [3, 3] },
              ticks: Object.assign(
                { padding: 6 },
                o.yTicks ? { callback: (v) => (o.yTicks.includes(v) ? (o.percent ? pct(v) : v) : null), autoSkip: false, stepSize: o.yStep } : {},
                !o.yTicks && o.percent ? { callback: pct } : {}
              ),
            },
          },
        },
      };
    } else if (payload.type === "hbar" || payload.type === "bar") {
      const horizontal = payload.type === "hbar";
      const s = payload.series[0];
      config = {
        type: "bar",
        data: {
          labels: payload.labels,
          datasets: [
            {
              data: s.data,
              backgroundColor: s.colors ? s.colors.map(cssVar) : cssVar(s.color),
              barThickness: o.barSize || 18,
              borderRadius: horizontal
                ? { topLeft: 0, topRight: 5, bottomRight: 5, bottomLeft: 0 }
                : { topLeft: 5, topRight: 5, bottomRight: 0, bottomLeft: 0 },
              borderSkipped: false,
            },
          ],
        },
        options: {
          indexAxis: horizontal ? "y" : "x",
          maintainAspectRatio: false,
          layout: horizontal ? { padding: { right: 34 } } : {},
          plugins: {
            tooltip: tooltipStyle(),
            datalabels: o.labels
              ? {
                  anchor: "end",
                  align: horizontal ? "end" : "end",
                  offset: 2,
                  color: cssVar("muted-foreground"),
                  font: { size: 10, weight: "600" },
                  formatter: (v) => (o.percent ? pct(v) : v),
                }
              : { display: false },
          },
          scales: horizontal
            ? {
                x: { display: false, max: o.xMax },
                y: {
                  grid: { display: false },
                  border: { display: false },
                  ticks: { color: cssVar("muted-foreground"), font: { size: 10 }, padding: 4 },
                  afterFit: (scale) => { if (o.labelWidth) scale.width = o.labelWidth; },
                },
              }
            : {
                x: { grid: { display: false }, border: { display: false } },
                y: { grid: { color: withAlpha(cssVar("border"), 50) }, border: { display: false } },
              },
        },
      };
    } else if (payload.type === "donut") {
      const s = payload.series[0];
      config = {
        type: "doughnut",
        data: {
          labels: payload.labels,
          datasets: [
            {
              data: s.data,
              backgroundColor: s.colors.map(cssVar),
              borderWidth: 0,
              spacing: 3,
            },
          ],
        },
        options: {
          maintainAspectRatio: false,
          cutout: "70%",
          radius: "95%",
          plugins: { tooltip: tooltipStyle(), datalabels: { display: false } },
        },
      };
    }

    if (!config) return;
    config.plugins = [centerText];
    if (typeof ChartDataLabels !== "undefined") config.plugins.push(ChartDataLabels);
    const instance = new Chart(canvas, config);
    instance.$rivalOptions = o;
    instances.set(canvas, instance);
  }

  function boot(root) {
    (root || document).querySelectorAll("canvas[data-chart]").forEach((canvas) => {
      if (!instances.has(canvas)) build(canvas);
    });
  }

  document.addEventListener("DOMContentLoaded", () => boot(document));

  document.addEventListener("htmx:beforeSwap", (event) => {
    event.detail.target.querySelectorAll("canvas[data-chart]").forEach((canvas) => {
      const instance = instances.get(canvas);
      if (instance) {
        instance.destroy();
        instances.delete(canvas);
      }
    });
  });

  document.addEventListener("htmx:afterSwap", (event) => boot(event.detail.target));
})();
