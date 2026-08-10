// ============================================================
// config.js — Central Configuration for All Indicators,
// Basemaps, Visualization Styles, and Priority Models
// ============================================================

const APP_CONFIG = {
  title: "AgriSight Cagayan Valley",
  subtitle: "Agriculture, climate risk, and seasonal rice decision map",
  defaultView: "municipality",
  defaultIndicator: "elnino_resilience_priority_score",
  defaultStyle: "priority",
  mapCenter: [17.6132, 121.7270],
  mapZoom: 8,
  dataPath: "data/",
  assetVersion: "20260810-rcpc-trends",
};

// ============================================================
// INDICATOR CONFIGURATION
// Add new indicators here — no other code changes needed.
// ============================================================
const INDICATOR_CONFIG = {
  // --- Demographics ---
  population: {
    label: "Population",
    category: "Demographics",
    type: "numeric",
    unit: "persons",
    aggregation: "sum",
    colorScheme: "Blues",
    description: "Total population of the municipality"
  },

  // --- Poverty ---
  poverty_2018: {
    label: "Poverty Incidence 2018",
    category: "Poverty",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "population",
    colorScheme: "Reds",
    description: "Poverty incidence rate in 2018"
  },
  poverty_2021: {
    label: "Poverty Incidence 2021",
    category: "Poverty",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "population",
    colorScheme: "Reds",
    description: "Poverty incidence rate in 2021"
  },
  poverty_2023: {
    label: "Poverty Incidence 2023",
    category: "Poverty",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "population",
    colorScheme: "Reds",
    description: "Poverty incidence rate in 2023"
  },

  // --- Malnutrition ---
  stunting: {
    label: "Stunting Rate",
    category: "Malnutrition",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "population",
    colorScheme: "Oranges",
    description: "Percentage of children with stunting"
  },
  underweight: {
    label: "Underweight Rate",
    category: "Malnutrition",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "population",
    colorScheme: "Oranges",
    description: "Percentage of children who are underweight"
  },
  obese: {
    label: "Obesity Rate",
    category: "Malnutrition",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "population",
    colorScheme: "Purples",
    description: "Percentage of population classified as obese"
  },
  wasting: {
    label: "Wasting Rate",
    category: "Malnutrition",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "population",
    colorScheme: "YlOrRd",
    description: "Percentage of children with wasting"
  },

  // --- Rice ---
  rice_production_2023: {
    label: "Rice Production 2023",
    category: "Rice",
    type: "numeric",
    unit: "MT",
    aggregation: "sum",
    colorScheme: "YlGn",
    description: "Total rice production in metric tons (2023)"
  },
  rice_production_2025: {
    label: "Rice Production 2025",
    category: "Rice",
    type: "numeric",
    unit: "MT",
    aggregation: "sum",
    colorScheme: "YlGn",
    description: "Total rice production in metric tons (2025)"
  },
  rice_area_2023: {
    label: "Rice Area Harvested 2023",
    category: "Rice",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "Rice area harvested in hectares (2023)"
  },
  rice_area_2025: {
    label: "Rice Area Harvested 2025",
    category: "Rice",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "Rice area harvested in hectares (2025)"
  },
  rice_yield_2023: {
    label: "Rice Yield 2023",
    category: "Rice",
    type: "numeric",
    unit: "MT/ha",
    aggregation: "ratio",
    numerator: "rice_production_2023",
    denominator: "rice_area_2023",
    colorScheme: "YlGn",
    description: "Rice yield in MT per hectare (2023)"
  },
  rice_yield_2025: {
    label: "Rice Yield 2025",
    category: "Rice",
    type: "numeric",
    unit: "MT/ha",
    aggregation: "ratio",
    numerator: "rice_production_2025",
    denominator: "rice_area_2025",
    colorScheme: "YlGn",
    description: "Rice yield in MT per hectare (2025)"
  },
  poor_rice_farmers: {
    label: "Rice Farms Below 0.5 ha",
    category: "Rice",
    type: "numeric",
    unit: "farms",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "Number of rice farms below 0.5 hectare from barangay-level farm count data"
  },
  rice_mechanization_level: {
    label: "Rice Mechanization Level",
    category: "Rice",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "rice_area_2023",
    colorScheme: "Blues",
    description: "Percentage of rice farms with mechanization"
  },

  // --- Corn ---
  corn_production_2023: {
    label: "Corn Production 2023",
    category: "Corn",
    type: "numeric",
    unit: "MT",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    description: "Total corn production in metric tons (2023)"
  },
  corn_production_2025: {
    label: "Corn Production 2025",
    category: "Corn",
    type: "numeric",
    unit: "MT",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    description: "Total corn production in metric tons (2025)"
  },
  corn_area_2023: {
    label: "Corn Area Harvested 2023",
    category: "Corn",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    description: "Corn area harvested in hectares (2023)"
  },
  corn_area_2025: {
    label: "Corn Area Harvested 2025",
    category: "Corn",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    description: "Corn area harvested in hectares (2025)"
  },
  corn_yield_2023: {
    label: "Corn Yield 2023",
    category: "Corn",
    type: "numeric",
    unit: "MT/ha",
    aggregation: "ratio",
    numerator: "corn_production_2023",
    denominator: "corn_area_2023",
    colorScheme: "YlOrBr",
    description: "Corn yield in MT per hectare (2023)"
  },
  corn_yield_2025: {
    label: "Corn Yield 2025",
    category: "Corn",
    type: "numeric",
    unit: "MT/ha",
    aggregation: "ratio",
    numerator: "corn_production_2025",
    denominator: "corn_area_2025",
    colorScheme: "YlOrBr",
    description: "Corn yield in MT per hectare (2025)"
  },
  poor_corn_farmers: {
    label: "Corn Farms Below 0.5 ha",
    category: "Corn",
    type: "numeric",
    unit: "farms",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "Number of corn farms below 0.5 hectare from barangay-level farm count data"
  },
  corn_mechanization_level: {
    label: "Corn Mechanization Level",
    category: "Corn",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "corn_area_2023",
    colorScheme: "Blues",
    description: "Percentage of corn farms with mechanization"
  },

  // --- Risk & Constraints ---
  pest_disease_occurrence: {
    label: "Pest & Disease Occurrence",
    category: "Pest and Disease",
    type: "categorical",
    unit: "",
    aggregation: "dominant",
    colorScheme: "Reds",
    categories: { "High": 3, "Moderate": 2, "Low": 1, "None": 0 },
    description: "Level of pest and disease occurrence"
  },
  rcpc_surveillance_priority_score: {
    label: "RCPC Surveillance Priority",
    category: "Pest and Disease",
    type: "numeric",
    unit: "/100",
    aggregation: "weighted_average",
    weightField: "rcpc_incident_records",
    colorScheme: "YlOrRd",
    description: "Municipal crop-protection priority score from RCPC pest and disease records, emphasizing recent affected area, affected farmers, pest diversity, and pressure."
  },
  rcpc_pest_pressure_score: {
    label: "RCPC Pest Pressure Score",
    category: "Pest and Disease",
    type: "numeric",
    unit: "/100",
    aggregation: "weighted_average",
    weightField: "rcpc_incident_records",
    colorScheme: "Reds",
    description: "Composite pest pressure score using affected area, record frequency, infestation, severity, and recent affected area."
  },
  rcpc_response_gap_score: {
    label: "RCPC Response Gap Score",
    category: "Pest and Disease",
    type: "numeric",
    unit: "/100",
    aggregation: "weighted_average",
    weightField: "rcpc_affected_area_ha",
    colorScheme: "OrRd",
    description: "Screening score for untreated area and recent treatment gaps in RCPC crop-protection records."
  },
  rcpc_risk_class: {
    label: "RCPC Risk Class",
    category: "Pest and Disease",
    type: "categorical",
    unit: "",
    aggregation: "dominant",
    colorScheme: "Reds",
    categories: { "Critical": 4, "High": 3, "Moderate": 2, "Watchlist": 1, "Data Insufficient": 0 },
    description: "Highest municipal RCPC screening class from pest pressure, surveillance priority, and response gap scores."
  },
  rcpc_incident_records: {
    label: "RCPC Incident Records",
    category: "Pest and Disease",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "Number of nonblank RCPC pest and disease incidence records for the municipality."
  },
  rcpc_incident_points: {
    label: "RCPC Geocoded Incident Points",
    category: "Pest and Disease",
    type: "numeric",
    unit: "points",
    aggregation: "sum",
    colorScheme: "PuBu",
    description: "Number of RCPC incidence records with valid Region 02 coordinates available for point-layer inspection."
  },
  rcpc_affected_area_ha: {
    label: "RCPC Affected Area",
    category: "Pest and Disease",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "Total crop area affected across RCPC pest and disease records."
  },
  rcpc_recent_affected_area_ha: {
    label: "RCPC Recent Affected Area",
    category: "Pest and Disease",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "YlOrRd",
    description: "Affected area in records from the latest available year and the preceding year for each municipality."
  },
  rcpc_affected_farmers: {
    label: "RCPC Affected Farmers",
    category: "Pest and Disease",
    type: "numeric",
    unit: "farmers",
    aggregation: "sum",
    colorScheme: "Oranges",
    description: "Affected farmers reported in RCPC pest and disease incidence records."
  },
  rcpc_recent_affected_farmers: {
    label: "RCPC Recent Affected Farmers",
    category: "Pest and Disease",
    type: "numeric",
    unit: "farmers",
    aggregation: "sum",
    colorScheme: "Oranges",
    description: "Affected farmers from the latest available year and preceding year for each municipality."
  },
  rcpc_avg_infestation_pct: {
    label: "RCPC Avg Infestation",
    category: "Pest and Disease",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "rcpc_incident_records",
    colorScheme: "YlOrRd",
    description: "Average percent infestation from RCPC records with usable infestation values."
  },
  rcpc_max_infestation_pct: {
    label: "RCPC Max Infestation",
    category: "Pest and Disease",
    type: "percentage",
    unit: "%",
    aggregation: "max",
    colorScheme: "Reds",
    description: "Highest percent infestation observed in RCPC records for the municipality."
  },
  rcpc_avg_severity: {
    label: "RCPC Avg Severity",
    category: "Pest and Disease",
    type: "numeric",
    unit: "",
    aggregation: "weighted_average",
    weightField: "rcpc_incident_records",
    colorScheme: "OrRd",
    description: "Average source severity score where severity values are available."
  },
  rcpc_high_severity_records: {
    label: "RCPC High-Severity Records",
    category: "Pest and Disease",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "Records with high severity or high infestation values, useful for validation and crop-protection triage."
  },
  rcpc_treatment_gap_ha: {
    label: "RCPC Treatment Gap",
    category: "Pest and Disease",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "OrRd",
    description: "Reported untreated affected area, including derived affected-minus-treated gaps where source fields permit."
  },
  rcpc_recent_treatment_gap_ha: {
    label: "RCPC Recent Treatment Gap",
    category: "Pest and Disease",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "OrRd",
    description: "Recent untreated affected area from the latest available year and preceding year."
  },
  rcpc_rice_affected_area_ha: {
    label: "RCPC Rice Affected Area",
    category: "Pest and Disease",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "Affected rice area in RCPC incidence records."
  },
  rcpc_corn_affected_area_ha: {
    label: "RCPC Corn Affected Area",
    category: "Pest and Disease",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    description: "Affected corn area in RCPC incidence records."
  },
  rcpc_hvc_affected_area_ha: {
    label: "RCPC HVC Affected Area",
    category: "Pest and Disease",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Purples",
    description: "Affected high-value crop area in RCPC incidence records."
  },
  rcpc_cassava_affected_area_ha: {
    label: "RCPC Cassava Affected Area",
    category: "Pest and Disease",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Oranges",
    description: "Affected cassava area in RCPC incidence records."
  },
  rcpc_rice_records: {
    label: "RCPC Rice Records",
    category: "Pest and Disease",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "RCPC rice pest and disease record count."
  },
  rcpc_corn_records: {
    label: "RCPC Corn Records",
    category: "Pest and Disease",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    description: "RCPC corn pest and disease record count."
  },
  rcpc_hvc_records: {
    label: "RCPC HVC Records",
    category: "Pest and Disease",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "Purples",
    description: "RCPC high-value crop pest and disease record count."
  },
  rcpc_cassava_records: {
    label: "RCPC Cassava Records",
    category: "Pest and Disease",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "Oranges",
    description: "RCPC cassava pest and disease record count."
  },
  asf_status: {
    label: "ASF Status",
    category: "ASF",
    type: "categorical",
    unit: "",
    aggregation: "dominant",
    colorScheme: "Reds",
    categories: { "Affected": 2, "At-risk": 1, "Clear": 0 },
    description: "African Swine Fever status derived from sanitized laboratory-result aggregates"
  },
  asf_risk_score: {
    label: "ASF Lab Risk Score",
    category: "ASF",
    type: "numeric",
    unit: "/100",
    aggregation: "weighted_average",
    weightField: "asf_sample_total",
    colorScheme: "Reds",
    description: "Composite ASF laboratory risk score from positive results, positivity rate, affected barangay count, and sample volume. Farmer names and farm identifiers are excluded."
  },
  asf_positive_total: {
    label: "ASF Positive Samples",
    category: "ASF",
    type: "numeric",
    unit: "samples",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "Total positive ASF laboratory results in the sanitized aggregate."
  },
  asf_negative_total: {
    label: "ASF Negative Samples",
    category: "ASF",
    type: "numeric",
    unit: "samples",
    aggregation: "sum",
    colorScheme: "Blues",
    description: "Total negative ASF laboratory results in the sanitized aggregate."
  },
  asf_sample_total: {
    label: "ASF Samples Tested",
    category: "ASF",
    type: "numeric",
    unit: "samples",
    aggregation: "sum",
    colorScheme: "Oranges",
    description: "Total ASF laboratory samples recorded after removing personal identifying fields."
  },
  asf_positive_rate_pct: {
    label: "ASF Positivity Rate",
    category: "ASF",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "asf_sample_total",
    colorScheme: "Reds",
    description: "ASF positive sample share from sanitized laboratory aggregates."
  },
  asf_affected_barangays: {
    label: "ASF Affected Barangays",
    category: "ASF",
    type: "numeric",
    unit: "barangays",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "Number of barangays with at least one positive ASF laboratory result."
  },
  asf_tested_barangays: {
    label: "ASF Tested Barangays",
    category: "ASF",
    type: "numeric",
    unit: "barangays",
    aggregation: "sum",
    colorScheme: "Blues",
    description: "Number of barangays represented in ASF laboratory testing records."
  },
  asf_lab_records: {
    label: "ASF Lab Result Records",
    category: "ASF",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "Greys",
    description: "Count of ASF laboratory-result rows summarized after excluding personal identifiers."
  },
  asf_whole_blood_positive: {
    label: "ASF Whole Blood Positives",
    category: "ASF",
    type: "numeric",
    unit: "samples",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "Positive whole-blood ASF laboratory samples."
  },
  asf_organ_positive: {
    label: "ASF Organ Positives",
    category: "ASF",
    type: "numeric",
    unit: "samples",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "Positive organ-sample ASF laboratory results."
  },
  asf_environmental_swab_positive: {
    label: "ASF Environmental Swab Positives",
    category: "ASF",
    type: "numeric",
    unit: "samples",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "Positive environmental-swab ASF laboratory results."
  },
  asf_fecal_swab_positive: {
    label: "ASF Fecal Swab Positives",
    category: "ASF",
    type: "numeric",
    unit: "samples",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "Positive fecal or fecal-swab ASF laboratory results."
  },
  asf_meat_products_positive: {
    label: "ASF Meat Product Positives",
    category: "ASF",
    type: "numeric",
    unit: "samples",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "Positive meat-product or other ASF laboratory results."
  },
  soil_fertility: {
    label: "Soil Fertility",
    category: "Soil Fertility",
    type: "categorical",
    unit: "",
    aggregation: "dominant",
    colorScheme: "Greens",
    categories: { "High": 3, "Moderate": 2, "Low": 1 },
    description: "Soil fertility classification"
  },
  soil_lab_area_ha: {
    label: "Soil-Tested Area",
    category: "Soil Fertility",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "Area covered by public soil fertility analysis records from the Region 02 Power BI report."
  },
  soil_fertility_stress_score: {
    label: "Soil Fertility Stress Score",
    category: "Soil Fertility",
    type: "numeric",
    unit: "/100",
    aggregation: "weighted_average",
    weightField: "soil_lab_area_ha",
    colorScheme: "YlOrRd",
    description: "Composite score combining low fertility, acidic pH, multiple low NPK ratings, zinc deficiency, tested area, and crop-specific soil constraints."
  },
  soil_low_fertility_area_ha: {
    label: "Low Fertility Area",
    category: "Soil Fertility",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "YlOrRd",
    description: "Soil-tested area rated low for overall fertility."
  },
  soil_low_fertility_pct: {
    label: "Low Fertility Share",
    category: "Soil Fertility",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "soil_lab_area_ha",
    colorScheme: "YlOrRd",
    description: "Share of soil-tested area rated low for overall fertility."
  },
  soil_acidic_area_ha: {
    label: "Acidic Soil Area",
    category: "Soil Fertility",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Oranges",
    description: "Soil-tested area classified as acidic."
  },
  soil_acidic_pct: {
    label: "Acidic Soil Share",
    category: "Soil Fertility",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "soil_lab_area_ha",
    colorScheme: "Oranges",
    description: "Share of soil-tested area classified as acidic."
  },
  soil_npk_multiple_low_area_ha: {
    label: "Multiple Low NPK Area",
    category: "Soil Fertility",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "Area where at least two of nitrogen, phosphorus, and potassium are rated low."
  },
  soil_npk_multiple_low_pct: {
    label: "Multiple Low NPK Share",
    category: "Soil Fertility",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "soil_lab_area_ha",
    colorScheme: "Reds",
    description: "Share of soil-tested area where at least two of nitrogen, phosphorus, and potassium are rated low."
  },
  soil_n_low_pct: {
    label: "Low Nitrogen Share",
    category: "Soil Fertility",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "soil_lab_area_ha",
    colorScheme: "YlOrRd",
    description: "Share of soil-tested area rated low in nitrogen."
  },
  soil_p_low_pct: {
    label: "Low Phosphorus Share",
    category: "Soil Fertility",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "soil_lab_area_ha",
    colorScheme: "YlOrRd",
    description: "Share of soil-tested area rated low in phosphorus."
  },
  soil_k_low_pct: {
    label: "Low Potassium Share",
    category: "Soil Fertility",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "soil_lab_area_ha",
    colorScheme: "YlOrRd",
    description: "Share of soil-tested area rated low in potassium."
  },
  soil_zinc_deficient_area_ha: {
    label: "Zinc-Deficient Area",
    category: "Soil Fertility",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Purples",
    description: "Soil-tested area classified as zinc deficient."
  },
  soil_zinc_deficient_pct: {
    label: "Zinc-Deficient Share",
    category: "Soil Fertility",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "soil_lab_area_ha",
    colorScheme: "Purples",
    description: "Share of soil-tested area classified as zinc deficient."
  },
  soil_acidic_low_fertility_area_ha: {
    label: "Acidic + Low Fertility Area",
    category: "Soil Fertility",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "Area where acidic pH and low fertility overlap."
  },
  soil_low_fertility_zinc_def_area_ha: {
    label: "Low Fertility + Zinc Deficient Area",
    category: "Soil Fertility",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "Area where low fertility and zinc deficiency overlap."
  },
  soil_rice_low_fertility_area_ha: {
    label: "Rice Low Fertility Area",
    category: "Soil Fertility",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "YlOrRd",
    description: "Rice soil-tested area rated low for overall fertility."
  },
  soil_rice_tested_area_ha: {
    label: "Rice Soil-Tested Area",
    category: "Soil Fertility",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "Rice area represented in the soil analysis records."
  },
  soil_rice_low_fertility_pct: {
    label: "Rice Low Fertility Share",
    category: "Soil Fertility",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "soil_rice_tested_area_ha",
    colorScheme: "YlOrRd",
    description: "Share of rice soil-tested area rated low for fertility."
  },
  soil_rice_acidic_pct: {
    label: "Rice Acidic Soil Share",
    category: "Soil Fertility",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "soil_rice_tested_area_ha",
    colorScheme: "Oranges",
    description: "Share of rice soil-tested area classified as acidic."
  },
  soil_rice_npk_multiple_low_pct: {
    label: "Rice Multiple Low NPK Share",
    category: "Soil Fertility",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "soil_rice_tested_area_ha",
    colorScheme: "Reds",
    description: "Share of rice soil-tested area where at least two of N, P, and K are low."
  },
  soil_rice_zinc_deficient_pct: {
    label: "Rice Zinc-Deficient Share",
    category: "Soil Fertility",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "soil_rice_tested_area_ha",
    colorScheme: "Purples",
    description: "Share of rice soil-tested area classified as zinc deficient."
  },
  soil_corn_low_fertility_area_ha: {
    label: "Corn Low Fertility Area",
    category: "Soil Fertility",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "YlOrRd",
    description: "Corn soil-tested area rated low for overall fertility."
  },
  soil_corn_tested_area_ha: {
    label: "Corn Soil-Tested Area",
    category: "Soil Fertility",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "Corn area represented in the soil analysis records."
  },
  soil_corn_low_fertility_pct: {
    label: "Corn Low Fertility Share",
    category: "Soil Fertility",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "soil_corn_tested_area_ha",
    colorScheme: "YlOrRd",
    description: "Share of corn soil-tested area rated low for fertility."
  },
  soil_corn_acidic_pct: {
    label: "Corn Acidic Soil Share",
    category: "Soil Fertility",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "soil_corn_tested_area_ha",
    colorScheme: "Oranges",
    description: "Share of corn soil-tested area classified as acidic."
  },
  soil_corn_npk_multiple_low_pct: {
    label: "Corn Multiple Low NPK Share",
    category: "Soil Fertility",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "soil_corn_tested_area_ha",
    colorScheme: "Reds",
    description: "Share of corn soil-tested area where at least two of N, P, and K are low."
  },
  soil_corn_zinc_deficient_pct: {
    label: "Corn Zinc-Deficient Share",
    category: "Soil Fertility",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "soil_corn_tested_area_ha",
    colorScheme: "Purples",
    description: "Share of corn soil-tested area classified as zinc deficient."
  },
  bswm_sample_count: {
    label: "FertMap Soil Samples",
    category: "BSWM FertMap",
    type: "numeric",
    unit: "samples",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "Public DA-BSWM FertMap soil-test sample count summarized to municipality."
  },
  bswm_coordinate_count: {
    label: "FertMap Sample Coordinates",
    category: "BSWM FertMap",
    type: "numeric",
    unit: "points",
    aggregation: "sum",
    colorScheme: "Blues",
    description: "Distinct FertMap coordinate count represented in the municipal sample summary."
  },
  bswm_complete_test_result_count: {
    label: "Complete FertMap Test Results",
    category: "BSWM FertMap",
    type: "numeric",
    unit: "samples",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "FertMap sample rows with pH, organic matter, phosphorus, and potassium classifications available."
  },
  bswm_avg_ph: {
    label: "Average FertMap pH",
    category: "BSWM FertMap",
    type: "numeric",
    unit: "pH",
    aggregation: "weighted_average",
    weightField: "bswm_sample_count",
    colorScheme: "Oranges",
    description: "Average soil pH from public DA-BSWM FertMap samples."
  },
  bswm_acidic_sample_count: {
    label: "Acidic FertMap Samples",
    category: "BSWM FertMap",
    type: "numeric",
    unit: "samples",
    aggregation: "sum",
    colorScheme: "Oranges",
    description: "FertMap samples with pH below 6.5."
  },
  bswm_acidic_sample_pct: {
    label: "Acidic FertMap Sample Share",
    category: "BSWM FertMap",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "bswm_sample_count",
    colorScheme: "Oranges",
    description: "Share of FertMap samples with pH below 6.5."
  },
  bswm_low_om_count: {
    label: "Low OM / N Proxy Samples",
    category: "BSWM FertMap",
    type: "numeric",
    unit: "samples",
    aggregation: "sum",
    colorScheme: "YlOrRd",
    description: "FertMap samples rated low in organic matter, used as the public N-related proxy shown by FertMap."
  },
  bswm_low_om_pct: {
    label: "Low OM / N Proxy Share",
    category: "BSWM FertMap",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "bswm_sample_count",
    colorScheme: "YlOrRd",
    description: "Share of FertMap samples rated low in organic matter, used as the public N-related proxy shown by FertMap."
  },
  bswm_low_p_count: {
    label: "Low Phosphorus Samples",
    category: "BSWM FertMap",
    type: "numeric",
    unit: "samples",
    aggregation: "sum",
    colorScheme: "YlOrRd",
    description: "FertMap samples rated low in phosphorus."
  },
  bswm_low_p_pct: {
    label: "Low Phosphorus Sample Share",
    category: "BSWM FertMap",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "bswm_sample_count",
    colorScheme: "YlOrRd",
    description: "Share of FertMap samples rated low in phosphorus."
  },
  bswm_low_k_count: {
    label: "Low Potassium Samples",
    category: "BSWM FertMap",
    type: "numeric",
    unit: "samples",
    aggregation: "sum",
    colorScheme: "YlOrRd",
    description: "FertMap samples rated low in potassium."
  },
  bswm_low_k_pct: {
    label: "Low Potassium Sample Share",
    category: "BSWM FertMap",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "bswm_sample_count",
    colorScheme: "YlOrRd",
    description: "Share of FertMap samples rated low in potassium."
  },
  bswm_multiple_low_npk_count: {
    label: "Multiple Low FertMap Nutrients",
    category: "BSWM FertMap",
    type: "numeric",
    unit: "samples",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "FertMap samples where at least two of organic matter/N proxy, phosphorus, and potassium are low."
  },
  bswm_multiple_low_npk_pct: {
    label: "Multiple Low FertMap Nutrient Share",
    category: "BSWM FertMap",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "bswm_sample_count",
    colorScheme: "Reds",
    description: "Share of FertMap samples where at least two of organic matter/N proxy, phosphorus, and potassium are low."
  },
  bswm_fertilizer_constraint_score: {
    label: "FertMap Fertilizer Constraint Score",
    category: "BSWM FertMap",
    type: "numeric",
    unit: "/100",
    aggregation: "weighted_average",
    weightField: "bswm_sample_count",
    colorScheme: "YlOrRd",
    description: "Composite sample-based score from acidic pH, low organic matter/N proxy, low phosphorus, low potassium, and multiple-low nutrient overlap."
  },
  bswm_coverage_confidence_score: {
    label: "FertMap Coverage Confidence",
    category: "BSWM FertMap",
    type: "numeric",
    unit: "/100",
    aggregation: "weighted_average",
    weightField: "bswm_sample_count",
    colorScheme: "Blues",
    description: "Screening confidence based on FertMap sample count and distinct coordinate coverage."
  },
  bswm_has_fertmap_coverage: {
    label: "FertMap Coverage Present",
    category: "BSWM FertMap",
    type: "categorical",
    unit: "",
    aggregation: "dominant",
    colorScheme: "Greens",
    categories: { "Yes": 1, "No": 0 },
    description: "Whether the municipality has public DA-BSWM FertMap soil-test samples in the current extract."
  },
  irrigated_area: {
    label: "Irrigated Area",
    category: "Irrigation",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Blues",
    description: "Total irrigated area in hectares"
  },
  // --- Infrastructure ---
  rpc_site: {
    label: "RPC Site Present",
    category: "Infrastructure",
    type: "binary",
    unit: "",
    aggregation: "sum",
    colorScheme: "Purples",
    description: "Presence of Rice Processing Complex site"
  },

  // --- FMR Inventory from public Power BI report ---
  fmr_inventory_count: {
    label: "FMR Projects",
    category: "FMR Inventory",
    type: "numeric",
    unit: "projects",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    description: "Farm-to-market road project count from the DA RFO 02 public FMR inventory."
  },
  fmr_completed_count: {
    label: "Completed FMR Projects",
    category: "FMR Inventory",
    type: "numeric",
    unit: "projects",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "Completed FMR projects from the public FMR inventory."
  },
  fmr_ongoing_count: {
    label: "Ongoing FMR Projects",
    category: "FMR Inventory",
    type: "numeric",
    unit: "projects",
    aggregation: "sum",
    colorScheme: "Oranges",
    description: "Ongoing or under-construction FMR projects from the public FMR inventory."
  },
  fmr_inventory_length_km: {
    label: "FMR Length",
    category: "FMR Inventory",
    type: "numeric",
    unit: "km",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    description: "Total FMR length from the public FMR inventory."
  },
  fmr_influence_area_ha: {
    label: "FMR Influence Area",
    category: "FMR Inventory",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "Total agricultural influence area served by FMR projects."
  },
  fmr_farmer_beneficiaries: {
    label: "FMR Farmer Beneficiaries",
    category: "FMR Inventory",
    type: "numeric",
    unit: "farmers",
    aggregation: "sum",
    colorScheme: "Blues",
    description: "Farmer beneficiaries reported in the public FMR inventory."
  },
  fmr_latest_year: {
    label: "Latest FMR Funding Year",
    category: "FMR Inventory",
    type: "numeric",
    unit: "",
    aggregation: "max",
    colorScheme: "Blues",
    description: "Latest funding year represented in the FMR inventory for the area."
  },

  // --- F2C2 / FCA Clusters from public Power BI report ---
  f2c2_cluster_count: {
    label: "F2C2 Clusters",
    category: "F2C2 Clusters",
    type: "numeric",
    unit: "clusters",
    aggregation: "sum",
    colorScheme: "YlGn",
    description: "FCA/F2C2 cluster count from the DA RFO 02 public F2C2 Power BI report."
  },
  f2c2_area_ha: {
    label: "F2C2 Cluster Area",
    category: "F2C2 Clusters",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "Total area covered by FCA/F2C2 clusters."
  },
  f2c2_farmer_members: {
    label: "F2C2 Farmer Members",
    category: "F2C2 Clusters",
    type: "numeric",
    unit: "farmers",
    aggregation: "sum",
    colorScheme: "Blues",
    description: "Farmer members reported by FCA/F2C2 clusters."
  },
  f2c2_heads_count: {
    label: "F2C2 Animal Heads",
    category: "F2C2 Clusters",
    type: "numeric",
    unit: "heads",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    description: "Animal heads represented by FCA/F2C2 clusters when applicable."
  },
  f2c2_cluster_leaders: {
    label: "F2C2 Cluster Leaders",
    category: "F2C2 Clusters",
    type: "numeric",
    unit: "leaders",
    aggregation: "sum",
    colorScheme: "Purples",
    description: "Number of cluster leaders reported by FCA/F2C2 clusters."
  },
  f2c2_with_eom_count: {
    label: "F2C2 Clusters with EOM",
    category: "F2C2 Clusters",
    type: "numeric",
    unit: "clusters",
    aggregation: "sum",
    colorScheme: "Blues",
    description: "FCA/F2C2 clusters marked as having enterprise operation monitoring."
  },
  f2c2_latest_year: {
    label: "Latest F2C2 Year",
    category: "F2C2 Clusters",
    type: "numeric",
    unit: "",
    aggregation: "max",
    colorScheme: "Blues",
    description: "Latest year represented by FCA/F2C2 cluster records for the area."
  },
  f2c2_commodities: {
    label: "F2C2 Commodities",
    category: "F2C2 Clusters",
    type: "categorical",
    unit: "",
    aggregation: "dominant",
    colorScheme: "YlGn",
    description: "Commodity mix represented by FCA/F2C2 clusters."
  },
  f2c2_banner_programs: {
    label: "F2C2 Banner Programs",
    category: "F2C2 Clusters",
    type: "categorical",
    unit: "",
    aggregation: "dominant",
    colorScheme: "Blues",
    description: "Banner programs represented by FCA/F2C2 clusters."
  },
  f2c2_enterprise_statuses: {
    label: "F2C2 Enterprise Statuses",
    category: "F2C2 Clusters",
    type: "categorical",
    unit: "",
    aggregation: "dominant",
    colorScheme: "Purples",
    description: "Proposed enterprise status values represented by FCA/F2C2 clusters."
  },

  // --- ABEMIS infrastructure inventory as of March 30, 2026 ---
  abemis_total_projects: {
    label: "ABEMIS Projects",
    category: "ABEMIS Database",
    type: "numeric",
    unit: "projects",
    aggregation: "sum",
    colorScheme: "PuBu",
    year: "as of 2026-03-30",
    description: "Total infrastructure and facility project records from the ABEMIS inventory."
  },
  abemis_total_cost: {
    label: "ABEMIS Project Cost",
    category: "ABEMIS Database",
    type: "numeric",
    unit: "PHP",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    year: "as of 2026-03-30",
    description: "Total project cost encoded in the ABEMIS infrastructure inventory."
  },
  abemis_total_quantity: {
    label: "ABEMIS Quantity",
    category: "ABEMIS Database",
    type: "numeric",
    unit: "qty",
    aggregation: "sum",
    colorScheme: "Greens",
    year: "as of 2026-03-30",
    description: "Total quantity encoded across ABEMIS project records."
  },
  abemis_avg_cost_per_project: {
    label: "ABEMIS Avg Cost per Project",
    category: "ABEMIS Database",
    type: "numeric",
    unit: "PHP/project",
    aggregation: "ratio",
    numerator: "abemis_total_cost",
    denominator: "abemis_total_projects",
    colorScheme: "YlOrBr",
    year: "as of 2026-03-30",
    description: "Average ABEMIS project cost, computed from total encoded cost divided by project records."
  },
  abemis_latest_year: {
    label: "Latest ABEMIS Funding Year",
    category: "ABEMIS Database",
    type: "numeric",
    unit: "",
    aggregation: "max",
    colorScheme: "Blues",
    year: "as of 2026-03-30",
    description: "Latest year funded represented in the ABEMIS records for the area."
  },
  abemis_dominant_project_type: {
    label: "Dominant ABEMIS Project Type",
    category: "ABEMIS Database",
    type: "categorical",
    unit: "",
    aggregation: "dominant",
    colorScheme: "PuBu",
    year: "as of 2026-03-30",
    description: "Most common ABEMIS project type in the area."
  },
  abemis_dominant_project_group: {
    label: "Dominant ABEMIS Project Group",
    category: "ABEMIS Database",
    type: "categorical",
    unit: "",
    aggregation: "dominant",
    colorScheme: "PuBu",
    year: "as of 2026-03-30",
    description: "Most common ABEMIS planning group in the area."
  },
  abemis_fmr_projects: { label: "ABEMIS FMR Projects", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "YlOrBr", year: "as of 2026-03-30", description: "ABEMIS farm-to-market road project records." },
  abemis_fmr_cost: { label: "ABEMIS FMR Cost", category: "ABEMIS Database", type: "numeric", unit: "PHP", aggregation: "sum", colorScheme: "YlOrBr", year: "as of 2026-03-30", description: "Total encoded cost of ABEMIS farm-to-market road projects." },
  abemis_irrigation_projects: { label: "ABEMIS Irrigation/Water Projects", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Blues", year: "as of 2026-03-30", description: "ABEMIS irrigation and water-system project records." },
  abemis_irrigation_cost: { label: "ABEMIS Irrigation/Water Cost", category: "ABEMIS Database", type: "numeric", unit: "PHP", aggregation: "sum", colorScheme: "Blues", year: "as of 2026-03-30", description: "Total encoded cost of ABEMIS irrigation and water-system projects." },
  abemis_postharvest_projects: { label: "ABEMIS Postharvest/Processing Projects", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Oranges", year: "as of 2026-03-30", description: "ABEMIS postharvest, processing, drying, storage, and packing project records." },
  abemis_postharvest_cost: { label: "ABEMIS Postharvest/Processing Cost", category: "ABEMIS Database", type: "numeric", unit: "PHP", aggregation: "sum", colorScheme: "Oranges", year: "as of 2026-03-30", description: "Total encoded cost of ABEMIS postharvest and processing projects." },
  abemis_protected_cultivation_projects: { label: "ABEMIS Protected Cultivation Projects", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Greens", year: "as of 2026-03-30", description: "ABEMIS greenhouse, rainshelter, nursery, mushroom, and vermi-composting project records." },
  abemis_protected_cultivation_cost: { label: "ABEMIS Protected Cultivation Cost", category: "ABEMIS Database", type: "numeric", unit: "PHP", aggregation: "sum", colorScheme: "Greens", year: "as of 2026-03-30", description: "Total encoded cost of ABEMIS protected cultivation and nursery projects." },
  abemis_food_garden_projects: { label: "ABEMIS Food Garden Projects", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Greens", year: "as of 2026-03-30", description: "ABEMIS school garden and Gulayan sa Barangay project records." },
  abemis_food_garden_cost: { label: "ABEMIS Food Garden Cost", category: "ABEMIS Database", type: "numeric", unit: "PHP", aggregation: "sum", colorScheme: "Greens", year: "as of 2026-03-30", description: "Total encoded cost of ABEMIS food garden projects." },
  abemis_livestock_projects: { label: "ABEMIS Livestock Facility Projects", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Oranges", year: "as of 2026-03-30", description: "ABEMIS livestock housing project records." },
  abemis_livestock_cost: { label: "ABEMIS Livestock Facility Cost", category: "ABEMIS Database", type: "numeric", unit: "PHP", aggregation: "sum", colorScheme: "Oranges", year: "as of 2026-03-30", description: "Total encoded cost of ABEMIS livestock facility projects." },
  abemis_other_projects: { label: "ABEMIS Other Infrastructure Projects", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Purples", year: "as of 2026-03-30", description: "ABEMIS projects not assigned to the main planning groups." },
  abemis_other_cost: { label: "ABEMIS Other Infrastructure Cost", category: "ABEMIS Database", type: "numeric", unit: "PHP", aggregation: "sum", colorScheme: "Purples", year: "as of 2026-03-30", description: "Total encoded cost of ABEMIS projects not assigned to the main planning groups." },
  abemis_check_dam_count: { label: "Check Dam", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Blues", year: "as of 2026-03-30", description: "ABEMIS Check Dam project count." },
  abemis_chicken_housing_count: { label: "Chicken Housing", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Oranges", year: "as of 2026-03-30", description: "ABEMIS Chicken Housing project count." },
  abemis_coffee_processing_center_count: { label: "Coffee Processing Center", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "YlOrBr", year: "as of 2026-03-30", description: "ABEMIS Coffee Processing Center project count." },
  abemis_cold_storage_count: { label: "Cold Storage", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "PuBu", year: "as of 2026-03-30", description: "ABEMIS Cold Storage project count." },
  abemis_diversion_dam_count: { label: "Diversion Dam", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Blues", year: "as of 2026-03-30", description: "ABEMIS Diversion Dam project count." },
  abemis_farm_to_market_road_count: { label: "Farm-to-Market Road", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "YlOrBr", year: "as of 2026-03-30", description: "ABEMIS Farm-to-Market Road project count." },
  abemis_fertilizer_processing_center_count: { label: "Fertilizer Processing Center", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Greens", year: "as of 2026-03-30", description: "ABEMIS Fertilizer Processing Center project count." },
  abemis_grain_silo_count: { label: "Grain Silo", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "YlOrBr", year: "as of 2026-03-30", description: "ABEMIS Grain Silo project count." },
  abemis_greenhouse_count: { label: "Greenhouse", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Greens", year: "as of 2026-03-30", description: "ABEMIS Greenhouse project count." },
  abemis_gulayan_sa_barangay_count: { label: "Gulayan sa Barangay", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Greens", year: "as of 2026-03-30", description: "ABEMIS Gulayan sa Barangay project count." },
  abemis_mobile_solar_power_irrigation_unit_count: { label: "Mobile Solar Power Irrigation Unit", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Blues", year: "as of 2026-03-30", description: "ABEMIS Mobile Solar Power Irrigation Unit project count." },
  abemis_multi_commodity_drying_shed_count: { label: "Multi-Commodity Drying Shed", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Oranges", year: "as of 2026-03-30", description: "ABEMIS Multi-Commodity Drying Shed project count." },
  abemis_multi_crop_drying_pavement_mcdp_count: { label: "Multi Crop Drying Pavement (MCDP)", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Oranges", year: "as of 2026-03-30", description: "ABEMIS Multi Crop Drying Pavement project count." },
  abemis_multi_purpose_drying_pavement_count: { label: "Multi-Purpose Drying Pavement", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Oranges", year: "as of 2026-03-30", description: "ABEMIS Multi-Purpose Drying Pavement project count." },
  abemis_mushroom_fruiting_house_count: { label: "Mushroom Fruiting House", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Purples", year: "as of 2026-03-30", description: "ABEMIS Mushroom Fruiting House project count." },
  abemis_nursery_establishment_count: { label: "Nursery Establishment", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Greens", year: "as of 2026-03-30", description: "ABEMIS Nursery Establishment project count." },
  abemis_packinghouse_count: { label: "Packinghouse", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "PuBu", year: "as of 2026-03-30", description: "ABEMIS Packinghouse project count." },
  abemis_palay_shed_count: { label: "Palay Shed", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "YlGn", year: "as of 2026-03-30", description: "ABEMIS Palay Shed project count." },
  abemis_rabbit_housing_count: { label: "Rabbit Housing", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Oranges", year: "as of 2026-03-30", description: "ABEMIS Rabbit Housing project count." },
  abemis_rainshelter_count: { label: "Rainshelter", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Greens", year: "as of 2026-03-30", description: "ABEMIS Rainshelter project count." },
  abemis_rice_processing_center_count: { label: "Rice Processing Center", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "YlGn", year: "as of 2026-03-30", description: "ABEMIS Rice Processing Center project count." },
  abemis_school_garden_count: { label: "School Garden", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Greens", year: "as of 2026-03-30", description: "ABEMIS School Garden project count." },
  abemis_small_water_impounding_project_count: { label: "Small Water Impounding Project", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Blues", year: "as of 2026-03-30", description: "ABEMIS Small Water Impounding Project count." },
  abemis_solar_powered_fertigation_system_8_count: { label: "Solar-Powered Fertigation System", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Blues", year: "as of 2026-03-30", description: "ABEMIS Solar-Powered Fertigation System project count." },
  abemis_solar_powered_irrigation_system_count: { label: "Solar-Powered Irrigation System", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Blues", year: "as of 2026-03-30", description: "ABEMIS Solar-Powered Irrigation System project count." },
  abemis_spring_development_count: { label: "Spring Development", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Blues", year: "as of 2026-03-30", description: "ABEMIS Spring Development project count." },
  abemis_swine_housing_count: { label: "Swine Housing", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Oranges", year: "as of 2026-03-30", description: "ABEMIS Swine Housing project count." },
  abemis_vermi_composting_facilities_count: { label: "Vermi-Composting Facilities", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "Greens", year: "as of 2026-03-30", description: "ABEMIS Vermi-Composting Facilities project count." },
  abemis_village_type_corn_postharvest_processing_center_vtcppc_count: { label: "Village Type Corn Postharvest Processing Center", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "YlOrBr", year: "as of 2026-03-30", description: "ABEMIS Village Type Corn Postharvest Processing Center project count." },
  abemis_warehouse_count: { label: "Warehouse", category: "ABEMIS Database", type: "numeric", unit: "projects", aggregation: "sum", colorScheme: "YlOrBr", year: "as of 2026-03-30", description: "ABEMIS Warehouse project count." },

  // --- RSBSA municipal farmer registry from public Power BI report ---
  rsba_registry_count: {
    label: "RSBSA Registry Records",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "YlGn",
    description: "Municipal Registry System for Basic Sectors in Agriculture records from the public RSBSA Power BI report."
  },
  rsba_crop_area_ha: {
    label: "RSBSA Crop Area",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "Total crop area represented in RSBSA municipal records."
  },
  rsba_avg_farm_size_ha: {
    label: "RSBSA Avg Farm Size",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "ha",
    aggregation: "weighted_average",
    weightField: "rsba_registry_count",
    colorScheme: "YlGnBu",
    description: "Average crop area per RSBSA crop record, derived from aggregate municipal crop area divided by registry records."
  },
  rsba_rice_count: {
    label: "RSBSA Rice/Palay Records",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "YlGn",
    description: "RSBSA municipal records where crop name is Rice/Palay."
  },
  rsba_rice_area_ha: {
    label: "RSBSA Rice/Palay Area",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "Rice/Palay crop area represented in RSBSA municipal records."
  },
  rsba_rice_avg_farm_size_ha: {
    label: "RSBSA Rice Avg Farm Size",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "ha",
    aggregation: "weighted_average",
    weightField: "rsba_rice_count",
    colorScheme: "YlGnBu",
    description: "Average rice/palay area per RSBSA rice/palay crop record."
  },
  rsba_corn_count: {
    label: "RSBSA Corn Records",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    description: "RSBSA municipal records where crop name is Corn."
  },
  rsba_corn_area_ha: {
    label: "RSBSA Corn Area",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    description: "Corn crop area represented in RSBSA municipal records."
  },
  rsba_corn_avg_farm_size_ha: {
    label: "RSBSA Corn Avg Farm Size",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "ha",
    aggregation: "weighted_average",
    weightField: "rsba_corn_count",
    colorScheme: "YlOrBr",
    description: "Average corn area per RSBSA corn crop record."
  },
  rsba_top_crop: {
    label: "RSBSA Top Crop",
    category: "RSBSA Registry",
    type: "categorical",
    unit: "",
    aggregation: "dominant",
    colorScheme: "YlGn",
    description: "Crop with the highest RSBSA record count in the municipality."
  },
  rsba_female_count: {
    label: "RSBSA Female Records",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "Purples",
    description: "Female RSBSA records by municipality."
  },
  rsba_female_pct: {
    label: "RSBSA Female Share",
    category: "RSBSA Registry",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "rsba_registry_count",
    colorScheme: "Purples",
    description: "Female share of RSBSA municipal records."
  },
  rsba_youth_count: {
    label: "RSBSA Youth Records",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "Blues",
    description: "Generation Z and Generation Alpha RSBSA records by municipality."
  },
  rsba_youth_pct: {
    label: "RSBSA Youth Share",
    category: "RSBSA Registry",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "rsba_registry_count",
    colorScheme: "Blues",
    description: "Youth share of RSBSA municipal records."
  },
  rsba_farmer_count: {
    label: "RSBSA Farmer Sector Records",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "RSBSA records tagged as farmers."
  },
  rsba_farmworker_count: {
    label: "RSBSA Farmworker Records",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "Oranges",
    description: "RSBSA records tagged as farmworkers."
  },
  rsba_fisherfolk_count: {
    label: "RSBSA Fisherfolk Records",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "Blues",
    description: "RSBSA records tagged as fisherfolk."
  },
  rsba_ip_count: {
    label: "RSBSA IP Records",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    description: "RSBSA records tagged as Indigenous Peoples."
  },
  rsba_pwd_count: {
    label: "RSBSA PWD Records",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "Purples",
    description: "RSBSA records tagged as persons with disability."
  },
  rsba_4ps_count: {
    label: "RSBSA 4Ps Records",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "RSBSA records tagged under 4Ps."
  },
  rsba_fca_count: {
    label: "RSBSA FCA Members",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "RSBSA records tagged as FCA members."
  },
  rsba_fca_pct: {
    label: "RSBSA FCA Share",
    category: "RSBSA Registry",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "rsba_registry_count",
    colorScheme: "Greens",
    description: "Share of RSBSA records tagged as FCA members."
  },
  rsba_fca_gap_pct: {
    label: "RSBSA Non-FCA Share",
    category: "RSBSA Registry",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "rsba_registry_count",
    colorScheme: "Reds",
    description: "Share of RSBSA records not tagged as FCA members."
  },
  rsba_agriyouth_count: {
    label: "RSBSA Agri-Youth Records",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "Blues",
    description: "RSBSA records tagged as agri-youth."
  },
  rsba_arb_count: {
    label: "RSBSA ARB Records",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    description: "RSBSA records tagged as agrarian reform beneficiaries."
  },
  rsba_organic_count: {
    label: "RSBSA Organic Records",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "RSBSA records tagged for organic agriculture."
  },
  rsba_with_imc_count: {
    label: "RSBSA With IMC",
    category: "RSBSA Registry",
    type: "numeric",
    unit: "records",
    aggregation: "sum",
    colorScheme: "Blues",
    description: "RSBSA records tagged with interventions monitoring card."
  },
  rsba_imc_gap_pct: {
    label: "RSBSA Without IMC Share",
    category: "RSBSA Registry",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "rsba_registry_count",
    colorScheme: "Reds",
    description: "Share of RSBSA records not tagged with interventions monitoring card."
  },

  // --- PhilRice PRiSM Rice Season Monitoring ---
  prism_rice_area_2026s1: {
    label: "PRiSM Rice Area 2026 S1",
    category: "PRiSM Rice Monitoring",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "YlGn",
    description: "PhilRice PRiSM satellite-detected rice area for 2026 Semester 1, planted September 16, 2025 to March 15, 2026."
  },
  prism_standing_crop_area: {
    label: "PRiSM Standing Crop Area",
    category: "PRiSM Rice Monitoring",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "YlOrRd",
    description: "PRiSM reproductive plus ripening rice area as of April 28, 2026."
  },
  prism_standing_crop_pct: {
    label: "PRiSM Standing Crop Share",
    category: "PRiSM Rice Monitoring",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "prism_rice_area_2026s1",
    colorScheme: "YlOrRd",
    description: "Share of PRiSM detected rice area that remains in reproductive or ripening stage."
  },
  prism_growth_reproductive_ha: {
    label: "PRiSM Reproductive Stage",
    category: "PRiSM Rice Monitoring",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Oranges",
    description: "Rice area in reproductive stage as of April 28, 2026."
  },
  prism_growth_ripening_ha: {
    label: "PRiSM Ripening Stage",
    category: "PRiSM Rice Monitoring",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    description: "Rice area in ripening stage as of April 28, 2026."
  },
  prism_growth_harvested_ha: {
    label: "PRiSM Harvested Area",
    category: "PRiSM Rice Monitoring",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "Rice area already harvested as of April 28, 2026."
  },
  prism_harvest_progress_pct: {
    label: "PRiSM Harvest Progress",
    category: "PRiSM Rice Monitoring",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "prism_rice_area_2026s1",
    colorScheme: "Greens",
    description: "Share of PRiSM detected rice area already harvested as of April 28, 2026."
  },
  prism_upcoming_harvest_area: {
    label: "PRiSM May-Jun Harvest Area",
    category: "PRiSM Rice Monitoring",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    description: "Estimated rice area scheduled for harvest in May and June 2026."
  },
  prism_production_mt: {
    label: "PRiSM Rice Production 2026 S1",
    category: "PRiSM Rice Monitoring",
    type: "numeric",
    unit: "MT",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "PhilRice PRiSM end-season municipal rice production estimate for 2026 Semester 1."
  },
  prism_yield_mt_ha: {
    label: "PRiSM Rice Yield 2026 S1",
    category: "PRiSM Rice Monitoring",
    type: "numeric",
    unit: "MT/ha",
    aggregation: "weighted_average",
    weightField: "prism_rice_area_2026s1",
    colorScheme: "YlGn",
    description: "PhilRice PRiSM end-season municipal rice yield estimate for 2026 Semester 1."
  },
  prism_area_gap_vs_app_ha: {
    label: "PRiSM Area Gap vs App Rice Area",
    category: "PRiSM Rice Monitoring",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "RdBu_r",
    description: "Difference between PRiSM detected 2026 S1 rice area and the app's current rice area reference."
  },
  prism_area_gap_vs_app_pct: {
    label: "PRiSM Area Gap vs App Rice Area %",
    category: "PRiSM Rice Monitoring",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "rice_area_2025",
    colorScheme: "RdBu_r",
    description: "Percent difference between PRiSM detected 2026 S1 rice area and the app's current rice area reference."
  },

  // --- PRiSM Flood Damage Assessment ---
  prism_flooded_nonrice_ha: {
    label: "PRiSM Flooded Non-Rice Area",
    category: "PRiSM Flood Damage",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Blues",
    description: "Flooded non-rice area detected from Sentinel-1A/1C flood event mapping."
  },
  prism_flooded_vegetative_ha: {
    label: "PRiSM Flooded Vegetative Rice",
    category: "PRiSM Flood Damage",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "PuBu",
    description: "Flooded rice area in vegetative stage."
  },
  prism_flooded_reproductive_ha: {
    label: "PRiSM Flooded Reproductive Rice",
    category: "PRiSM Flood Damage",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Oranges",
    description: "Flooded rice area in reproductive stage."
  },
  prism_flooded_ripening_ha: {
    label: "PRiSM Flooded Ripening Rice",
    category: "PRiSM Flood Damage",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    description: "Flooded rice area in ripening stage."
  },
  prism_flooded_reproductive_ripening_ha: {
    label: "PRiSM Flooded Reproductive + Ripening Rice",
    category: "PRiSM Flood Damage",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "YlOrRd",
    description: "Flooded rice area in reproductive or ripening stage, useful for estimating near-term production risk."
  },
  prism_flooded_harvested_ha: {
    label: "PRiSM Flooded Harvested Rice",
    category: "PRiSM Flood Damage",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "Flooded rice area already tagged as harvested."
  },
  prism_flooded_standing_crop_ha: {
    label: "PRiSM Flooded Standing Crop",
    category: "PRiSM Flood Damage",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "Flooded vegetative, reproductive, and ripening rice area still standing in the field."
  },
  prism_flooded_rice_total_ha: {
    label: "PRiSM Total Flooded Rice Area",
    category: "PRiSM Flood Damage",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "Total flooded rice area across vegetative, reproductive, ripening, and harvested stages."
  },
  prism_flooded_standing_share_pct: {
    label: "PRiSM Flooded Standing Crop Share",
    category: "PRiSM Flood Damage",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "prism_standing_crop_area",
    colorScheme: "Reds",
    description: "Percent of PRiSM standing crop area affected by flood."
  },
  prism_flooded_rice_share_pct: {
    label: "PRiSM Flooded Rice Share",
    category: "PRiSM Flood Damage",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "prism_rice_area_2026s1",
    colorScheme: "Reds",
    description: "Percent of PRiSM detected rice area affected by flood."
  },
  prism_expected_production_at_risk_mt: {
    label: "PRiSM Expected Production at Risk",
    category: "PRiSM Flood Damage",
    type: "numeric",
    unit: "MT",
    aggregation: "sum",
    colorScheme: "OrRd",
    description: "Estimated production represented by flooded rice area, using municipal PRiSM yield."
  },
  prism_flood_damage_priority_score: {
    label: "PRiSM Flood Damage Priority Score",
    category: "PRiSM Flood Damage",
    type: "numeric",
    unit: "/100",
    aggregation: "weighted_average",
    weightField: "prism_flooded_rice_total_ha",
    colorScheme: "Reds",
    description: "Composite priority score using flooded standing crop, flooded rice share, production at risk, and small rice farm exposure."
  },
  prism_flood_damage_priority_class: {
    label: "PRiSM Flood Damage Priority Class",
    category: "PRiSM Flood Damage",
    type: "categorical",
    unit: "",
    aggregation: "dominant",
    colorScheme: "Reds",
    categories: { "Very High": 4, "High": 3, "Moderate": 2, "Low": 1, "No Flooded Rice Detected": 0 },
    description: "Classified flood-damage priority based on the composite PRiSM flood damage score."
  },

  // --- El Nino / Drought Rice Exposure ---
  pagasa_drought_outlook: {
    label: "PAGASA Drought Outlook",
    category: "El Nino Rice Risk",
    type: "categorical",
    unit: "",
    aggregation: "dominant",
    colorScheme: "YlOrRd",
    categories: { "Drought": 3, "Dry Spell": 2, "Dry Condition": 1, "Not Affected": 0 },
    description: "PAGASA dry condition, dry spell, and drought outlook by province."
  },
  pagasa_drought_score: {
    label: "PAGASA Drought Severity Score",
    category: "El Nino Rice Risk",
    type: "numeric",
    unit: "(0-3)",
    aggregation: "weighted_average",
    weightField: "prism_standing_crop_area",
    colorScheme: "YlOrRd",
    description: "Numeric drought class: 0=not affected, 1=dry condition, 2=dry spell, 3=drought."
  },
  pagasa_powerbi_rainfall_mm: {
    label: "PAGASA Power BI Rainfall",
    category: "El Nino Rice Risk",
    type: "numeric",
    unit: "mm",
    aggregation: "weighted_average",
    weightField: "prism_standing_crop_area",
    colorScheme: "Blues",
    description: "Rainfall amount extracted from the PAGASA Power BI report for the latest available climate advisory period."
  },
  pagasa_powerbi_rainfall_anomaly_pct: {
    label: "PAGASA Power BI Rainfall Anomaly",
    category: "El Nino Rice Risk",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "prism_standing_crop_area",
    colorScheme: "RdBu_r",
    description: "Rainfall anomaly from the PAGASA Power BI report. Negative values indicate rainfall deficit."
  },
  pagasa_powerbi_rainfall_deficit_score: {
    label: "PAGASA Power BI Rainfall Deficit Score",
    category: "El Nino Rice Risk",
    type: "numeric",
    unit: "/100",
    aggregation: "weighted_average",
    weightField: "prism_standing_crop_area",
    colorScheme: "YlOrRd",
    description: "Positive risk score derived from negative PAGASA Power BI rainfall anomaly. Higher values indicate stronger rainfall deficit."
  },
  pagasa_powerbi_drought_class: {
    label: "PAGASA Power BI Drought Class",
    category: "El Nino Rice Risk",
    type: "categorical",
    unit: "",
    aggregation: "dominant",
    colorScheme: "YlOrRd",
    categories: { "Drought": 3, "Dry Spell": 2, "Dry Condition": 1, "Not Affected": 0 },
    description: "Drought or dry-spell class extracted from the PAGASA Power BI report, used as a current advisory validation layer."
  },
  pagasa_powerbi_dry_spell_probability_pct: {
    label: "PAGASA Power BI Dry Spell Probability",
    category: "El Nino Rice Risk",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "prism_standing_crop_area",
    colorScheme: "YlOrRd",
    description: "Probability or likelihood of dry-spell conditions extracted from the PAGASA Power BI report."
  },
  pagasa_powerbi_heat_stress_days: {
    label: "PAGASA Power BI Heat Stress Days",
    category: "El Nino Rice Risk",
    type: "numeric",
    unit: "days",
    aggregation: "weighted_average",
    weightField: "prism_standing_crop_area",
    colorScheme: "OrRd",
    description: "Count of heat-stress days or equivalent high-temperature advisory signal extracted from the PAGASA Power BI report."
  },
  pagasa_powerbi_agri_risk_score: {
    label: "PAGASA Power BI Agri Risk Score",
    category: "El Nino Rice Risk",
    type: "numeric",
    unit: "/100",
    aggregation: "weighted_average",
    weightField: "prism_standing_crop_area",
    colorScheme: "Reds",
    description: "Composite agricultural climate risk signal derived from PAGASA Power BI rainfall deficit, dry-spell probability, drought class, and heat stress."
  },
  drrmis_elnino_historical_impact_score: {
    label: "DRRMIS Historical El Nino Impact Score",
    category: "El Nino Historical Impact",
    type: "numeric",
    unit: "/100",
    aggregation: "max",
    colorScheme: "Reds",
    description: "Province-level historical El Nino damage/loss score from DA-DRRMO DRRMIS. Repeated to municipalities for screening context only."
  },
  drrmis_elnino_historical_impact_class: {
    label: "DRRMIS Historical Impact Class",
    category: "El Nino Historical Impact",
    type: "categorical",
    unit: "",
    aggregation: "dominant",
    colorScheme: "Reds",
    categories: {
      "Very High Historical Impact": 4,
      "High Historical Impact": 3,
      "Moderate Historical Impact": 2,
      "Lower Historical Impact": 1,
      "No Extracted Historical Impact": 0
    },
    description: "Classified province-level historical El Nino impact from DA-DRRMO DRRMIS."
  },
  drrmis_elnino_episode_count: {
    label: "DRRMIS El Nino Episodes",
    category: "El Nino Historical Impact",
    type: "numeric",
    unit: "episodes",
    aggregation: "max",
    colorScheme: "OrRd",
    description: "Number of historical El Nino episodes with extracted drought damage/loss records for the province."
  },
  drrmis_elnino_total_farmers_affected: {
    label: "DRRMIS Farmers/Fisherfolk Affected",
    category: "El Nino Historical Impact",
    type: "numeric",
    unit: "persons",
    aggregation: "max",
    colorScheme: "Oranges",
    description: "Province-level historical total farmers/fisherfolk affected by El Nino drought reports."
  },
  drrmis_elnino_total_area_affected_ha: {
    label: "DRRMIS Total Area Affected",
    category: "El Nino Historical Impact",
    type: "numeric",
    unit: "ha",
    aggregation: "max",
    colorScheme: "YlOrRd",
    description: "Province-level historical total agricultural area affected by El Nino drought reports."
  },
  drrmis_elnino_total_production_loss_mt: {
    label: "DRRMIS Production Loss",
    category: "El Nino Historical Impact",
    type: "numeric",
    unit: "MT",
    aggregation: "max",
    colorScheme: "Purples",
    description: "Province-level historical total production loss from El Nino drought reports."
  },
  drrmis_elnino_total_value_loss_php: {
    label: "DRRMIS Value Loss",
    category: "El Nino Historical Impact",
    type: "numeric",
    unit: "PHP",
    aggregation: "max",
    colorScheme: "Reds",
    description: "Province-level historical total value loss from El Nino drought reports."
  },
  drrmis_elnino_rice_area_affected_ha: {
    label: "DRRMIS Rice Area Affected",
    category: "El Nino Historical Impact",
    type: "numeric",
    unit: "ha",
    aggregation: "max",
    colorScheme: "YlGn",
    description: "Province-level historical rice area affected by El Nino drought reports."
  },
  drrmis_elnino_rice_value_loss_php: {
    label: "DRRMIS Rice Value Loss",
    category: "El Nino Historical Impact",
    type: "numeric",
    unit: "PHP",
    aggregation: "max",
    colorScheme: "YlGn",
    description: "Province-level historical rice value loss from El Nino drought reports."
  },
  drrmis_elnino_corn_area_affected_ha: {
    label: "DRRMIS Corn Area Affected",
    category: "El Nino Historical Impact",
    type: "numeric",
    unit: "ha",
    aggregation: "max",
    colorScheme: "YlOrBr",
    description: "Province-level historical corn area affected by El Nino drought reports."
  },
  drrmis_elnino_corn_value_loss_php: {
    label: "DRRMIS Corn Value Loss",
    category: "El Nino Historical Impact",
    type: "numeric",
    unit: "PHP",
    aggregation: "max",
    colorScheme: "YlOrBr",
    description: "Province-level historical corn value loss from El Nino drought reports."
  },
  drrmis_elnino_hvcc_area_affected_ha: {
    label: "DRRMIS HVCC Area Affected",
    category: "El Nino Historical Impact",
    type: "numeric",
    unit: "ha",
    aggregation: "max",
    colorScheme: "Greens",
    description: "Province-level historical HVCC area affected by El Nino drought reports."
  },
  drrmis_elnino_hvcc_value_loss_php: {
    label: "DRRMIS HVCC Value Loss",
    category: "El Nino Historical Impact",
    type: "numeric",
    unit: "PHP",
    aggregation: "max",
    colorScheme: "Greens",
    description: "Province-level historical HVCC value loss from El Nino drought reports."
  },
  drrmis_elnino_latest_total_value_loss_php: {
    label: "DRRMIS Latest Episode Value Loss",
    category: "El Nino Historical Impact",
    type: "numeric",
    unit: "PHP",
    aggregation: "max",
    colorScheme: "Reds",
    description: "Province-level value loss from the latest extracted El Nino drought episode."
  },
  drrmis_elnino_latest_area_affected_ha: {
    label: "DRRMIS Latest Episode Area Affected",
    category: "El Nino Historical Impact",
    type: "numeric",
    unit: "ha",
    aggregation: "max",
    colorScheme: "YlOrRd",
    description: "Province-level area affected in the latest extracted El Nino drought episode."
  },
  drrmis_elnino_latest_farmers_affected: {
    label: "DRRMIS Latest Farmers/Fisherfolk Affected",
    category: "El Nino Historical Impact",
    type: "numeric",
    unit: "persons",
    aggregation: "max",
    colorScheme: "Oranges",
    description: "Province-level farmers/fisherfolk affected in the latest extracted El Nino drought episode."
  },
  elnino_prism_standing_exposed_area: {
    label: "El Nino Exposed Standing Rice",
    category: "El Nino Rice Risk",
    type: "numeric",
    unit: "ha",
    aggregation: "sum",
    colorScheme: "Reds",
    description: "PRiSM standing rice area weighted by PAGASA drought outlook severity."
  },
  elnino_irrigation_gap_pct: {
    label: "El Nino Irrigation Gap",
    category: "El Nino Rice Risk",
    type: "percentage",
    unit: "%",
    aggregation: "weighted_average",
    weightField: "prism_rice_area_2026s1",
    colorScheme: "Oranges",
    description: "Estimated rice area not covered by recorded irrigated area."
  },
  elnino_rice_risk_score: {
    label: "El Nino Rice Risk Score",
    category: "El Nino Rice Risk",
    type: "numeric",
    unit: "/100",
    aggregation: "weighted_average",
    weightField: "prism_standing_crop_area",
    colorScheme: "Reds",
    description: "Composite risk score combining PAGASA drought class, PRiSM standing rice, irrigation gap, poverty, and poor rice farmer exposure."
  },
  elnino_resilience_priority_score: {
    label: "El Nino Resilience Priority Score",
    category: "El Nino Resilience",
    type: "numeric",
    unit: "/100",
    aggregation: "weighted_average",
    weightField: "population",
    colorScheme: "Reds",
    description: "Composite decision score combining climate exposure, farmer vulnerability, production sensitivity, response capacity gaps, and implementation gaps."
  },
  elnino_resilience_climate_exposure_score: {
    label: "Climate Exposure Score",
    category: "El Nino Resilience",
    type: "numeric",
    unit: "/100",
    aggregation: "weighted_average",
    weightField: "population",
    colorScheme: "YlOrRd",
    description: "Drought outlook, PRiSM standing/reproductive/ripening rice, drought hazard, and flood/typhoon exposure."
  },
  elnino_resilience_farmer_vulnerability_score: {
    label: "Farmer Vulnerability Score",
    category: "El Nino Resilience",
    type: "numeric",
    unit: "/100",
    aggregation: "weighted_average",
    weightField: "population",
    colorScheme: "Oranges",
    description: "Poverty, small rice/corn farms, malnutrition, and RSBSA social-targeting exposure."
  },
  elnino_resilience_production_sensitivity_score: {
    label: "Production Sensitivity Score",
    category: "El Nino Resilience",
    type: "numeric",
    unit: "/100",
    aggregation: "weighted_average",
    weightField: "population",
    colorScheme: "PuRd",
    description: "Soil stress, acidity, NPK, zinc, irrigation gap, crop area, and yield sensitivity."
  },
  elnino_resilience_response_capacity_gap_score: {
    label: "Response Capacity Gap Score",
    category: "El Nino Resilience",
    type: "numeric",
    unit: "/100",
    aggregation: "weighted_average",
    weightField: "population",
    colorScheme: "Greys",
    description: "Estimated gap after considering irrigation, FMR, postharvest, F2C2, and planned infrastructure coverage."
  },
  elnino_resilience_implementation_gap_score: {
    label: "Implementation Gap Score",
    category: "El Nino Resilience",
    type: "numeric",
    unit: "/100",
    aggregation: "weighted_average",
    weightField: "population",
    colorScheme: "Reds",
    description: "Plan need gap, missing 2027 allocation, and missing irrigation/FMR plan signals."
  },

  // --- DA Plans and Projects 2025-2027 ---
  plans_projects_2027_count: {
    label: "2027 Plan Items",
    category: "Plans & Projects",
    type: "numeric",
    unit: "items",
    aggregation: "sum",
    colorScheme: "Blues",
    description: "Number of extracted FY 2027 plan/project items assigned to the municipality from DA planning workbooks."
  },
  plans_projects_2027_budget: {
    label: "2027 Plan Budget",
    category: "Plans & Projects",
    type: "numeric",
    unit: "PHP '000",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "Extracted FY 2027 plan/project budget allocation in thousand pesos."
  },
  plans_projects_total_count: {
    label: "2025-2027 Plan Items",
    category: "Plans & Projects",
    type: "numeric",
    unit: "items",
    aggregation: "sum",
    colorScheme: "Blues",
    description: "Total extracted plan/project items from 2025, 2026, and 2027."
  },
  plans_projects_total_budget: {
    label: "2025-2027 Plan Budget",
    category: "Plans & Projects",
    type: "numeric",
    unit: "PHP '000",
    aggregation: "sum",
    colorScheme: "Greens",
    description: "Total extracted plan/project budget from 2025, 2026, and 2027 in thousand pesos."
  },
  plans_fmr_2027_count: {
    label: "2027 FMR Project Items",
    category: "Plans & Projects",
    type: "numeric",
    unit: "items",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    description: "FY 2027 farm-to-market road or PRDP road project items."
  },
  plans_fmr_2027_budget: {
    label: "2027 FMR Budget",
    category: "Plans & Projects",
    type: "numeric",
    unit: "PHP '000",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    description: "FY 2027 farm-to-market road or PRDP road budget in thousand pesos."
  },
  plans_fmr_2027_length_km: {
    label: "2027 FMR Length",
    category: "Plans & Projects",
    type: "numeric",
    unit: "km",
    aggregation: "sum",
    colorScheme: "YlOrBr",
    description: "Estimated length of FY 2027 FMR/PRDP road projects."
  },
  plans_irrigation_2027_count: {
    label: "2027 Irrigation Project Items",
    category: "Plans & Projects",
    type: "numeric",
    unit: "items",
    aggregation: "sum",
    colorScheme: "Blues",
    description: "FY 2027 plan items related to irrigation, pumps, canals, or water systems."
  },
  plans_2027_budget_per_small_farm: {
    label: "2027 Budget per Small Farm",
    category: "Plans & Projects",
    type: "numeric",
    unit: "PHP '000/farm",
    aggregation: "ratio",
    colorScheme: "Greens",
    description: "FY 2027 plan budget divided by rice and corn farms below 0.5 hectare."
  },
  plans_2027_need_gap_score: {
    label: "2027 Plan Need Gap Score",
    category: "Plans & Projects",
    type: "numeric",
    unit: "/100",
    aggregation: "weighted_average",
    weightField: "population",
    colorScheme: "Reds",
    description: "Higher score means high poverty/small-farm/climate need with relatively thinner 2027 plan allocation."
  },

  // ============================================================
  // CLIMATE RISK VULNERABILITY ASSESSMENT (CRVA)
  // Based on DA-CRAO / AMIA CRVA Framework (IPCC AR4)
  // Source: CIAO / CIAT — https://ciatph.github.io
  // ============================================================

  // --- CRVA Composite / Overall ---
  crva_index_rice: {
    label: "CRVA Index — Rice",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "Reds",
    higherIsBetter: false,
    description: "Overall climate risk vulnerability index for rice production (0=low, 1=very high). Composite of Sensitivity, Hazard Exposure, and Adaptive Capacity (weights: 15%, 15%, 70%)."
  },
  crva_index_corn: {
    label: "CRVA Index — Corn",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "Reds",
    higherIsBetter: false,
    description: "Overall climate risk vulnerability index for corn production."
  },

  // ------------ SENSITIVITY ------------
  // Sensitivity = change in climatic suitability of crops (MaxEnt model, RCP 8.5, year 2050 vs baseline)
  // Index: -1.0 = very high gain in suitability; +1.0 = very high loss (negative impact)
  sensitivity_rice: {
    label: "Sensitivity — Rice",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(−1 to +1)",
    aggregation: "weighted_average",
    colorScheme: "RdBu_r",
    higherIsBetter: false,
    description: "Change in rice climatic suitability by 2050 vs baseline. Positive = loss in suitability (worse). Based on MaxEnt species distribution modelling using 19–20 bioclimatic variables (WorldClim) and RCP 8.5 scenario."
  },
  sensitivity_corn: {
    label: "Sensitivity — Corn",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(−1 to +1)",
    aggregation: "weighted_average",
    colorScheme: "RdBu_r",
    higherIsBetter: false,
    description: "Change in corn climatic suitability by 2050 vs baseline (RCP 8.5)."
  },
  sensitivity_coconut: {
    label: "Sensitivity — Coconut",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(−1 to +1)",
    aggregation: "weighted_average",
    colorScheme: "RdBu_r",
    higherIsBetter: false,
    description: "Change in coconut climatic suitability by 2050 vs baseline (RCP 8.5)."
  },
  sensitivity_banana: {
    label: "Sensitivity — Banana",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(−1 to +1)",
    aggregation: "weighted_average",
    colorScheme: "RdBu_r",
    higherIsBetter: false,
    description: "Change in banana climatic suitability by 2050 vs baseline (RCP 8.5)."
  },
  sensitivity_hvc: {
    label: "Sensitivity — High-Value Crops",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(−1 to +1)",
    aggregation: "weighted_average",
    colorScheme: "RdBu_r",
    higherIsBetter: false,
    description: "Composite sensitivity index for high-value crops (vegetables, fruit trees)."
  },

  // ------------ HAZARD / EXPOSURE ------------
  // 8 climate-related hazards from national agencies (MGB, DOST-PAGASA, NAMRIA, etc.)
  // Index: 0 = no/low hazard, 1 = very high hazard
  hazard_index: {
    label: "Hazard Index (Composite)",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "YlOrRd",
    higherIsBetter: false,
    description: "Composite hazard exposure index across all 8 climate-related hazards. Data sourced from DENR-MGB, DOST-PAGASA, NAMRIA, and other national agencies."
  },
  hazard_typhoon: {
    label: "Hazard — Typhoon",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "YlOrRd",
    higherIsBetter: false,
    description: "Exposure index to typhoon hazard. Based on historical typhoon tracks and wind intensity data."
  },
  hazard_flood: {
    label: "Hazard — Flood",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "Blues",
    higherIsBetter: false,
    description: "Exposure index to flooding hazard. Based on DOST-PAGASA and DENR-MGB flood susceptibility maps."
  },
  hazard_drought: {
    label: "Hazard — Drought",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "YlOrBr",
    higherIsBetter: false,
    description: "Exposure index to drought hazard. Based on SPI (Standardized Precipitation Index) and ENSO patterns."
  },
  hazard_soil_erosion: {
    label: "Hazard — Soil Erosion",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "YlOrBr",
    higherIsBetter: false,
    description: "Soil erosion susceptibility index from DENR-BSWM."
  },
  hazard_landslide: {
    label: "Hazard — Landslide",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "Oranges",
    higherIsBetter: false,
    description: "Landslide susceptibility index from DENR-MGB."
  },
  hazard_swi: {
    label: "Hazard — Salt Water Intrusion",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "Blues",
    higherIsBetter: false,
    description: "Salt water intrusion susceptibility index. Relevant for coastal and river-delta areas."
  },
  hazard_storm_surge: {
    label: "Hazard — Storm Surge",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "Blues",
    higherIsBetter: false,
    description: "Storm surge exposure index from NAMRIA and DOST-PAGASA."
  },
  hazard_sea_level_rise: {
    label: "Hazard — Sea Level Rise",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "Blues",
    higherIsBetter: false,
    description: "Sea level rise vulnerability index. Relevant for coastal municipalities."
  },

  // ------------ ADAPTIVE CAPACITY (AC) ------------
  // 8 Capitals per DA-AMIA CRVA Framework
  // Index: 0 = very low AC, 1 = very high AC (higher is BETTER — more capacity to adapt)
  ac_index: {
    label: "Adaptive Capacity Index (Composite)",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "Greens",
    higherIsBetter: true,
    description: "Composite adaptive capacity index across all 8 capitals. Weight in overall CRVA: 70% (most critical component). 0–0.20 = very low, 0.20–0.40 = low, 0.40–0.60 = moderate, 0.60–0.80 = high, 0.80–1.0 = very high."
  },
  ac_economic: {
    label: "AC — Economic Capital",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "Greens",
    higherIsBetter: true,
    description: "Economic capital: access to credit, number of financial institutions, cooperatives, employed population, income sources, poverty incidence."
  },
  ac_natural: {
    label: "AC — Natural Capital",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "Greens",
    higherIsBetter: true,
    description: "Natural capital: forest cover, soil quality, water resource availability, protected area coverage."
  },
  ac_human: {
    label: "AC — Human Capital",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "Greens",
    higherIsBetter: true,
    description: "Human capital: literacy rate, years of schooling, number of agricultural technicians, farmer education level."
  },
  ac_physical: {
    label: "AC — Physical Capital",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "Greens",
    higherIsBetter: true,
    description: "Physical capital: road density, irrigation infrastructure, post-harvest facilities, storage facilities, electricity access."
  },
  ac_social: {
    label: "AC — Social Capital",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "Greens",
    higherIsBetter: true,
    description: "Social capital: number of farmer organizations, cooperative membership rate, social cohesion indicators."
  },
  ac_health: {
    label: "AC — Health Capital",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "Greens",
    higherIsBetter: true,
    description: "Health capital: doctor-to-population ratio, number of health facilities, life expectancy, malnutrition rates."
  },
  ac_anticipatory: {
    label: "AC — Anticipatory Capital",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "Greens",
    higherIsBetter: true,
    description: "Anticipatory capital: DRRM registrations, farmer training count, % farmers with access to mobile phones/TV/radio, weather advisory access, early warning systems."
  },
  ac_institutional: {
    label: "AC — Institutional Capital",
    category: "Climate Risk Vulnerability",
    type: "index",
    unit: "(0–1)",
    aggregation: "weighted_average",
    colorScheme: "Greens",
    higherIsBetter: true,
    description: "Institutional capital: LGU income class, Cities & Municipalities Competitiveness Index (CMCI), presence of DRRM office, agricultural extension services."
  }
};

// ============================================================
// CATEGORIES — determines sidebar grouping and order
// ============================================================
const CATEGORIES = [
  "Demographics",
  "Poverty",
  "Malnutrition",
  "Rice",
  "Corn",
  "Pest and Disease",
  "ASF",
  "Soil Fertility",
  "BSWM FertMap",
  "FMR Inventory",
  "F2C2 Clusters",
  "ABEMIS Database",
  "RSBSA Registry",
  "PRiSM Rice Monitoring",
  "PRiSM Flood Damage",
  "El Nino Rice Risk",
  "El Nino Historical Impact",
  "El Nino Resilience",
  "Plans & Projects",
  "Climate Risk Vulnerability",
  "Planning Priority"
];

// ============================================================
// COLOR SCHEMES (Brewer-inspired, colorblind-friendly)
// ============================================================
const COLOR_SCHEMES = {
  Blues:    ["#deebf7","#c6dbef","#9ecae1","#6baed6","#4292c6","#2171b5","#084594"],
  Reds:     ["#fee5d9","#fcbba1","#fc9272","#fb6a4a","#ef3b2c","#cb181d","#99000d"],
  Greens:   ["#edf8e9","#c7e9c0","#a1d99b","#74c476","#41ab5d","#238b45","#005a32"],
  Oranges:  ["#feedde","#fdd0a2","#fdae6b","#fd8d3c","#f16913","#d94801","#7f2704"],
  Purples:  ["#f2f0f7","#dadaeb","#bcbddc","#9e9ac8","#807dba","#6a51a3","#4a1486"],
  Greys:    ["#f7f7f7","#e5e5e5","#cccccc","#969696","#737373","#525252","#252525"],
  PuBu:     ["#fff7fb","#ece7f2","#d0d1e6","#a6bddb","#74a9cf","#3690c0","#0570b0"],
  YlGn:     ["#ffffcc","#d9f0a3","#addd8e","#78c679","#41ab5d","#238443","#005a32"],
  YlOrBr:   ["#ffffe5","#fff7bc","#fee391","#fec44f","#fe9929","#ec7014","#8c2d04"],
  OrRd:     ["#fff7ec","#fee8c8","#fdd49e","#fdbb84","#fc8d59","#e34a33","#b30000"],
  YlOrRd:   ["#ffffb2","#fed976","#feb24c","#fd8d3c","#fc4e2a","#e31a1c","#b10026"],
  // Diverging: blue=gain in suitability (good), red=loss in suitability (bad)
  RdBu_r:   ["#4393c3","#74add1","#abd9e9","#e0f3f8","#fee08b","#fc8d59","#d73027"],
  YlOrRd:   ["#ffffb2","#fed976","#feb24c","#fd8d3c","#fc4e2a","#e31a1c","#b10026"],
  RdYlGn:   ["#d73027","#f46d43","#fdae61","#fee08b","#d9ef8b","#a6d96a","#1a9850"],
  Bivariate: {
    "LL": "#e8e8e8", "LM": "#ace4e4", "LH": "#5ac8c8",
    "ML": "#dfb0d6", "MM": "#a5add3", "MH": "#5698b9",
    "HL": "#be64ac", "HM": "#8c62aa", "HH": "#3b4994"
  }
};

// ============================================================
// BASEMAP CONFIGURATION
// ============================================================
const BASEMAPS = {
  osm: {
    label: "OpenStreetMap",
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  },
  cartoLight: {
    label: "CartoDB Positron",
    url: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors © <a href="https://carto.com/attributions">CARTO</a>'
  },
  cartoDark: {
    label: "CartoDB Dark Matter",
    url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors © <a href="https://carto.com/attributions">CARTO</a>'
  },
  esriImagery: {
    label: "Esri World Imagery",
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attribution: 'Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP'
  },
  esriTopo: {
    label: "Esri World Topographic",
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
    attribution: 'Tiles © Esri — Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community'
  },
  // NOTE: Google Maps tiles require a valid API key and compliance with Google's Terms of Service.
  // Replace "YOUR_GOOGLE_MAPS_API_KEY" below before enabling.
  // googleSatellite: {
  //   label: "Google Satellite",
  //   url: "http://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}",
  //   attribution: 'Map data © Google'
  // },
  // googleTerrain: {
  //   label: "Google Terrain",
  //   url: "http://mt0.google.com/vt/lyrs=p&hl=en&x={x}&y={y}&z={z}",
  //   attribution: 'Map data © Google'
  // },
  // googleHybrid: {
  //   label: "Google Hybrid",
  //   url: "http://mt0.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}",
  //   attribution: 'Map data © Google'
  // },
  // googleRoadmap: {
  //   label: "Google Roadmap",
  //   url: "http://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}",
  //   attribution: 'Map data © Google'
  // }
};

// ============================================================
// VISUALIZATION STYLES
// ============================================================
const VIZ_STYLES = [
  { id: "choropleth",        label: "Choropleth" },
  { id: "gradient",          label: "Gradient" },
  { id: "proportional",      label: "Proportional Circles" },
  { id: "bivariate",         label: "Bivariate Comparison" },
  { id: "dominant_crop",     label: "Dominant Crop" },
  { id: "pie_symbols",       label: "Pie Chart Symbols" },
  { id: "bar_symbols",       label: "Bar Chart Symbols" },
  { id: "ranked",            label: "Ranked Highlight" },
  { id: "deviation",         label: "Deviation from Regional Avg" },
  { id: "ratio",             label: "Ratio Map" },
  { id: "priority",          label: "Planning Priority" }
];

// ============================================================
// PRIORITY SCORING MODELS
// ============================================================
const PRIORITY_MODELS = {
  rice: {
    label: "Rice Intervention Priority",
    weights: {
      poor_rice_farmers: 0.25,
      poverty_2023: 0.20,
      rice_yield_gap: 0.20,
      rice_mechanization_gap: 0.15,
      irrigation_gap: 0.10,
      pest_disease_score: 0.10
    }
  },
  corn: {
    label: "Corn Intervention Priority",
    weights: {
      poor_corn_farmers: 0.25,
      poverty_2023: 0.20,
      corn_yield_gap: 0.20,
      corn_mechanization_gap: 0.15,
      irrigation_gap: 0.10,
      pest_disease_score: 0.10
    }
  },
  nutrition: {
    label: "Nutrition-Sensitive Agriculture Priority",
    weights: {
      poverty_2023: 0.20,
      stunting: 0.20,
      underweight: 0.20,
      wasting: 0.15,
      population: 0.10,
      poor_rice_farmers: 0.075,
      poor_corn_farmers: 0.075
    }
  },
  climate: {
    label: "Climate & Biosecurity Priority",
    weights: {
      pest_disease_score: 0.25,
      asf_score: 0.20,
      poverty_2023: 0.15,
      irrigation_gap: 0.15,
      soil_fertility_gap: 0.15,
      poor_rice_farmers: 0.05,
      poor_corn_farmers: 0.05
    }
  },
  rcpc_crop_protection: {
    label: "RCPC Crop Protection Priority",
    weights: {
      rcpc_surveillance_priority_score: 0.25,
      rcpc_pest_pressure_score: 0.20,
      rcpc_response_gap_score: 0.15,
      rcpc_recent_affected_area_ha: 0.12,
      rcpc_recent_affected_farmers: 0.10,
      rcpc_high_severity_records: 0.08,
      poverty_2023: 0.05,
      plans_2027_need_gap_score: 0.05
    }
  },
  asf_biosecurity: {
    label: "ASF Biosecurity Response Priority",
    weights: {
      asf_risk_score: 0.40,
      asf_positive_total: 0.20,
      asf_positive_rate_pct: 0.15,
      asf_affected_barangays: 0.10,
      abemis_swine_housing_count: 0.08,
      poverty_2023: 0.07
    }
  },
  soil_rehab: {
    label: "Soil Fertility Rehabilitation Priority",
    weights: {
      soil_fertility_stress_score: 0.30,
      soil_low_fertility_area_ha: 0.20,
      soil_acidic_low_fertility_area_ha: 0.15,
      soil_npk_multiple_low_area_ha: 0.15,
      poverty_2023: 0.10,
      plans_2027_need_gap_score: 0.10
    }
  },
  soil_acidity: {
    label: "Acidity and Liming Priority",
    weights: {
      soil_acidic_area_ha: 0.35,
      soil_acidic_pct: 0.20,
      soil_acidic_low_fertility_area_ha: 0.20,
      rice_area_2025: 0.10,
      corn_area_2025: 0.10,
      poverty_2023: 0.05
    }
  },
  soil_npk: {
    label: "NPK Balancing Priority",
    weights: {
      soil_npk_multiple_low_area_ha: 0.30,
      soil_npk_multiple_low_pct: 0.20,
      soil_n_low_pct: 0.15,
      soil_p_low_pct: 0.15,
      soil_k_low_pct: 0.10,
      soil_lab_area_ha: 0.10
    }
  },
  soil_zinc: {
    label: "Zinc Deficiency Correction Priority",
    weights: {
      soil_zinc_deficient_area_ha: 0.35,
      soil_zinc_deficient_pct: 0.20,
      soil_low_fertility_zinc_def_area_ha: 0.20,
      soil_rice_zinc_deficient_pct: 0.10,
      soil_corn_zinc_deficient_pct: 0.10,
      poverty_2023: 0.05
    }
  },
  soil_rice: {
    label: "Rice Soil Constraint Priority",
    weights: {
      soil_rice_low_fertility_area_ha: 0.25,
      soil_rice_low_fertility_pct: 0.15,
      soil_rice_acidic_pct: 0.15,
      soil_rice_npk_multiple_low_pct: 0.15,
      poor_rice_farmers: 0.15,
      rice_yield_gap: 0.15
    }
  },
  soil_corn: {
    label: "Corn Soil Constraint Priority",
    weights: {
      soil_corn_low_fertility_area_ha: 0.25,
      soil_corn_low_fertility_pct: 0.15,
      soil_corn_acidic_pct: 0.15,
      soil_corn_npk_multiple_low_pct: 0.15,
      poor_corn_farmers: 0.15,
      corn_yield_gap: 0.15
    }
  },
  bswm_fertmap_advisory: {
    label: "BSWM FertMap Advisory Priority",
    weights: {
      bswm_fertilizer_constraint_score: 0.30,
      bswm_coverage_confidence_score: 0.15,
      bswm_acidic_sample_pct: 0.15,
      bswm_multiple_low_npk_pct: 0.15,
      bswm_low_p_pct: 0.08,
      bswm_low_k_pct: 0.08,
      rice_area_2025: 0.05,
      corn_area_2025: 0.04
    }
  },
  prism: {
    label: "PRiSM Rice Season Monitoring",
    weights: {
      prism_standing_crop_area: 0.30,
      prism_upcoming_harvest_area: 0.25,
      prism_area_gap_abs: 0.15,
      poverty_2023: 0.10,
      poor_rice_farmers: 0.10,
      pest_disease_score: 0.10
    }
  },
  prism_flood: {
    label: "PRiSM Flood Damage Priority",
    weights: {
      prism_flood_damage_priority_score: 0.35,
      prism_flooded_standing_crop_ha: 0.20,
      prism_flooded_reproductive_ripening_ha: 0.15,
      prism_expected_production_at_risk_mt: 0.10,
      prism_flooded_standing_share_pct: 0.10,
      poor_rice_farmers: 0.10
    }
  },
  elnino: {
    label: "El Nino Rice Exposure Priority",
    weights: {
      elnino_rice_risk_score: 0.30,
      elnino_prism_standing_exposed_area: 0.22,
      pagasa_drought_score: 0.12,
      pagasa_powerbi_agri_risk_score: 0.10,
      pagasa_powerbi_rainfall_deficit_score: 0.08,
      elnino_irrigation_gap_pct: 0.10,
      poverty_2023: 0.04,
      poor_rice_farmers: 0.04
    }
  },
  pagasa_validation: {
    label: "PAGASA Advisory Exposure Validation",
    weights: {
      pagasa_powerbi_agri_risk_score: 0.24,
      pagasa_powerbi_rainfall_deficit_score: 0.16,
      pagasa_powerbi_dry_spell_probability_pct: 0.14,
      pagasa_drought_score: 0.12,
      prism_standing_crop_area: 0.14,
      elnino_irrigation_gap_pct: 0.08,
      poor_rice_farmers: 0.06,
      plans_2027_need_gap_score: 0.06
    }
  },
  drrmis_elnino_history: {
    label: "DRRMIS Historical El Nino Impact",
    weights: {
      drrmis_elnino_historical_impact_score: 0.34,
      drrmis_elnino_episode_count: 0.18,
      drrmis_elnino_total_value_loss_php: 0.18,
      drrmis_elnino_total_area_affected_ha: 0.12,
      drrmis_elnino_total_farmers_affected: 0.10,
      drrmis_elnino_latest_total_value_loss_php: 0.08
    }
  },
  elnino_resilience: {
    label: "El Nino Resilience Package Priority",
    weights: {
      elnino_resilience_priority_score: 0.25,
      elnino_resilience_climate_exposure_score: 0.17,
      drrmis_elnino_historical_impact_score: 0.08,
      pagasa_powerbi_agri_risk_score: 0.08,
      elnino_resilience_farmer_vulnerability_score: 0.17,
      elnino_resilience_production_sensitivity_score: 0.13,
      bswm_fertilizer_constraint_score: 0.04,
      elnino_resilience_implementation_gap_score: 0.10,
      elnino_resilience_response_capacity_gap_score: 0.06,
      pagasa_powerbi_dry_spell_probability_pct: 0.02
    }
  },
  projects: {
    label: "2027 Plan Need Gap Priority",
    weights: {
      plans_2027_need_gap_score: 0.35,
      poverty_2023: 0.15,
      poor_rice_farmers: 0.15,
      poor_corn_farmers: 0.15,
      elnino_rice_risk_score: 0.10,
      crva_index_rice: 0.05,
      irrigation_gap: 0.05
    }
  },
  fmr_access: {
    label: "FMR Access and Coverage Priority",
    weights: {
      plans_fmr_2027_count: 0.18,
      fmr_inventory_count: 0.17,
      fmr_inventory_length_km: 0.17,
      fmr_influence_area_ha: 0.14,
      fmr_farmer_beneficiaries: 0.14,
      poor_rice_farmers: 0.10,
      poor_corn_farmers: 0.10
    }
  },
  f2c2_cluster_support: {
    label: "F2C2 Cluster and Enterprise Support Priority",
    weights: {
      f2c2_cluster_count: 0.20,
      f2c2_area_ha: 0.18,
      f2c2_farmer_members: 0.18,
      f2c2_cluster_leaders: 0.12,
      f2c2_with_eom_count: 0.10,
      poor_rice_farmers: 0.11,
      poor_corn_farmers: 0.11
    }
  },
  abemis_infra_review: {
    label: "ABEMIS Infrastructure Review Priority",
    weights: {
      abemis_total_projects: 0.18,
      abemis_total_cost: 0.16,
      abemis_fmr_projects: 0.12,
      abemis_irrigation_projects: 0.12,
      abemis_postharvest_projects: 0.10,
      abemis_protected_cultivation_projects: 0.08,
      poor_rice_farmers: 0.10,
      poor_corn_farmers: 0.10,
      poverty_2023: 0.04
    }
  },
  rsba_registry_targeting: {
    label: "RSBSA Farmer Registry Targeting Priority",
    weights: {
      rsba_registry_count: 0.24,
      rsba_crop_area_ha: 0.18,
      poverty_2023: 0.16,
      rsba_farmer_count: 0.14,
      rsba_farmworker_count: 0.10,
      rsba_fisherfolk_count: 0.08,
      rsba_imc_gap_pct: 0.10
    }
  },
  rsba_rice_corn: {
    label: "RSBSA Rice and Corn Producer Priority",
    weights: {
      rsba_rice_count: 0.20,
      rsba_corn_count: 0.20,
      rsba_rice_area_ha: 0.15,
      rsba_corn_area_ha: 0.15,
      poor_rice_farmers: 0.10,
      poor_corn_farmers: 0.10,
      poverty_2023: 0.10
    }
  },
  rsba_inclusion: {
    label: "RSBSA Inclusion and Social Targeting Priority",
    weights: {
      rsba_4ps_count: 0.18,
      rsba_ip_count: 0.16,
      rsba_pwd_count: 0.14,
      rsba_female_count: 0.14,
      rsba_youth_count: 0.14,
      poverty_2023: 0.14,
      rsba_registry_count: 0.10
    }
  },
  rsba_fca_organizing: {
    label: "RSBSA FCA Organizing Gap Priority",
    weights: {
      rsba_fca_gap_pct: 0.28,
      rsba_registry_count: 0.20,
      rsba_rice_count: 0.12,
      rsba_corn_count: 0.12,
      f2c2_cluster_count: 0.10,
      rsba_with_imc_count: 0.08,
      poverty_2023: 0.10
    }
  }
};

// ============================================================
// PLANNING INSIGHT RULES
// Auto-generates text interpretation for selected municipality
// ============================================================
const PLANNING_INSIGHTS = [
  {
    condition: (d) => parseFloat(d.poverty_2023) > 30 && parseInt(d.poor_rice_farmers) > 500,
    insight: "This area has a high concentration of rice farms below 0.5 ha and may be prioritized for farm clustering or targeted rice support.",
    icon: "⚠️", level: "high"
  },
  {
    condition: (d) => parseFloat(d.poverty_2023) > 30 && parseInt(d.poor_corn_farmers) > 500,
    insight: "This area has a high concentration of corn farms below 0.5 ha and may be prioritized for farm clustering or targeted corn support.",
    icon: "⚠️", level: "high"
  },
  {
    condition: (d) => parseFloat(d.rice_yield_2023) < 3.0 && parseInt(d.rice_area_2023) > 1000,
    insight: "This area may require productivity-enhancing interventions for rice.",
    icon: "🌾", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.corn_yield_2023) < 2.5 && parseInt(d.corn_area_2023) > 500,
    insight: "This area may require productivity-enhancing interventions for corn.",
    icon: "🌽", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.rice_mechanization_level) < 30 && parseInt(d.rice_area_2023) > 1000,
    insight: "This area may be suitable for mechanization support in rice.",
    icon: "🚜", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.corn_mechanization_level) < 30 && parseInt(d.corn_area_2023) > 500,
    insight: "This area may be suitable for mechanization support in corn.",
    icon: "🚜", level: "moderate"
  },
  {
    condition: (d) => parseInt(d.irrigated_area) < 500 && parseInt(d.rice_area_2023) > 1000,
    insight: "This area may require irrigation or drought mitigation support.",
    icon: "💧", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.soil_fertility_stress_score) >= 55,
    insight: "High soil fertility stress. Prioritize field validation for low fertility, pH, NPK, and zinc constraints before selecting intervention packages.",
    icon: "Soil", level: "high"
  },
  {
    condition: (d) => parseFloat(d.soil_low_fertility_pct) >= 50 && parseFloat(d.soil_lab_area_ha) > 500,
    insight: "At least half of the soil-tested area is rated low fertility. Consider soil rehabilitation, nutrient management advisories, and organic matter support.",
    icon: "Soil", level: "high"
  },
  {
    condition: (d) => parseFloat(d.soil_acidic_pct) >= 50 && parseFloat(d.soil_acidic_area_ha) > 300,
    insight: "Acidic soil is a major constraint in the tested area. Check lime suitability, soil texture, and timing before fertilizer response programs.",
    icon: "Soil", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.soil_npk_multiple_low_pct) >= 25,
    insight: "Multiple NPK ratings are low in a substantial share of tested area. Balanced fertilizer recommendations may be more appropriate than single-nutrient support.",
    icon: "Soil", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.soil_zinc_deficient_pct) >= 25,
    insight: "Zinc deficiency appears in a substantial share of tested area. Validate micronutrient needs before rice or corn intensification support.",
    icon: "Soil", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.soil_rice_low_fertility_pct) >= 40 && parseFloat(d.poor_rice_farmers) > 300,
    insight: "Rice soil fertility constraints overlap with many small rice farms. This is a candidate for targeted rice nutrient management support.",
    icon: "Soil", level: "high"
  },
  {
    condition: (d) => parseFloat(d.soil_corn_low_fertility_pct) >= 40 && parseFloat(d.poor_corn_farmers) > 300,
    insight: "Corn soil fertility constraints overlap with many small corn farms. This is a candidate for targeted corn nutrient management support.",
    icon: "Soil", level: "high"
  },
  {
    condition: (d) => d.pest_disease_occurrence === "High",
    insight: "This area may require intensified pest surveillance and crop protection support.",
    icon: "🦠", level: "high"
  },
  {
    condition: (d) => parseFloat(d.rcpc_surveillance_priority_score) >= 60,
    insight: "RCPC records show high crop-protection surveillance priority. Inspect incident points and validate recent pest pressure, affected area, and response gaps with field teams.",
    icon: "RCPC", level: "high"
  },
  {
    condition: (d) => parseFloat(d.rcpc_response_gap_score) >= 45,
    insight: "RCPC records indicate a notable treatment or response gap. Check untreated affected area, action taken, and available crop-protection support before programming.",
    icon: "RCPC", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.rcpc_high_severity_records) >= 5,
    insight: "Multiple RCPC records show high severity or high infestation. Prioritize validation of the pest family, crop stage, and barangay cluster before recommending controls.",
    icon: "RCPC", level: "high"
  },
  {
    condition: (d) => parseFloat(d.rcpc_recent_affected_area_ha) >= 500,
    insight: "Recent RCPC affected area is substantial. Review whether rice, corn, HVC, or cassava incidents are driving the signal and align surveillance accordingly.",
    icon: "RCPC", level: "moderate"
  },
  {
    condition: (d) => d.asf_status === "Affected",
    insight: "Sanitized ASF laboratory aggregates show positive results here. Coordinate livestock biosecurity validation without exposing farmer identities.",
    icon: "🐖", level: "high"
  },
  {
    condition: (d) => parseFloat(d.asf_risk_score) >= 60,
    insight: "High ASF laboratory risk score. Prioritize veterinary validation, movement-control review, disinfection support, and restocking safeguards.",
    icon: "ASF", level: "high"
  },
  {
    condition: (d) => parseFloat(d.stunting) > 30 || parseFloat(d.underweight) > 20,
    insight: "This area shows elevated malnutrition indicators. Nutrition-sensitive agriculture programs are recommended.",
    icon: "🥗", level: "high"
  },
  // CRVA-based insights
  {
    condition: (d) => parseFloat(d.crva_index_rice) > 0.65,
    insight: "Very high climate risk vulnerability for rice production. Priority area for DA-AMIA climate-resilient agriculture (CRA) interventions and CRVA-based targeting.",
    icon: "🌡️", level: "high"
  },
  {
    condition: (d) => parseFloat(d.crva_index_rice) > 0.45 && parseFloat(d.crva_index_rice) <= 0.65,
    insight: "High climate risk vulnerability for rice. Consider climate-smart variety adoption, crop calendar adjustment, and insurance programs.",
    icon: "🌾", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.ac_index) < 0.25,
    insight: "Very low Adaptive Capacity — this municipality has limited ability to cope with climate shocks. Multi-capital capacity building (economic, physical, anticipatory) is urgently needed.",
    icon: "⚠️", level: "high"
  },
  {
    condition: (d) => parseFloat(d.hazard_flood) > 0.70 && parseFloat(d.hazard_typhoon) > 0.70,
    insight: "High combined exposure to both typhoon and flood hazards. Flood-resilient crop varieties and disaster preparedness programs should be prioritized.",
    icon: "🌊", level: "high"
  },
  {
    condition: (d) => parseFloat(d.hazard_landslide) > 0.65 || parseFloat(d.hazard_soil_erosion) > 0.65,
    insight: "High landslide or soil erosion susceptibility. Reforestation, slope stabilization, and contour farming practices are recommended for upland agriculture areas.",
    icon: "⛰️", level: "high"
  },
  {
    condition: (d) => parseFloat(d.sensitivity_rice) > 0.40,
    insight: "Rice climatic suitability is projected to decrease significantly by 2050 (RCP 8.5). Crop diversification and heat-tolerant variety deployment are recommended.",
    icon: "🔥", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.ac_anticipatory) < 0.20,
    insight: "Very low anticipatory capital. Farmer early warning system access, DRRM training, and mobile-based advisory services should be strengthened.",
    icon: "📡", level: "moderate"
  }
  ,
  {
    condition: (d) => parseFloat(d.prism_standing_crop_area) > 1500,
    insight: "Large PRiSM standing rice area remains in the field. Prioritize field monitoring, irrigation checks, and weather advisory coordination.",
    icon: "PRiSM", level: "high"
  },
  {
    condition: (d) => parseFloat(d.prism_upcoming_harvest_area) > 1500,
    insight: "High May-June harvest area is expected. Review dryer, warehouse, hauling, and buying station readiness.",
    icon: "PRiSM", level: "moderate"
  },
  {
    condition: (d) => Math.abs(parseFloat(d.prism_area_gap_vs_app_pct)) > 20,
    insight: "PRiSM detected rice area differs substantially from the app reference area. Validate municipal rice area records before final targeting.",
    icon: "PRiSM", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.prism_flood_damage_priority_score) >= 50,
    insight: "High PRiSM flood-damage priority. Validate field damage reports and prepare recovery support for flooded standing rice areas.",
    icon: "PRiSM Flood", level: "high"
  },
  {
    condition: (d) => parseFloat(d.prism_flooded_reproductive_ripening_ha) > 20,
    insight: "Flooding affected reproductive or ripening rice. This deserves near-term production-loss validation and crop insurance coordination.",
    icon: "PRiSM Flood", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.elnino_rice_risk_score) >= 50,
    insight: "High El Nino rice exposure. Coordinate irrigation scheduling, field validation, and advisory support for standing rice areas.",
    icon: "El Nino", level: "high"
  },
  {
    condition: (d) => parseFloat(d.elnino_resilience_priority_score) >= 58,
    insight: "High El Nino resilience package priority. Review climate exposure, farmer vulnerability, production constraints, and implementation gaps as one response package.",
    icon: "Package", level: "high"
  },
  {
    condition: (d) => parseFloat(d.elnino_resilience_implementation_gap_score) >= 55,
    insight: "Implementation gap is elevated. Check whether 2026-2027 plan items, procurement status, or encoded allocations are missing for this risk profile.",
    icon: "Plan", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.elnino_prism_standing_exposed_area) > 1000,
    insight: "Large PRiSM standing rice area overlaps with PAGASA dry-spell or drought concern. Prioritize monitoring for crop water stress.",
    icon: "El Nino", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.plans_2027_need_gap_score) >= 65,
    insight: "High planning need gap. This area has strong poverty, small-farm, or climate need relative to the extracted 2027 plan allocation.",
    icon: "Plans", level: "high"
  },
  {
    condition: (d) => parseFloat(d.fmr_inventory_count) >= 10,
    insight: "This area has a substantial FMR inventory. Use the FMR map layer to inspect project locations, status, influence area, and beneficiaries.",
    icon: "FMR", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.plans_fmr_2027_count) > 0 && parseFloat(d.fmr_inventory_count) > 0,
    insight: "Existing FMR inventory overlaps with extracted 2027 FMR plans. Check whether new projects extend coverage or duplicate already-served locations.",
    icon: "FMR", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.f2c2_cluster_count) >= 3,
    insight: "Multiple FCA/F2C2 clusters are present. Use the F2C2 cluster layer to review commodities, enterprise status, farmer membership, and cluster area.",
    icon: "F2C2", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.f2c2_farmer_members) >= 300 && (parseFloat(d.poor_rice_farmers) > 300 || parseFloat(d.poor_corn_farmers) > 300),
    insight: "FCA/F2C2 membership overlaps with many small rice or corn farms. This area is a candidate for cluster-based enterprise support and market linkage validation.",
    icon: "F2C2", level: "high"
  },
  {
    condition: (d) => parseFloat(d.abemis_total_projects) >= 25,
    insight: "ABEMIS shows a large infrastructure inventory here. Use grouped ABEMIS layers to validate project distribution by barangay, type, year, beneficiary, and cost.",
    icon: "ABEMIS", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.abemis_irrigation_projects) >= 5 && parseFloat(d.poor_rice_farmers) >= 300,
    insight: "ABEMIS irrigation or water-system investments overlap with many small rice farms. Check whether projects support current rice exposure and actual service areas.",
    icon: "ABEMIS", level: "high"
  },
  {
    condition: (d) => parseFloat(d.abemis_postharvest_projects) >= 3 && (parseFloat(d.poor_rice_farmers) + parseFloat(d.poor_corn_farmers)) >= 500,
    insight: "Postharvest or processing records overlap with small-farm concentration. Validate whether facilities address drying, storage, processing, or market-access bottlenecks.",
    icon: "ABEMIS", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.rsba_registry_count) >= 5000,
    insight: "A large RSBSA registry base is present. Use RSBSA indicators to target interventions, validate commodity mix, and check IMC coverage before allocating support.",
    icon: "RSBSA", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.rsba_fca_gap_pct) >= 80 && parseFloat(d.rsba_registry_count) >= 1000,
    insight: "Most RSBSA records are not tagged as FCA members. This area may need organizing, clustering, or F2C2 validation before enterprise-scale support.",
    icon: "RSBSA", level: "moderate"
  },
  {
    condition: (d) => parseFloat(d.rsba_4ps_count) + parseFloat(d.rsba_ip_count) + parseFloat(d.rsba_pwd_count) >= 500,
    insight: "RSBSA social-targeting records are substantial. Consider inclusion-sensitive delivery, registration validation, and beneficiary safeguards.",
    icon: "RSBSA", level: "high"
  },
  {
    condition: (d) => parseFloat(d.plans_projects_2027_budget) <= 0 && (parseFloat(d.poverty_2023) > 20 || parseFloat(d.elnino_rice_risk_score) > 40),
    insight: "No extracted 2027 plan allocation was found despite notable poverty or climate exposure. Check if projects are missing, unfunded, or encoded under another municipality.",
    icon: "Plans", level: "moderate"
  }
];

// ============================================================
// FACILITY CATEGORIES & TYPES
// Add new facility types here — the sidebar and map update automatically.
// Each category has a group key, label, color, and list of types.
// Each type has: key (matches facility_type in CSV), label, icon, color.
// ============================================================
const FACILITY_CATEGORIES = {
  rpc: {
    label: "Post-Production Centers",
    groupColor: "#1a6b3c",
    types: {
      RPC: { label: "Rice Processing Complex (RPC)", icon: "🏭", color: "#1a6b3c" }
    }
  },
  fmr: {
    label: "Farm-to-Market Roads",
    groupColor: "#7a4a18",
    types: {
      FMR: { label: "Farm-to-Market Road (FMR)", icon: "FMR", color: "#7a4a18" }
    }
  },
  f2c2: {
    label: "F2C2 / FCA Clusters",
    groupColor: "#256d3c",
    types: {
      F2C2: { label: "FCA/F2C2 Cluster", icon: "F2C2", color: "#256d3c" }
    }
  },
  abemis: {
    label: "ABEMIS Database",
    groupColor: "#4f46e5",
    types: {
      ABEMIS_FMR: { label: "ABEMIS FMR", icon: "FMR", color: "#7a4a18" },
      ABEMIS_IRRIGATION: { label: "ABEMIS Irrigation / Water", icon: "IRR", color: "#0284c7" },
      ABEMIS_POSTHARVEST: { label: "ABEMIS Postharvest / Processing", icon: "PH", color: "#d97706" },
      ABEMIS_PROTECTED_CULTIVATION: { label: "ABEMIS Protected Cultivation", icon: "PC", color: "#16a34a" },
      ABEMIS_FOOD_GARDEN: { label: "ABEMIS Food Gardens", icon: "FG", color: "#65a30d" },
      ABEMIS_LIVESTOCK: { label: "ABEMIS Livestock Facilities", icon: "LV", color: "#ea580c" },
      ABEMIS_OTHER: { label: "ABEMIS Other Infrastructure", icon: "ABI", color: "#4f46e5" }
    }
  },
  bswm: {
    label: "BSWM FertMap",
    groupColor: "#0f766e",
    types: {
      BSWM_FERTMAP: { label: "FertMap Soil Sample Points", icon: "pH", color: "#0f766e" }
    }
  },
  rcpc: {
    label: "RCPC Pest & Disease",
    groupColor: "#b91c1c",
    types: {
      RCPC_RICE: { label: "RCPC Rice Incidents", icon: "R", color: "#b91c1c" },
      RCPC_CORN: { label: "RCPC Corn Incidents", icon: "C", color: "#d97706" },
      RCPC_HVC: { label: "RCPC HVC Incidents", icon: "HV", color: "#7c3aed" },
      RCPC_CASSAVA: { label: "RCPC Cassava Incidents", icon: "CA", color: "#ea580c" }
    }
  }
  // Add more categories here freely, e.g.:
  // veterinary: { label: "Veterinary Stations", groupColor: "#7c3aed", types: { ... } }
};
