import pandas as pd

def generate_transfer_plan(forecast_df, inventory_df, cost_df, threshold=0.2):
    suggestions = []

    for sku in forecast_df['SKU'].unique():
        sku_forecast = forecast_df[forecast_df['SKU'] == sku]
        sku_inventory = inventory_df[inventory_df['SKU'] == sku]

        merged = pd.merge(sku_forecast, sku_inventory, on=['SKU', 'Zone'])

        # Define stock status
        merged['Gap'] = merged['Current_Stock'] - merged['Forecast_Quantity']
        merged['Status'] = merged['Gap'].apply(
            lambda x: 'Overstock' if x > threshold * merged['Forecast_Quantity'].mean()
            else 'Understock' if x < -threshold * merged['Forecast_Quantity'].mean()
            else 'Balanced'
        )

        overstocked = merged[merged['Status'] == 'Overstock']
        understocked = merged[merged['Status'] == 'Understock']

        for _, under in understocked.iterrows():
            sku_understock_qty = abs(under['Gap'])

            # Sort overstock zones by transport cost
            candidates = []
            for _, over in overstocked.iterrows():
                available_qty = over['Gap']
                if available_qty <= 0:
                    continue

                cost_row = cost_df[
                    (cost_df['From'] == over['Zone']) &
                    (cost_df['To'] == under['Zone'])
                ]
                if cost_row.empty:
                    continue

                cost = cost_row['Transport_Cost'].values[0]
                transfer_qty = min(available_qty, sku_understock_qty)

                candidates.append({
                    'from': over['Zone'],
                    'to': under['Zone'],
                    'sku': sku,
                    'quantity': round(transfer_qty),
                    'cost': cost,
                    'reason': 'Overstock-Understock Gap'
                })

            # Pick cheapest route
            if candidates:
                best = sorted(candidates, key=lambda x: x['cost'])[0]
                suggestions.append(best)

    return suggestions
def save_transfer_plan(suggestions, output_path='outputs/transfer_plan.csv'):
    if not suggestions:
        print("No transfer suggestions generated.")
        return

    transfer_df = pd.DataFrame(suggestions)
    transfer_df.to_csv(output_path, index=False)
    print(f"Transfer plan saved to: {output_path}")
    
    
def main():
    # Load necessary data
    forecast_df = pd.read_csv('outputs/forecasts.csv')
    inventory_df = pd.read_csv('data/inventory.csv')
    cost_df = pd.read_csv('data/cost_matrix.csv')

    # Generate transfer plan
    suggestions = generate_transfer_plan(forecast_df, inventory_df, cost_df)

    # Save the transfer plan
    save_transfer_plan(suggestions)
    
    

if __name__ == "__main__":
    main()