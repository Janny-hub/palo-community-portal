. Phase 5: Spatial Mapping, Geocoding, & Statistical Analytics
To transform raw community assessment data into high-impact public health intelligence, assessment teams must integrate spatial visualization (GIS) with advanced statistical modeling.
6.1 Spot Mapping & Mobile Address Geocoding Protocol
•	Step 1: Participatory BHW Spot Mapping: Mobilize BHWs to draw baseline community spot maps capturing every residential structure, water source, and health facility.
•	Step 2: GPS Mobile Geocoding: Utilizing handheld GPS devices or mobile survey software (KoboToolbox), capture exact latitude and longitude coordinates (x, y) for every surveyed household.
•	Step 3: GIS Layering: Upload geocoded survey points into QGIS or ArcGIS to convert static addresses into spatial shapefiles.
6.2 Multi-Layer GIS Visualization Framework
•	Layer 1: Disease Hotspot Mapping: Apply Kernel Density Estimation (KDE) to plot heatmaps of chronic hypertension, diabetes, and active TB clusters across Puroks.
•	Layer 2: Environmental SDOH Overlay: Superimpose disease hot spots over layers of unsafe water sources (Level I/unprotected), flood risk zones, and open waste dumping areas.
•	Layer 3: Food Desert Identification: Perform buffer analysis (500-meter walking radius) around fresh food markets versus sari-sari store density to map food deserts against childhood malnutrition.
•	Layer 4: Catchment Isochrone Modeling: Generate 15-minute and 30-minute travel time contours around the BHS/RHU to identify geographically isolated and disadvantaged areas (GIDAs).
6.3 Statistical Analysis & Advanced Analytical Modeling Plan
A. Descriptive Analysis (Measuring the Social Gradient)
Cross-tabulate clinical health outcomes across income quintiles, educational attainment levels, and geographic zones. Calculate Odds Ratios (OR) and Relative Risks (RR) to quantify how disease burdens increase along lower socio-economic tiers.
B. Advanced Multivariate Modeling (Factor Analysis & Latent Class Analysis)
Social determinants rarely occur in isolation; compounding social risks produce exponential health detriments. Two advanced statistical techniques are deployed:
•	1. Principal Component & Factor Analysis: Collapse correlated environmental and economic variables (e.g., wall material, toilet type, income, water level) into latent factor scores (e.g., Household Deprivation Index) to measure overall structural vulnerability.
•	2. Latent Class Analysis (LCA): Group households into discrete vulnerability classes based on overlapping social risks (e.g., Class 1: High Income/High Access; Class 2: Severe Food Insecurity + Housing Instability + No Piped Water). Model the direct probability of chronic disease prevalence per class.
Statistical Method	Input Variables (Survey/GIS)	Target Public Health Output
Descriptive Cross-Tabulation & Odds Ratios	Income Quintiles × Hypertension / Diabetes Prevalence	Quantifies the slope of the social gradient in health across income tiers.
Factor Analysis (PCA)	Housing materials, WASH level, Income, Cooking fuel	Generates a composite 'Barangay Socio-Economic Vulnerability Index'.
Latent Class Analysis (LCA)	Co-occurring food insecurity, housing instability, distance barrier	Identifies multi-risk household clusters requiring integrated LGU social protection.
