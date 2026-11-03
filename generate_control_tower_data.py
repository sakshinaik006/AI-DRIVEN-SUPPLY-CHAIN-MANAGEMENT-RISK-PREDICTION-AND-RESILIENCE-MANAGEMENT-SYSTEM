import pandas as pd
import json

suppliers = pd.read_parquet('data/synthetic/suppliers.parquet')
plants = pd.read_parquet('data/synthetic/plants.parquet')
warehouses = pd.read_parquet('data/synthetic/warehouses.parquet')
routes = pd.read_parquet('data/synthetic/routes.parquet')

fs = pd.read_parquet('data/processed/features_supplier_v1.parquet')
fp = pd.read_parquet('data/processed/features_manufacturing_v1.parquet')
fw = pd.read_parquet('data/processed/features_warehouse_v1.parquet')
fr = pd.read_parquet('data/processed/features_transport_v1.parquet')

scenarios = {
    '2025-04-15': {'name': 'Scenario 1: Normal Operations (Apr 15)', 'desc': 'All network nodes operating within safe baseline parameters'},
    '2025-08-15': {'name': 'Scenario 2: Typhoon & Supply Starvation (Aug 15)', 'desc': 'Severe climate disruption at coastal supplier cascading downstream to assembly and transit'},
    '2025-10-24': {'name': 'Scenario 3: Retail Stockout Surge (Oct 24)', 'desc': 'High consumer demand surge creating stockout risk at regional warehouses and upstream pull'}
}

prob_matrix = {
    '2025-04-15': {
        'default': 0.06
    },
    '2025-08-15': {
        'SUP001': 0.82, 'RT001': 0.75, 'PLT004': 0.74,
        'WH002': 0.48, 'WH003': 0.48, 'RT009': 0.44, 'RT010': 0.44,
        'default': 0.07
    },
    '2025-10-24': {
        'WH001': 0.78, 'RT006': 0.75, 'PLT001': 0.46, 'RT003': 0.44, 'SUP003': 0.35,
        'default': 0.08
    }
}

output_data = {'scenarios': scenarios, 'dates': list(scenarios.keys()), 'scenario_data': {}}

for dt in scenarios.keys():
    fs_dt = fs[fs['date'] == dt].set_index('entity_id')
    fp_dt = fp[fp['date'] == dt].set_index('entity_id')
    fw_dt = fw[fw['date'] == dt].set_index('entity_id')
    fr_dt = fr[fr['date'] == dt].set_index('entity_id')
    
    entities = []
    
    # 1. Suppliers
    for _, row in suppliers.iterrows():
        eid = row['entity_id']
        p = prob_matrix[dt].get(eid, prob_matrix[dt]['default'])
        lvl = 'High' if p >= 0.70 else ('Medium' if p >= 0.30 else 'Low')
        feat = fs_dt.loc[eid] if eid in fs_dt.index else None
        entities.append({
            'entity_id': eid,
            'name': row['name'],
            'type': 'supplier',
            'category': 'Supplier Risk',
            'country': row['country'],
            'city': row['city'],
            'latitude': float(row['latitude']),
            'longitude': float(row['longitude']),
            'tier': int(row['tier']),
            'probability': p,
            'level': lvl,
            'reliability_score': round(1.0 - (p * 0.8), 2),
            'lead_time_days': int(row['base_lead_time_days']),
            'single_source': bool(row['single_source_flag']),
            'delay_7d_avg': float(feat['supplier_delay_7d_avg']) if feat is not None else 0.0,
            'rain_7d_sum': float(feat['rain_7d_sum']) if feat is not None else 0.0,
            'news_tone': float(feat['news_tone_14d_trend']) if feat is not None else 0.0,
            'connected_entities': ['RT001'] if eid == 'SUP001' else (['RT002'] if eid == 'SUP002' else (['RT003'] if eid == 'SUP003' else (['RT004'] if eid == 'SUP004' else (['RT005'] if eid == 'SUP008' else []))))
        })

    # 2. Plants
    for _, row in plants.iterrows():
        eid = row['entity_id']
        p = prob_matrix[dt].get(eid, prob_matrix[dt]['default'])
        lvl = 'High' if p >= 0.70 else ('Medium' if p >= 0.30 else 'Low')
        feat = fp_dt.loc[eid] if eid in fp_dt.index else None
        planned_cap = int(row['capacity_units_per_day'])
        ratio = float(feat['production_ratio_7d_avg']) if feat is not None else (0.65 if lvl == 'High' else (0.85 if lvl == 'Medium' else 1.0))
        if lvl == 'High': ratio = 0.65
        entities.append({
            'entity_id': eid,
            'name': row['name'],
            'type': 'plant',
            'category': 'Manufacturing Risk',
            'country': row['country'],
            'city': row['city'],
            'latitude': float(row['latitude']),
            'longitude': float(row['longitude']),
            'capacity_planned': planned_cap,
            'actual_output': int(planned_cap * ratio),
            'production_ratio': ratio,
            'probability': p,
            'level': lvl,
            'delay_7d_avg': float(feat['delivery_delay_7d_avg']) if feat is not None else 0.0,
            'rain_7d_sum': float(feat['rain_7d_sum']) if feat is not None else 0.0,
            'connected_entities': ['WH001', 'RT006'] if eid == 'PLT001' else (['WH005', 'RT007'] if eid == 'PLT002' else (['WH004', 'RT008'] if eid == 'PLT003' else ['WH002', 'WH003', 'RT009', 'RT010']))
        })

    # 3. Warehouses
    for _, row in warehouses.iterrows():
        eid = row['entity_id']
        p = prob_matrix[dt].get(eid, prob_matrix[dt]['default'])
        lvl = 'High' if p >= 0.70 else ('Medium' if p >= 0.30 else 'Low')
        feat = fw_dt.loc[eid] if eid in fw_dt.index else None
        safety_stock = int(row['safety_stock_units'])
        stock_days = float(feat['stock_days_cover']) if feat is not None else 6.0
        if lvl == 'High': stock_days = 2.4
        elif lvl == 'Medium': stock_days = 4.2
        curr_inv = int(safety_stock * (stock_days / 7.0))
        entities.append({
            'entity_id': eid,
            'name': row['name'],
            'type': 'warehouse',
            'category': 'Warehouse Stockout',
            'country': row['country'],
            'city': row['city'],
            'latitude': float(row['latitude']),
            'longitude': float(row['longitude']),
            'safety_stock': safety_stock,
            'inventory_level': curr_inv,
            'stock_days_cover': stock_days,
            'demand_7d_avg': float(feat['demand_7d_avg']) if feat is not None else 1020.0,
            'probability': p,
            'level': lvl,
            'connected_entities': ['PLT001', 'RT006'] if eid == 'WH001' else (['PLT004', 'RT010'] if eid == 'WH002' else (['PLT004', 'RT009'] if eid == 'WH003' else (['PLT003', 'RT008'] if eid == 'WH004' else ['PLT002', 'RT007'])))
        })

    # 4. Routes
    for _, row in routes.iterrows():
        eid = row['entity_id']
        p = prob_matrix[dt].get(eid, prob_matrix[dt]['default'])
        lvl = 'High' if p >= 0.70 else ('Medium' if p >= 0.30 else 'Low')
        feat = fr_dt.loc[eid] if eid in fr_dt.index else None
        entities.append({
            'entity_id': eid,
            'name': f"Corridor {eid} ({row['origin_city']} -> {row['destination_city']})",
            'type': 'route',
            'category': 'Transportation Delay',
            'route_type': row['route_type'],
            'origin_id': row['origin_id'],
            'destination_id': row['destination_id'],
            'shipping_mode': row['shipping_mode'],
            'scheduled_days': int(row['scheduled_days']),
            'distance_km': float(row['distance_km']),
            'latitude': float(row['latitude']),
            'longitude': float(row['longitude']),
            'probability': p,
            'level': lvl,
            'delay_7d_avg': float(feat['delivery_delay_7d_avg']) if feat is not None else 0.0,
            'rain_7d_sum': float(feat['rain_7d_sum']) if feat is not None else 0.0,
            'port_news_tone': float(feat['port_news_tone_14d']) if feat is not None else 0.0,
            'connected_entities': [row['origin_id'], row['destination_id']]
        })

    high_count = sum(1 for e in entities if e['level'] == 'High')
    med_count = sum(1 for e in entities if e['level'] == 'Medium')
    low_count = sum(1 for e in entities if e['level'] == 'Low')
    avg_p = sum(e['probability'] for e in entities) / len(entities)
    
    cat_summary = {}
    for cat in ['Supplier Risk', 'Manufacturing Risk', 'Warehouse Stockout', 'Transportation Delay']:
        cat_entities = [e for e in entities if e['category'] == cat]
        cat_high = sum(1 for e in cat_entities if e['level'] == 'High')
        cat_med = sum(1 for e in cat_entities if e['level'] == 'Medium')
        cat_p = sum(e['probability'] for e in cat_entities) / max(len(cat_entities), 1)
        cat_summary[cat] = {
            'level': 'High' if cat_high > 0 else ('Medium' if cat_med > 0 else 'Low'),
            'affected_count': cat_high + cat_med,
            'total_count': len(cat_entities),
            'avg_probability': round(cat_p, 3)
        }
    
    recs = []
    for e in entities:
        if e['level'] in ['High', 'Medium']:
            if e['type'] == 'supplier':
                recs.append({
                    'id': f"REC-{e['entity_id']}",
                    'category': 'Supplier Risk',
                    'entity_id': e['entity_id'],
                    'entity_name': e['name'],
                    'priority': 'Critical' if e['level'] == 'High' else 'Moderate',
                    'action': f"Activate secondary dual-source supplier (Berlin/Ningbo) and buffer inventory for {e['entity_id']}.",
                    'status': 'Action Required',
                    'mitigation_effect': 'Reduces supplier disruption probability from 82% to 25%',
                    'reason': f"High failure risk ({int(e['probability']*100)}%) due to climate storm and rolling delivery lag"
                })
            elif e['type'] == 'plant':
                recs.append({
                    'id': f"REC-{e['entity_id']}",
                    'category': 'Manufacturing Risk',
                    'entity_id': e['entity_id'],
                    'entity_name': e['name'],
                    'priority': 'Critical' if e['level'] == 'High' else 'Moderate',
                    'action': f"Rebalance assembly schedule and shift batch production from {e['entity_id']} to auxiliary plant PLT001.",
                    'status': 'Action Required',
                    'mitigation_effect': 'Prevents line stoppage; recovers production throughput to 94%',
                    'reason': f"Assembly starvation due to delayed parts from upstream inbound routes"
                })
            elif e['type'] == 'warehouse':
                recs.append({
                    'id': f"REC-{e['entity_id']}",
                    'category': 'Warehouse Risk',
                    'entity_id': e['entity_id'],
                    'entity_name': e['name'],
                    'priority': 'Critical' if e['level'] == 'High' else 'Moderate',
                    'action': f"Increase safety stock coverage buffer by +25% and trigger emergency cross-dock rebalancing for {e['entity_id']}.",
                    'status': 'Action Required',
                    'mitigation_effect': 'Restores days-of-supply inventory cover to safe zone (>6 days)',
                    'reason': f"Stockout risk ({int(e['probability']*100)}%) due to demand surge and thin safety buffer"
                })
            elif e['type'] == 'route':
                recs.append({
                    'id': f"REC-{e['entity_id']}",
                    'category': 'Transportation Risk',
                    'entity_id': e['entity_id'],
                    'entity_name': e['name'],
                    'priority': 'Critical' if e['level'] == 'High' else 'Moderate',
                    'action': f"Reroute critical express shipments along corridor {e['entity_id']} to alternative air cargo route.",
                    'status': 'Action Required',
                    'mitigation_effect': 'Avoids 4.5 days maritime port dwell delay',
                    'reason': f"Corridor bottleneck and adverse weather advisory"
                })
    
    base_trend_p = avg_p
    trend = [
        {'day': 'Day -6', 'network_risk': max(0.04, round(base_trend_p * 0.72, 3))},
        {'day': 'Day -5', 'network_risk': max(0.04, round(base_trend_p * 0.78, 3))},
        {'day': 'Day -4', 'network_risk': max(0.05, round(base_trend_p * 0.85, 3))},
        {'day': 'Day -3', 'network_risk': max(0.05, round(base_trend_p * 0.91, 3))},
        {'day': 'Day -2', 'network_risk': max(0.05, round(base_trend_p * 0.96, 3))},
        {'day': 'Day -1', 'network_risk': max(0.06, round(base_trend_p * 0.98, 3))},
        {'day': 'Today (Day 0)', 'network_risk': round(base_trend_p, 3)},
        {'day': 'Forecast (+7d)', 'network_risk': round(min(0.95, base_trend_p * 1.08 if high_count > 0 else base_trend_p), 3)}
    ]
    
    output_data['scenario_data'][dt] = {
        'prediction_horizon': 'Next 7 Days',
        'last_data_update': f'{dt} 08:00 UTC',
        'total_suppliers': len(suppliers),
        'total_plants': len(plants),
        'total_warehouses': len(warehouses),
        'total_routes': len(routes),
        'total_entities': len(entities),
        'overall_network_score': round(avg_p, 3),
        'overall_health': 'Stable / Normal' if high_count == 0 and med_count <= 2 else ('At Risk - Critical Attention Needed' if high_count >= 2 else 'Guarded / Moderate Risk'),
        'high_risk_count': high_count,
        'medium_risk_count': med_count,
        'low_risk_count': low_count,
        'category_summary': cat_summary,
        'entities': entities,
        'recommendations': recs,
        'risk_trend': trend,
        'top_alerts': [
            {
                'entity_id': e['entity_id'],
                'name': e['name'],
                'category': e['category'],
                'level': e['level'],
                'probability': e['probability'],
                'summary': next((r['action'] for r in recs if r['entity_id'] == e['entity_id']), ('Elevated conditional disruption probability detected' if e['level'] != 'Low' else 'Baseline telemetry nominal.')),
                'recommended_action': next((r['action'] for r in recs if r['entity_id'] == e['entity_id']), 'Maintain continuous telemetry monitoring.')
            }
            for e in (sorted([e for e in entities if e['level'] in ['High', 'Medium']], key=lambda x: x['probability'], reverse=True)[:3] if any(e['level'] in ['High', 'Medium'] for e in entities) else sorted(entities, key=lambda x: x['probability'], reverse=True)[:3])
        ],
        'alerts': [
            {'id': f"ALT-{e['entity_id']}", 'severity': e['level'], 'message': f"{e['name']} ({e['entity_id']}) breached failure threshold with {int(e['probability']*100)}% probability."}
            for e in entities if e['level'] == 'High'
        ] + [
            {'id': f"ALT-{e['entity_id']}", 'severity': e['level'], 'message': f"{e['name']} ({e['entity_id']}) elevated risk detected ({int(e['probability']*100)}%)."}
            for e in entities if e['level'] == 'Medium'
        ]
    }

with open('frontend/public/control_tower_data.json', 'w') as f:
    json.dump(output_data, f, indent=2)

print('control_tower_data.json generated successfully!')
