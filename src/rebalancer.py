import pandas as pd

def generate_transfer_plan(forecast_df, inventory_df, cost_df, threshold=0.2, penalty_per_unit=10):
    suggestions = []

    for sku in forecast_df['SKU'].unique():
        sku_forecast = forecast_df[forecast_df['SKU'] == sku]
        sku_inventory = inventory_df[inventory_df['SKU'] == sku]

        # Ensure Current_Stock is coming from inventory_df
        merged = pd.merge(
            sku_forecast,
            sku_inventory[['SKU', 'Zone', 'Current_Stock']],
            on=['SKU', 'Zone'],
            how='left'
        )

        if merged.empty:
            continue

        merged['Gap'] = merged['Current_Stock_y'] - merged['Forecast_Quantity']

        avg_forecast = merged['Forecast_Quantity'].mean()

        def get_status(gap):
            if gap > threshold * avg_forecast:
                return 'Overstock'
            elif gap < -threshold * avg_forecast:
                return 'Understock'
            else:
                return 'Balanced'

        merged['Status'] = merged['Gap'].apply(get_status)

        overstocked = merged[merged['Status'] == 'Overstock']
        understocked = merged[merged['Status'] == 'Understock']

        for _, under in understocked.iterrows():
            under_zone = under['Zone']
            sku_understock_qty = abs(under['Gap'])

            candidates = []

            for _, over in overstocked.iterrows():
                over_zone = over['Zone']
                available_qty = over['Gap']

                if available_qty <= 0 or over_zone == under_zone:
                    continue

                cost_row = cost_df[
                    (cost_df['From'] == over_zone) & (cost_df['To'] == under_zone)
                ]

                if cost_row.empty:
                    continue

                transport_cost = cost_row['Transport_Cost'].values[0]
                transfer_qty = min(available_qty, sku_understock_qty)

                avoided_loss = penalty_per_unit * transfer_qty
                net_saving = avoided_loss - transport_cost

                candidates.append({
                    'SKU': sku,
                    'From': over_zone,
                    'To': under_zone,
                    'Quantity': int(round(transfer_qty)),
                    'Transport_Cost': float(transport_cost),
                    'Avoided_Loss': float(avoided_loss),
                    'Net_Saving': float(net_saving),
                    'Estimated_Savings': float(net_saving),
                    'Reason': 'Overstock-Understock Gap'
                })

            if candidates:
                best = sorted(candidates, key=lambda x: x['Transport_Cost'])[0]
                suggestions.append(best)

    return suggestions



def save_transfer_plan(suggestions, output_path='outputs/transfer_plan.csv'):
    if not suggestions:
        print("\n🚫 No transfer suggestions generated.")
        return

    transfer_df = pd.DataFrame(suggestions)
    transfer_df.to_csv(output_path, index=False)
    print(f"\n✅ Transfer plan saved to: {output_path}")


def main():
    # Load data
    forecast_df = pd.read_csv('outputs/forecasts.csv')
    inventory_df = pd.read_csv('data/inventory.csv')
    cost_df = pd.read_csv('data/cost_matrix.csv')

    print("📊 Forecast Data:")
    print(forecast_df.head())

    print("\n📦 Inventory Data:")
    print(inventory_df.head())

    print("\n💰 Cost Matrix:")
    print(cost_df.head())

    # Generate plan
    suggestions = generate_transfer_plan(forecast_df, inventory_df, cost_df)

    # Save plan
    save_transfer_plan(suggestions)


if __name__ == "__main__":
    main()
