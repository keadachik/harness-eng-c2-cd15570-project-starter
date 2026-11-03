Analysis results with evidence from the inventory and vehicle-history datasets for Cedar Lane Motors:

1. Dataset structure: 
- Inventory has 240 vehicles with detailed attributes including price_usd, horsepower, and condition (mostly used vehicles, 210 used vs 30 new).
- Vehicle-history data covers 48 rows of model-year summaries with avg_annual_repair_cost_usd and powertrain type among other metrics.

2. Numeric summaries:
- Inventory price_usd ranges from about $14,100 to $60,600 with an average near $35,000.
- Inventory horsepower ranges from 178 to 390 hp with a mean around 276 hp.
- Average annual repair cost in history data ranges from $249 to $846, averaging approximately $558.

3. Scatter plot of horsepower vs. price in inventory vehicles:
- There is a strong positive correlation (r=0.708) between horsepower and price.
- Higher horsepower vehicles tend to be priced higher, indicating a typical performance-price trade-off.

4. Bar chart of average annual repair cost by powertrain from history data:
- Average repair costs vary by powertrain type:
  - Plug-in Hybrid: $674 (highest repair cost)
  - Gasoline: $607
  - Electric: $530
  - Hybrid: $457 (lowest repair cost)
- Hybrid powertrains exhibit the lowest average repair cost, followed by electric. Plug-in hybrids show the highest costs on average.

Findings:
- A clear pattern links higher performance (horsepower) with higher pricing in inventory vehicles, reflecting typical market valuation for enhanced power.
- Ownership cost patterns by powertrain indicate that hybrids and electric vehicles may offer lower average repair costs compared to gasoline and plug-in hybrid powertrains, relevant for cost-conscious buyers.
- The majority of inventory is used, which should be considered alongside vehicle condition in ownership cost assessments.

Limitations: 
- Correlations like horsepower-price do not imply causation. Other factors like brand, model, and features affect pricing.
- Repair cost averages by powertrain come from historical model summaries and may not fully reflect individual vehicle conditions or regional service cost variations.

This analysis provides associative insights into performance, price, vehicle condition, and ownership cost trade-offs, without making specific recommendations. Would you like me to explore any specific segments or details next?
