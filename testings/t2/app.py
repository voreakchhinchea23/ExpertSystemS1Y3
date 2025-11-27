from flask import Flask, render_template, request
import json

app = Flask(__name__)

# Load facts and rules
with open('facts.json', encoding='utf-8') as f:
    facts = json.load(f)
with open('rules.json', encoding='utf-8') as f:
    rules = json.load(f)

def set_fact(fid, val=True):
    for f in facts:
        if f["id"] == fid:
            f["value"] = val

def get_fact(fid):
    for f in facts:
        if f["id"] == fid:
            return f["value"]
    return False

def reset_facts():
    for f in facts:
        f["value"] = False

def run_expert_system():
    recommendations = []
    for rule in rules:
        if all(get_fact(cond) for cond in rule["conditions"]):
            recipe_name = next(f["description"].split(": ", 1)[1] for f in facts if f["id"] == rule["conclusion"])
            recommendations.append({
                "recipe": recipe_name,
                "reason": rule["explain"]
            })
            set_fact(rule["conclusion"])
    return recommendations

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        reset_facts()
        selected = request.form.getlist('ing')  # works with Select2!
        for ing in selected:
            set_fact(ing)
        
        results = run_expert_system()
        if not results:
            results = [{"recipe": "No recipe matches", "reason": "Try adding more ingredients"}]
        return render_template('result.html', results=results)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)