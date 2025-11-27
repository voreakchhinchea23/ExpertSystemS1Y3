from flask import Flask, render_template, request
import json

app = Flask(__name__)

# Load Facts & Rules
with open('facts.json', encoding='utf-8') as f:
    FACTS = json.load(f)

with open('rules.json', encoding='utf-8') as f:
    RULES = json.load(f)

def recommend_phones(budget, camera_priority, battery_priority, gaming_priority):
    weights = RULES['priority_weights']
    importance = RULES['feature_importance']
    bonus_rules = RULES['bonus_rules']

    scored_phones = []

    for phone in FACTS:
        if phone['price'] > budget:
            continue  # Hard rule: never recommend over budget

        # Calculate base score using weighted priorities
        score = 0
        score += phone['camera']  * importance['camera'][camera_priority]  * weights[camera_priority]
        score += phone['battery'] * importance['battery'][battery_priority] * weights[battery_priority]
        score += phone['gaming']  * importance['gaming'][gaming_priority]   * weights[gaming_priority]

        # Apply bonus rules
        explanation = []
        for rule in bonus_rules:
            if rule['condition'] == "price <= budget * 0.7" and phone['price'] <= budget * 0.7:
                score += rule['bonus']
                explanation.append(rule['reason'])
            elif rule['condition'] == "price <= budget * 0.85" and phone['price'] <= budget * 0.85:
                score += rule['bonus']
                explanation.append(rule['reason'])

        phone_with_details = phone.copy()
        phone_with_details['score'] = round(score, 2)
        phone_with_details['explanation'] = " | ".join(explanation) if explanation else "Matches your needs"

        scored_phones.append(phone_with_details)

    # Sort and return top N
    scored_phones.sort(key=lambda x: x['score'], reverse=True)
    return scored_phones[:RULES['final_selection']['max_recommendations']]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        budget = int(request.form['budget'])
        camera = request.form['camera']
        battery = request.form['battery']
        gaming = request.form['gaming']

        recommendations = recommend_phones(budget, camera, battery, gaming)

        return render_template('result.html',
                               recommendations=recommendations,
                               budget=budget)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)