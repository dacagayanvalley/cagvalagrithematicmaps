const PlansDashboard = (() => {
  const VERSION = "20260518-versioned-plans";
  const DETAIL_URL = `data/plans_projects_2025_2027_details.csv?v=${VERSION}`;
  const METADATA_URL = `data/plans_projects_metadata.json?v=${VERSION}`;
  const VERSION_MANIFEST_URL = `data/plans_versions/manifest.json?v=${VERSION}`;

  const COMMODITIES = [
    { key: "all", label: "All" },
    { key: "rice", label: "Rice", programs: ["Rice Program"] },
    { key: "corn", label: "Corn", programs: ["Corn Program"] },
    { key: "hvc", label: "High Value Crops", programs: ["High Value Crops"] },
    { key: "oap", label: "OAP", programs: ["OAP"] },
    { key: "nupap", label: "NUPAP", programs: ["NUPAP"] },
    { key: "livestock", label: "Livestock", programs: ["LIVESTOCK"] },
    { key: "fmr", label: "FMR", programs: ["Farm-to-Market Roads"] },
    { key: "prdp", label: "PRDP", programs: ["PRDP"] },
    { key: "4ks", label: "4Ks", programs: ["4Ks"] },
    { key: "saad", label: "SAAD", programs: ["SAAD"] },
    { key: "mcra", label: "MCRA", programs: ["MCRA"] },
    { key: "nshp", label: "NSHP", programs: ["National Soil Health"] },
    { key: "halal", label: "HALAL", programs: ["HALAL"] },
    { key: "other", label: "Other", programs: ["COLD STORAGE", "2024-2026", "Research and Development (R4)", "F2C2"] }
  ];

  const YEAR_LABELS = {
    "2025": "2025 accomplishment",
    "2026": "2026 ongoing",
    "2027": "2027 proposal"
  };

  let rows = [];
  let activeYear = "2027";
  let activeCommodity = "all";
  let hvcCommodityFilter = "all";
  let provinceFilter = "all";
  let districtFilter = "all";
  let municipalityFilter = "all";
  let chartType = "horizontal-bar";
  let themeMode = "dark";
  let searchTerm = "";
  let activitySearchTerm = "";
  let tableSortField = "budget";
  let tableSortDir = "desc";
  let metadata = null;
  let dataVersions = [];
  let activeDataVersionId = "latest";
  let compareRowsCache = new Map();
  let charts = {};

  const currency = new Intl.NumberFormat("en-PH", { maximumFractionDigits: 0 });
  const decimal = new Intl.NumberFormat("en-PH", { maximumFractionDigits: 2 });

  function init() {
    document.body.dataset.theme = themeMode;
    bindEvents();
    buildCommodityTabs();
    loadVersionManifest().finally(loadDataset);
  }

  function loadDataset() {
    const version = activeDataVersion();
    rows = [];
    loadMetadata(version.metadata_url);
    Papa.parse(version.detail_url, {
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: result => {
        rows = result.data.map(normalizeRow).filter(row => !isSummaryOnlyRow(row));
        buildProvinceFilter();
        buildHvcCommodityFilter();
        updateGeographyFilters();
        update();
      },
      error: err => {
        document.getElementById("planning-notes").innerHTML =
          `<div class="note danger">Planning data could not be loaded: ${escapeHTML(err.message || err)}</div>`;
      }
    });
  }

  async function loadVersionManifest() {
    try {
      const res = await fetch(VERSION_MANIFEST_URL, { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const manifest = await res.json();
      dataVersions = Array.isArray(manifest.versions) ? manifest.versions : [];
      activeDataVersionId = manifest.latest_version_id || dataVersions[0]?.id || "latest";
    } catch (err) {
      dataVersions = [];
      activeDataVersionId = "latest";
    }
    buildVersionFilter();
  }

  function activeDataVersion() {
    const version = dataVersions.find(item => item.id === activeDataVersionId);
    return {
      id: version?.id || "latest",
      detail_url: version?.detail_url ? cacheBusted(version.detail_url) : DETAIL_URL,
      metadata_url: version?.metadata_url ? cacheBusted(version.metadata_url) : METADATA_URL,
      generated_at: version?.generated_at || "",
    };
  }

  function cacheBusted(url) {
    return `${url}${url.includes("?") ? "&" : "?"}v=${encodeURIComponent(VERSION)}`;
  }

  function buildVersionFilter() {
    const select = document.getElementById("version-filter");
    if (!select) return;

    if (!dataVersions.length) {
      select.innerHTML = `<option value="latest">Latest dataset</option>`;
      select.value = "latest";
      select.disabled = true;
      buildCompareControls();
      return;
    }

    select.disabled = false;
    select.innerHTML = dataVersions.map(version => {
      return `<option value="${escapeHTML(version.id)}">${escapeHTML(versionOptionLabel(version))}</option>`;
    }).join("");
    select.value = activeDataVersionId;
    buildCompareControls();
  }

  function versionOptionLabel(version) {
    const generated = formatTimestamp(version.generated_at);
    const sourceTime = formatTimestamp(version.latest_source_file_modified_at);
    const records = formatNumber(version.detail_rows || 0);
    return `${generated} - ${records} records - source ${sourceTime}`;
  }

  function buildCompareControls() {
    const fromSelect = document.getElementById("compare-from");
    const toSelect = document.getElementById("compare-to");
    const button = document.getElementById("compare-versions");
    const output = document.getElementById("version-compare");
    if (!fromSelect || !toSelect || !button || !output) return;

    if (dataVersions.length < 2) {
      fromSelect.innerHTML = `<option value="">Need two versions</option>`;
      toSelect.innerHTML = `<option value="">Need two versions</option>`;
      fromSelect.disabled = true;
      toSelect.disabled = true;
      button.disabled = true;
      output.innerHTML = `<div class="source-line">Archive another refresh to compare timelines.</div>`;
      return;
    }

    const options = dataVersions.map(version =>
      `<option value="${escapeHTML(version.id)}">${escapeHTML(versionOptionLabel(version))}</option>`
    ).join("");
    fromSelect.innerHTML = options;
    toSelect.innerHTML = options;
    fromSelect.disabled = false;
    toSelect.disabled = false;
    button.disabled = false;
    fromSelect.value = dataVersions[1]?.id || dataVersions[0].id;
    toSelect.value = dataVersions[0].id;
  }

  async function loadMetadata(url = METADATA_URL) {
    try {
      const res = await fetch(url, { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      metadata = await res.json();
      renderMetadata();
    } catch (err) {
      document.getElementById("source-summary").innerHTML =
        `<div class="source-line source-warn">Source metadata unavailable.</div>`;
    }
  }

  function renderMetadata() {
    if (!metadata) return;
    const generated = formatTimestamp(metadata.generated_at);
    const latest = formatTimestamp(metadata.latest_source_file_modified_at);
    const version = dataVersions.find(item => item.id === activeDataVersionId);
    const link = metadata.source_folder_url
      ? `<a href="${escapeHTML(metadata.source_folder_url)}" target="_blank" rel="noopener">Google Drive folder</a>`
      : "Google Drive folder";

    document.getElementById("source-summary").innerHTML = `
      <div class="source-line"><strong>${escapeHTML(metadata.source || "Planning workbooks")}</strong></div>
      ${version ? `<div class="source-line">Selected timeline: ${escapeHTML(formatTimestamp(version.generated_at))}</div>` : ""}
      <div class="source-line">Dashboard data refreshed: ${escapeHTML(generated)}</div>
      <div class="source-line">Latest downloaded workbook timestamp: ${escapeHTML(latest)}</div>
      <div class="source-line">${formatNumber(metadata.source_file_count || 0)} workbooks, ${formatNumber(metadata.detail_rows || 0)} records</div>
      <div class="source-line">${link}</div>
    `;
  }

  function normalizeRow(row) {
    const districtInfo = normalizeDistrict(row.province, row.district);
    const displayMunicipality = row.municipality ||
      (districtInfo.key ? `${districtInfo.label} districtwide` : `${row.province} provincewide`);
    return {
      ...row,
      year: String(row.year || "").trim(),
      districtKey: districtInfo.key,
      displayDistrict: districtInfo.label,
      displayMunicipality,
      budgetValue: parseNumber(row.budget),
      lengthValue: parseNumber(row.length_km),
      physicalValue: parseNumber(row.physical_target),
      commodityLabel: row.commodity || row.program || "",
      officeFunction: row.office_function || row.tier_2 || "",
      tier1: row.tier_1 || "",
      tier2: row.tier_2 || row.office_function || "",
      searchText: [
        row.province, row.municipality, row.program, row.activity,
        row.commodity, row.office_function, row.tier_1, row.tier_2,
        row.district, row.unit, row.source_note, row.source_file, row.sheet
      ].join(" ").toLowerCase()
    };
  }

  function isSummaryOnlyRow(row) {
    const allocation = String(row.allocation_method || "").toLowerCase();
    const activity = String(row.activity || "").toLowerCase();
    const program = String(row.program || "").trim().toUpperCase();
    const sourceNote = String(row.source_note || "").toLowerCase();
    const municipality = String(row.municipality || "").trim();

    if (allocation === "district/province sheet total") return true;
    if (!municipality && activity.includes("district/province total")) return true;
    if (!municipality && sourceNote.includes("district/province commodity total")) return true;
    return !municipality && ["GRAND TOTAL", "2025-2027"].includes(program);
  }

  function parseNumber(value) {
    const n = parseFloat(String(value || "").replace(/,/g, ""));
    return Number.isFinite(n) ? n : 0;
  }

  function bindEvents() {
    document.getElementById("year-tabs").addEventListener("click", event => {
      const btn = event.target.closest("button[data-year]");
      if (!btn) return;
      activeYear = btn.dataset.year;
      setActiveButton("#year-tabs button", btn);
      update();
    });

    document.getElementById("province-filter").addEventListener("change", event => {
      provinceFilter = event.target.value;
      districtFilter = "all";
      municipalityFilter = "all";
      updateGeographyFilters();
      update();
    });

    document.getElementById("district-filter").addEventListener("change", event => {
      districtFilter = event.target.value;
      municipalityFilter = "all";
      updateMunicipalityFilter();
      update();
    });

    document.getElementById("municipality-filter").addEventListener("change", event => {
      municipalityFilter = event.target.value;
      update();
    });

    document.getElementById("hvc-commodity-filter").addEventListener("change", event => {
      hvcCommodityFilter = event.target.value;
      update();
    });

    document.getElementById("search-filter").addEventListener("input", event => {
      searchTerm = event.target.value.trim().toLowerCase();
      update();
    });

    document.getElementById("activity-search").addEventListener("input", event => {
      activitySearchTerm = event.target.value.trim().toLowerCase();
      updateTable(filteredRows());
    });

    document.querySelector("thead").addEventListener("click", event => {
      const button = event.target.closest("[data-sort]");
      if (!button) return;
      const field = button.dataset.sort;
      if (tableSortField === field) {
        tableSortDir = tableSortDir === "asc" ? "desc" : "asc";
      } else {
        tableSortField = field;
        tableSortDir = ["budget", "length", "year"].includes(field) ? "desc" : "asc";
      }
      updateTable(filteredRows());
    });

    document.getElementById("chart-type").addEventListener("change", event => {
      chartType = event.target.value;
      update();
    });

    const versionFilter = document.getElementById("version-filter");
    if (versionFilter) {
      versionFilter.addEventListener("change", event => {
        activeDataVersionId = event.target.value;
        provinceFilter = "all";
        districtFilter = "all";
        municipalityFilter = "all";
        hvcCommodityFilter = "all";
        searchTerm = "";
        activitySearchTerm = "";
        document.getElementById("search-filter").value = "";
        document.getElementById("activity-search").value = "";
        document.getElementById("hvc-commodity-filter").value = "all";
        loadDataset();
      });
    }

    const compareButton = document.getElementById("compare-versions");
    if (compareButton) {
      compareButton.addEventListener("click", compareSelectedVersions);
    }

    document.querySelectorAll("[data-theme-mode]").forEach(button => {
      button.addEventListener("click", event => {
        themeMode = event.currentTarget.dataset.themeMode || "dark";
        document.querySelectorAll("[data-theme-mode]").forEach(btn => {
          btn.classList.toggle("active", btn === event.currentTarget);
        });
        document.body.dataset.theme = themeMode;
        update();
      });
    });

    const activeThemeButton = document.querySelector(`[data-theme-mode="${themeMode}"]`);
    if (activeThemeButton) {
      document.querySelectorAll("[data-theme-mode]").forEach(btn => {
        btn.classList.toggle("active", btn === activeThemeButton);
      });
      document.body.dataset.theme = themeMode;
    }

    document.getElementById("export-plans").addEventListener("click", () => {
      const csv = toCSV(filteredRows());
      const hvcSuffix = activeCommodity === "hvc" && hvcCommodityFilter !== "all"
        ? `_${slugify(hvcCommodityFilter)}`
        : "";
      downloadCSV(csv, `agriplan_${activeCommodity}${hvcSuffix}_${activeYear}.csv`);
    });
  }

  function buildProvinceFilter() {
    const select = document.getElementById("province-filter");
    const provinces = [...new Set(rows.map(row => row.province).filter(Boolean))].sort();
    select.innerHTML = `<option value="all">All Provinces</option>` +
      provinces.map(province => `<option value="${escapeHTML(province)}">${escapeHTML(province)}</option>`).join("");
  }

  function updateGeographyFilters() {
    updateDistrictFilter();
    updateMunicipalityFilter();
  }

  function updateDistrictFilter() {
    const select = document.getElementById("district-filter");
    const districtMap = new Map();
    rows
      .filter(row => provinceFilter === "all" || row.province === provinceFilter)
      .forEach(row => {
        if (!row.districtKey) return;
        districtMap.set(row.districtKey, row.displayDistrict);
      });
    const districts = [...districtMap.entries()]
      .map(([key, label]) => ({ key, label }))
      .sort((a, b) => compareDistricts(a.key, b.key));

    if (districtFilter !== "all" && !districtMap.has(districtFilter)) districtFilter = "all";
    select.innerHTML = `<option value="all">All Districts</option>` +
      districts.map(district =>
        `<option value="${escapeHTML(district.key)}" ${district.key === districtFilter ? "selected" : ""}>${escapeHTML(district.label)}</option>`
      ).join("");
    select.value = districtFilter;
  }

  function updateMunicipalityFilter() {
    const select = document.getElementById("municipality-filter");
    const municipalities = [...new Set(rows
      .filter(row => provinceFilter === "all" || row.province === provinceFilter)
      .filter(row => districtFilter === "all" || row.districtKey === districtFilter)
      .filter(row => row.municipality)
      .map(row => row.municipality))]
      .sort((a, b) => a.localeCompare(b));

    if (municipalityFilter !== "all" && !municipalities.includes(municipalityFilter)) municipalityFilter = "all";
    select.innerHTML = `<option value="all">All Municipalities</option>` +
      municipalities.map(municipality =>
        `<option value="${escapeHTML(municipality)}" ${municipality === municipalityFilter ? "selected" : ""}>${escapeHTML(municipality)}</option>`
      ).join("");
    select.value = municipalityFilter;
  }

  function buildHvcCommodityFilter() {
    const section = document.getElementById("hvc-commodity-section");
    const select = document.getElementById("hvc-commodity-filter");
    if (!section || !select) return;

    const commodities = [...new Set(rows
      .filter(row => row.program === "High Value Crops")
      .map(row => row.commodityLabel)
      .filter(Boolean))]
      .sort((a, b) => a.localeCompare(b));

    if (hvcCommodityFilter !== "all" && !commodities.includes(hvcCommodityFilter)) {
      hvcCommodityFilter = "all";
    }

    select.innerHTML = `<option value="all">All HVCDP Commodities</option>` +
      commodities.map(commodity =>
        `<option value="${escapeHTML(commodity)}" ${commodity === hvcCommodityFilter ? "selected" : ""}>${escapeHTML(commodity)}</option>`
      ).join("");
    select.value = hvcCommodityFilter;
    section.classList.toggle("filter-section-muted", activeCommodity !== "hvc");
    select.disabled = activeCommodity !== "hvc";
  }

  function compareDistricts(a, b) {
    const av = districtOrder(a.split("|").pop());
    const bv = districtOrder(b.split("|").pop());
    return av === bv ? a.localeCompare(b) : av - bv;
  }

  function normalizeDistrict(province, district) {
    const raw = String(district || "").trim();
    if (!raw) return { key: "", label: "" };

    const normalizedRaw = raw.toUpperCase().replace(/DISTRICT/g, "").trim();
    let code = "";
    if (normalizedRaw.includes("LONE")) {
      code = "LONE";
    } else {
      const roman = normalizedRaw.match(/\b(I|II|III|IV|V|VI)\b/);
      const number = normalizedRaw.match(/\d+/);
      if (number) code = number[0];
      if (roman) code = { I: "1", II: "2", III: "3", IV: "4", V: "5", VI: "6" }[roman[1]];
    }
    if (!code) code = normalizedRaw.replace(/\s+/g, "");

    const provinceName = province || "Unspecified";
    const key = `${provinceName}|${code}`;
    const label = code === "LONE" ? `${provinceName} - Lone District` : `${provinceName} - District ${code}`;
    return { key, label };
  }

  function districtOrder(value) {
    const text = String(value || "").toUpperCase();
    if (text.includes("LONE")) return 0;
    const roman = text.match(/\b(I|II|III|IV|V|VI)\b/);
    if (roman) return { I: 1, II: 2, III: 3, IV: 4, V: 5, VI: 6 }[roman[1]];
    const number = text.match(/\d+/);
    return number ? Number(number[0]) : 99;
  }

  function formatDistrict(value) {
    const text = String(value || "").trim();
    if (!text) return "Unspecified";
    if (/^lone$/i.test(text) || /^lone district$/i.test(text)) return "Lone District";
    if (/district/i.test(text)) return text;
    return `District ${text}`;
  }

  function districtLabel(row) {
    return row.displayDistrict || `${row.province || "Unspecified"} - Unspecified District`;
  }

  function buildCommodityTabs() {
    const tabs = document.getElementById("commodity-tabs");
    tabs.innerHTML = COMMODITIES.map(item =>
      `<button data-commodity="${item.key}" class="${item.key === activeCommodity ? "active" : ""}">${item.label}</button>`
    ).join("");

    tabs.addEventListener("click", event => {
      const btn = event.target.closest("button[data-commodity]");
      if (!btn) return;
      activeCommodity = btn.dataset.commodity;
      if (activeCommodity !== "hvc") hvcCommodityFilter = "all";
      setActiveButton("#commodity-tabs button", btn);
      buildHvcCommodityFilter();
      update();
    });
  }

  function setActiveButton(selector, activeButton) {
    document.querySelectorAll(selector).forEach(btn => btn.classList.toggle("active", btn === activeButton));
  }

  function filteredRows(options = {}) {
    const year = options.year || activeYear;
    const commodity = options.commodity || activeCommodity;
    const commodityDef = COMMODITIES.find(item => item.key === commodity);
    const programs = commodityDef?.programs || null;

    return rows.filter(row => {
      if (year !== "all" && row.year !== year) return false;
      if (provinceFilter !== "all" && row.province !== provinceFilter) return false;
      if (districtFilter !== "all" && row.districtKey !== districtFilter) return false;
      if (municipalityFilter !== "all" && row.municipality !== municipalityFilter) return false;
      if (programs && !programs.includes(row.program)) return false;
      if (commodity === "hvc" && hvcCommodityFilter !== "all" && row.commodityLabel !== hvcCommodityFilter) return false;
      if (searchTerm && !row.searchText.includes(searchTerm)) return false;
      return true;
    });
  }

  function update() {
    const data = filteredRows();
    updateKpis(data);
    updateLens(data);
    updateCharts(data);
    updateNotes(data);
    updateTable(data);
  }

  function updateKpis(data) {
    const municipalities = new Set(data.filter(row => row.municipality).map(row => `${row.province}|${row.municipality}`));
    setText("kpi-items", formatNumber(data.length));
    setText("kpi-budget", formatNumber(sum(data, "budgetValue")));
    setText("kpi-municipalities", formatNumber(municipalities.size));
    setText("kpi-length", formatDecimal(sum(data, "lengthValue")));
  }

  function updateLens(data) {
    const commodity = COMMODITIES.find(item => item.key === activeCommodity)?.label || "All";
    const hvcCommodity = activeCommodity === "hvc" && hvcCommodityFilter !== "all" ? hvcCommodityFilter : "";
    const budget = sum(data, "budgetValue");
    const provinceText = provinceFilter === "all" ? "all provinces" : provinceFilter;
    const districtText = districtFilter === "all" ? "all districts" : (rows.find(row => row.districtKey === districtFilter)?.displayDistrict || districtFilter);
    const municipalityText = municipalityFilter === "all" ? "all municipalities" : municipalityFilter;
    document.getElementById("lens-summary").innerHTML = `
      <div><strong>${escapeHTML(commodity)}</strong>${escapeHTML(YEAR_LABELS[activeYear] || activeYear)}</div>
      ${hvcCommodity ? `<div>HVCDP commodity: ${escapeHTML(hvcCommodity)}</div>` : ""}
      <div>${formatNumber(data.length)} records across ${escapeHTML(provinceText)}, ${escapeHTML(districtText)}, ${escapeHTML(municipalityText)}</div>
      <div>${formatNumber(budget)} PHP '000 total tagged budget</div>
    `;
  }

  function updateCharts(data) {
    renderCategoryChart("province-chart", groupBudget(data, "province").slice(0, 8), "Budget", "#1a6b3c");
    renderCategoryChart("district-chart", groupBudget(data, "district").slice(0, 12), "Budget", "#b45309");
    renderCategoryChart("municipality-chart", groupBudget(data, "municipality").slice(0, 10), "Budget", "#2e7d9a");
    renderCategoryChart("commodity-chart", groupBudget(data, "commodity").slice(0, 10), "Budget", "#2563eb");
    renderCategoryChart("tier1-chart", groupBudget(data, "tier1").slice(0, 8), "Budget", "#7c3aed");
    renderCategoryChart("tier2-chart", groupBudget(data, "tier2").slice(0, 8), "Budget", "#0f766e");
    renderYearChart();
  }

  function groupBudget(data, field) {
    const map = new Map();
    data.forEach(row => {
      const key = field === "municipality"
        ? row.displayMunicipality
        : field === "district"
          ? districtLabel(row)
          : field === "commodity"
            ? (row.commodityLabel || row.program || "Unspecified Commodity")
          : field === "tier1"
            ? (row.tier1 || "Unspecified Tier 1")
            : field === "tier2"
              ? (row.tier2 || "Unspecified Tier 2")
          : (row[field] || "Unspecified");
      map.set(key, (map.get(key) || 0) + row.budgetValue);
    });
    return [...map.entries()]
      .map(([label, value]) => ({ label, value }))
      .sort((a, b) => b.value - a.value);
  }

  function renderCategoryChart(id, data, label, color) {
    const ctx = document.getElementById(id);
    if (charts[id]) charts[id].destroy();
    const theme = chartTheme();
    const isDoughnut = chartType === "doughnut";
    const isLine = chartType === "line";
    const horizontal = chartType === "horizontal-bar";
    const chartColors = data.map((_, index) => palette(index, color));

    charts[id] = new Chart(ctx, {
      type: isDoughnut ? "doughnut" : isLine ? "line" : "bar",
      data: {
        labels: data.map(item => item.label),
        datasets: [{
          label,
          data: data.map(item => item.value),
          backgroundColor: isDoughnut ? chartColors : color,
          borderColor: isDoughnut ? theme.surface : color,
          fill: isLine,
          tension: 0.25
        }]
      },
      options: {
        indexAxis: !isDoughnut && !isLine && horizontal ? "y" : "x",
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: isDoughnut, labels: { color: theme.text } },
          tooltip: { callbacks: { label: item => `${label}: ${formatNumber(item.raw)} PHP '000` } }
        },
        scales: isDoughnut ? {} : categoryScales(horizontal, theme)
      }
    });
  }

  function renderYearChart() {
    const commodity = activeCommodity;
    const yearData = ["2025", "2026", "2027"].map(year => {
      const data = filteredRows({ year, commodity });
      return {
        year,
        count: data.length,
        budget: sum(data, "budgetValue")
      };
    });

    const id = "year-chart";
    const ctx = document.getElementById(id);
    if (charts[id]) charts[id].destroy();
    const theme = chartTheme();

    charts[id] = new Chart(ctx, {
      type: "line",
      data: {
        labels: yearData.map(item => item.year),
        datasets: [
          {
            label: "Budget PHP '000",
            data: yearData.map(item => item.budget),
            borderColor: "#4ade80",
            backgroundColor: "rgba(74,222,128,0.12)",
            fill: true,
            tension: 0.25,
            yAxisID: "y"
          },
          {
            label: "Items",
            data: yearData.map(item => item.count),
            borderColor: "#fbbf24",
            backgroundColor: "#fbbf24",
            tension: 0.25,
            yAxisID: "y1"
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: { legend: { position: "bottom", labels: { color: theme.text } } },
        scales: timelineScales(theme)
      }
    });
  }

  function updateNotes(data) {
    const budget = sum(data, "budgetValue");
    const municipalities = new Set(data.filter(row => row.municipality).map(row => `${row.province}|${row.municipality}`));
    const topProgram = groupBudget(data, "program")[0];
    const zeroBudget = data.filter(row => row.budgetValue <= 0).length;
    const notes = [];

    if (!data.length) {
      notes.push(["danger", "No records match the current commodity, year, province, and search filters."]);
    } else {
      notes.push(["", `${formatNumber(data.length)} records are tagged to ${municipalities.size} municipality/province combinations for this lens.`]);
      if (topProgram) notes.push(["", `${topProgram.label} carries the largest tagged budget at ${formatNumber(topProgram.value)} PHP '000.`]);
      const topTier2 = groupBudget(data, "tier2")[0];
      if (activeYear === "2027" && topTier2) notes.push(["", `${topTier2.label} is the largest Tier 2/function grouping at ${formatNumber(topTier2.value)} PHP '000.`]);
      const topDistrict = groupBudget(data, "district")[0];
      if (topDistrict) notes.push(["", `${topDistrict.label} is the top district grouping for this lens at ${formatNumber(topDistrict.value)} PHP '000.`]);
      if (activeYear === "2027") notes.push(["warn", "Use this view to compare proposed allocations with the need-gap layer in the decision map before realignment."]);
      if (zeroBudget > 0) notes.push(["warn", `${zeroBudget} records have no extracted budget value; verify the source workbook before treating them as unfunded.`]);
      if (budget <= 0) notes.push(["danger", "The current filter has no extracted budget. This may be a real gap or a workbook encoding issue."]);
    }

    document.getElementById("planning-notes").innerHTML = notes
      .map(([level, text]) => `<div class="note ${level}">${escapeHTML(text)}</div>`)
      .join("");
  }

  function updateTable(data) {
    const tbody = document.getElementById("plans-table");
    const tableRows = filterActivityRows(data);
    const sorted = sortTableRows(tableRows);
    document.getElementById("table-count").textContent = activitySearchTerm
      ? `${formatNumber(sorted.length)} matching records of ${formatNumber(data.length)}`
      : `${formatNumber(sorted.length)} records`;
    updateSortIndicators();

    tbody.innerHTML = sorted.slice(0, 500).map(row => `
      <tr>
        <td>${escapeHTML(row.province)}</td>
        <td>${escapeHTML(row.displayDistrict || formatDistrict(row.district))}</td>
        <td>${escapeHTML(row.displayMunicipality)}</td>
        <td>${escapeHTML(row.year)}</td>
        <td>${escapeHTML(row.program)}${row.commodityLabel && row.commodityLabel !== row.program ? `<div class="muted">${escapeHTML(row.commodityLabel)}</div>` : ""}</td>
        <td>${escapeHTML(row.tier1 || "")}<div class="muted">${escapeHTML(row.tier2 || "")}</div></td>
        <td class="activity-cell">${escapeHTML(row.activity || row.source_note || "")}<div class="muted">${escapeHTML(row.unit || "")}</div></td>
        <td>${formatNumber(row.budgetValue)}</td>
        <td>${row.lengthValue ? formatDecimal(row.lengthValue) + " km" : ""}</td>
        <td>${escapeHTML(row.source_file)}</td>
      </tr>
    `).join("");
  }

  async function compareSelectedVersions() {
    const fromId = document.getElementById("compare-from")?.value;
    const toId = document.getElementById("compare-to")?.value;
    const output = document.getElementById("version-compare");
    if (!output) return;

    if (!fromId || !toId || dataVersions.length < 2) {
      output.innerHTML = `<div class="source-line source-warn">At least two archived versions are needed.</div>`;
      return;
    }
    if (fromId === toId) {
      output.innerHTML = `<div class="source-line source-warn">Choose two different versions to compare.</div>`;
      return;
    }

    output.innerHTML = `<div class="source-line">Comparing archived datasets...</div>`;
    try {
      const [fromRows, toRows] = await Promise.all([
        loadCompareRows(fromId),
        loadCompareRows(toId)
      ]);
      renderVersionComparison(fromId, toId, compareRows(fromRows, toRows));
    } catch (err) {
      output.innerHTML = `<div class="source-line source-warn">Comparison failed: ${escapeHTML(err.message || err)}</div>`;
    }
  }

  function loadCompareRows(versionId) {
    if (compareRowsCache.has(versionId)) return Promise.resolve(compareRowsCache.get(versionId));
    const version = dataVersions.find(item => item.id === versionId);
    if (!version?.detail_url) return Promise.reject(new Error("Version detail CSV is unavailable."));

    return new Promise((resolve, reject) => {
      Papa.parse(cacheBusted(version.detail_url), {
        download: true,
        header: true,
        skipEmptyLines: true,
        complete: result => {
          const normalized = result.data.map(normalizeRow).filter(row => !isSummaryOnlyRow(row));
          compareRowsCache.set(versionId, normalized);
          resolve(normalized);
        },
        error: reject
      });
    });
  }

  function compareRows(fromRows, toRows) {
    const fromMap = aggregateCompareRows(fromRows);
    const toMap = aggregateCompareRows(toRows);
    const added = [];
    const deleted = [];
    const changed = [];
    let fromBudget = 0;
    let toBudget = 0;

    fromMap.forEach(item => { fromBudget += item.budget; });
    toMap.forEach(item => { toBudget += item.budget; });

    toMap.forEach((toItem, key) => {
      const fromItem = fromMap.get(key);
      if (!fromItem) {
        added.push(toItem);
        return;
      }

      const delta = {
        row: toItem.row,
        fromBudget: fromItem.budget,
        toBudget: toItem.budget,
        budgetDelta: toItem.budget - fromItem.budget,
        physicalDelta: toItem.physical - fromItem.physical,
        lengthDelta: toItem.length - fromItem.length,
        countDelta: toItem.count - fromItem.count,
      };
      if (
        Math.abs(delta.budgetDelta) >= 0.01 ||
        Math.abs(delta.physicalDelta) >= 0.01 ||
        Math.abs(delta.lengthDelta) >= 0.01 ||
        delta.countDelta !== 0
      ) {
        changed.push(delta);
      }
    });

    fromMap.forEach((fromItem, key) => {
      if (!toMap.has(key)) deleted.push(fromItem);
    });

    changed.sort((a, b) => Math.abs(b.budgetDelta) - Math.abs(a.budgetDelta));
    added.sort((a, b) => b.budget - a.budget);
    deleted.sort((a, b) => b.budget - a.budget);

    return {
      added,
      deleted,
      changed,
      fromCount: fromRows.length,
      toCount: toRows.length,
      fromBudget,
      toBudget,
      budgetDelta: toBudget - fromBudget,
    };
  }

  function aggregateCompareRows(data) {
    const map = new Map();
    data.forEach(row => {
      const key = compareKey(row);
      const item = map.get(key) || {
        row,
        count: 0,
        budget: 0,
        physical: 0,
        length: 0,
      };
      item.count += 1;
      item.budget += row.budgetValue || 0;
      item.physical += row.physicalValue || 0;
      item.length += row.lengthValue || 0;
      map.set(key, item);
    });
    return map;
  }

  function compareKey(row) {
    return [
      row.source_file,
      row.sheet,
      row.province,
      row.district,
      row.municipality,
      row.year,
      row.program,
      row.commodityLabel,
      row.tier1,
      row.tier2,
      row.activity,
      row.unit,
      row.allocation_method
    ].map(value => String(value || "").trim().toLowerCase()).join("|");
  }

  function renderVersionComparison(fromId, toId, comparison) {
    const output = document.getElementById("version-compare");
    const fromVersion = dataVersions.find(item => item.id === fromId);
    const toVersion = dataVersions.find(item => item.id === toId);
    const changedItems = comparison.changed.slice(0, 5).map(item =>
      compareItemHTML(item.row, item.budgetDelta, `${formatSigned(item.budgetDelta)} PHP '000`)
    ).join("");
    const addedItems = comparison.added.slice(0, 3).map(item =>
      compareItemHTML(item.row, item.budget, `+${formatNumber(item.budget)} PHP '000`)
    ).join("");
    const deletedItems = comparison.deleted.slice(0, 3).map(item =>
      compareItemHTML(item.row, -item.budget, `-${formatNumber(item.budget)} PHP '000`)
    ).join("");

    output.innerHTML = `
      <div class="source-line"><strong>${escapeHTML(formatTimestamp(fromVersion?.generated_at))} to ${escapeHTML(formatTimestamp(toVersion?.generated_at))}</strong></div>
      <div class="compare-metrics">
        ${compareMetricHTML("Added", comparison.added.length)}
        ${compareMetricHTML("Deleted", comparison.deleted.length)}
        ${compareMetricHTML("Changed", comparison.changed.length)}
        ${compareMetricHTML("Budget delta", formatSigned(comparison.budgetDelta))}
      </div>
      <div class="source-line">Records: ${formatNumber(comparison.fromCount)} to ${formatNumber(comparison.toCount)}</div>
      <div class="source-line">Budget: ${formatNumber(comparison.fromBudget)} to ${formatNumber(comparison.toBudget)} PHP '000</div>
      ${changedItems ? `<div class="compare-list"><div class="source-line"><strong>Largest Changes</strong></div>${changedItems}</div>` : ""}
      ${addedItems ? `<div class="compare-list"><div class="source-line"><strong>Added</strong></div>${addedItems}</div>` : ""}
      ${deletedItems ? `<div class="compare-list"><div class="source-line"><strong>Deleted</strong></div>${deletedItems}</div>` : ""}
      ${!changedItems && !addedItems && !deletedItems ? `<div class="source-line">No record-level changes detected.</div>` : ""}
    `;
  }

  function compareMetricHTML(label, value) {
    return `
      <div class="compare-metric">
        <span>${escapeHTML(label)}</span>
        <strong>${escapeHTML(value)}</strong>
      </div>
    `;
  }

  function compareItemHTML(row, delta, deltaText) {
    const deltaClass = delta >= 0 ? "compare-delta-pos" : "compare-delta-neg";
    return `
      <div class="compare-item">
        <strong>${escapeHTML(row.municipality || row.displayMunicipality)}, ${escapeHTML(row.province)}</strong>
        <div>${escapeHTML(row.year)} - ${escapeHTML(row.program)}</div>
        <div>${escapeHTML(row.activity || row.source_note || "")}</div>
        <div class="${deltaClass}">${escapeHTML(deltaText)}</div>
      </div>
    `;
  }

  function formatSigned(value) {
    const sign = value > 0 ? "+" : "";
    return `${sign}${formatNumber(value)}`;
  }

  function filterActivityRows(data) {
    if (!activitySearchTerm) return data;
    return data.filter(row => [
      row.activity,
      row.source_note,
      row.unit,
      row.program,
      row.commodityLabel,
      row.tier1,
      row.tier2,
      row.displayMunicipality,
      row.displayDistrict
    ].join(" ").toLowerCase().includes(activitySearchTerm));
  }

  function sortTableRows(data) {
    const dir = tableSortDir === "asc" ? 1 : -1;
    return [...data].sort((a, b) => {
      const av = sortValue(a, tableSortField);
      const bv = sortValue(b, tableSortField);

      if (typeof av === "number" && typeof bv === "number") {
        return (av - bv) * dir || a.province.localeCompare(b.province);
      }
      return String(av).localeCompare(String(bv), undefined, { numeric: true, sensitivity: "base" }) * dir;
    });
  }

  function sortValue(row, field) {
    const values = {
      province: row.province,
      district: row.displayDistrict,
      municipality: row.displayMunicipality,
      year: parseNumber(row.year),
      program: row.program,
      function: row.tier2 || row.officeFunction,
      activity: row.activity || row.source_note || "",
      budget: row.budgetValue,
      length: row.lengthValue,
      source: row.source_file
    };
    return values[field] ?? "";
  }

  function updateSortIndicators() {
    document.querySelectorAll("[data-sort]").forEach(button => {
      const active = button.dataset.sort === tableSortField;
      button.classList.toggle("active", active);
      button.dataset.dir = active ? tableSortDir : "";
      button.setAttribute("aria-sort", active ? (tableSortDir === "asc" ? "ascending" : "descending") : "none");
    });
  }

  function sum(data, field) {
    return data.reduce((total, row) => total + (row[field] || 0), 0);
  }

  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  function formatNumber(value) {
    return currency.format(value || 0);
  }

  function formatDecimal(value) {
    return decimal.format(value || 0);
  }

  function formatCompact(value) {
    return Intl.NumberFormat("en-PH", { notation: "compact", maximumFractionDigits: 1 }).format(value || 0);
  }

  function chartTheme() {
    return themeMode === "dark"
      ? { text: "#d8e4dc", grid: "rgba(216,228,220,0.14)", surface: "#18251d" }
      : { text: "#1e2a1f", grid: "rgba(30,42,31,0.12)", surface: "#ffffff" };
  }

  function categoryScales(horizontal, theme) {
    if (horizontal) {
      return {
        x: {
          beginAtZero: true,
          grid: { color: theme.grid },
          ticks: { color: theme.text, callback: value => formatCompact(value) }
        },
        y: {
          grid: { color: "transparent" },
          ticks: { color: theme.text, autoSkip: false }
        }
      };
    }
    return {
      x: {
        grid: { color: "transparent" },
        ticks: { color: theme.text }
      },
      y: {
        beginAtZero: true,
        grid: { color: theme.grid },
        ticks: { color: theme.text, callback: value => formatCompact(value) }
      }
    };
  }

  function timelineScales(theme) {
    return {
      x: { grid: { color: theme.grid }, ticks: { color: theme.text } },
      y: {
        beginAtZero: true,
        grid: { color: theme.grid },
        ticks: { color: theme.text, callback: value => formatCompact(value) }
      },
      y1: {
        beginAtZero: true,
        position: "right",
        grid: { drawOnChartArea: false },
        ticks: { color: theme.text }
      }
    };
  }

  function palette(index, fallback) {
    const colors = ["#1a6b3c", "#2e7d9a", "#b45309", "#7c3aed", "#b91c1c", "#047857", "#2563eb", "#9333ea", "#c2410c", "#0f766e"];
    return colors[index % colors.length] || fallback;
  }

  function formatTimestamp(value) {
    if (!value) return "Not available";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleString("en-PH", {
      year: "numeric",
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    });
  }

  function slugify(value) {
    return String(value || "")
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "") || "selection";
  }

  function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, ch => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;"
    }[ch]));
  }

  function toCSV(data) {
    if (!data.length) return "";
    const fields = ["province", "district", "municipality", "year", "program", "commodity", "tier_1", "tier_2", "activity", "unit", "physical_target", "budget", "length_km", "source_file", "sheet", "allocation_method"];
    const quote = value => `"${String(value ?? "").replace(/"/g, '""')}"`;
    return [fields.join(",")]
      .concat(data.map(row => fields.map(field => quote(row[field])).join(",")))
      .join("\n");
  }

  function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  return { init };
})();

document.addEventListener("DOMContentLoaded", PlansDashboard.init);
