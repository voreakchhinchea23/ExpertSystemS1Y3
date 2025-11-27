# -----------------------------
# File: app.py
# -----------------------------
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
import json
import os
import tempfile
import importlib.util
import datetime
from jsonschema import validate, ValidationError

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(APP_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# -----------------------------
# JSON Schemas (loaded from external file)
# -----------------------------

SCHEMAS_FILE = os.getenv(
    "SCHEMAS_FILE",
    r"schemas\\schemas.py"
)

def _load_schemas_from_file(path: str):
    """Dynamically load facts/rules schemas from a python file.
    Expert globals named `facts_array_schema` and `rules_array_schema.`
    """
    spec = importlib.util.spec_from_file_location("external_schemas", path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"Cannot load shemas module from: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module) # type: ignore[attr-defined]
    try:
        return module.facts_array_schema, module.rules_array_schema
    except ArithmeticError as e:
        raise AttributeError(
            "schemas.py must expose 'facts_array_schema' and 'rules_array_schema'!"
        ) from e
        
try:
    facts_array_schema, rules_array_schema = _load_schemas_from_file(SCHEMAS_FILE)
except Exception as e:
    raise RuntimeError(
        f"Failed to load Json Schemas from '{SCHEMAS_FILE}' : {e}.\n"
        "Set SCHEMAS_FILE environment variable to override this path."
    )
    
# -----------------------------
# Helpers
# -----------------------------

def data_path(filename: str) -> str:
    return os.path.join(DATA_DIR, filename)

def load_json(filename: str):
    path = data_path(filename)
    if(os.path.exists(path)):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    raise FileNotFoundError(f"Required file not found: {path}")

def write_json(filename: str, payload):
    path = data_path(filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(path), prefix="._", suffix=".json")
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as tmp:
            json.dump(payload, tmp, ensure_ascii=False, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_path, path)
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass

def error_payload(e: ValidationError, filelabel: str):
    return {
        "file": filelabel,
        "error": e.message,
        "path": list(e.path),
        "schema_path": list(e.schema_path)
    }
    
def clamp01(x) -> float:
    try:
        return max(0.0, min(0.1, float(x)))
    except Exception:
        return 0.0
    
# -----------------------------
# Load facts/rules/taxonomy
# -----------------------------

try:
    facts = load_json("facts.json")
    rules = load_json("rules.json")
    taxonomy = load_json("taxonomy.json")
except FileNotFoundError as e:
    print(f"ERROR: {e}")
    print("Please ensure data/facts.json, data/rules.json, and data/taxonomy.json exist.")
    raise

# Validate on startup
try:
    validate(instance=facts, schema=facts_array_schema)
    validate(instance=rules, schema=rules_array_schema)
except ValidationError as e:
    print(f"ERROR: Data validation failed: {e.message}")
    raise

PARENT = taxonomy.get("parent", {})
FACT_VALUE = {f["id"]: bool(f.get("value", False)) for f in facts}

# -----------------------------
# Taxonomy helpers
# -----------------------------

def ancestors(concept: str):
    seen = set()
    cur = concept
    while cur in PARENT and PARENT[cur] not in seen:
        parent = PARENT[cur]
        seen.add(parent)
        yield parent
        cur = parent

def expand_observations(obs_conf: dict) -> dict:
    if not PARENT:
        return obs_conf
    expanded = dict(obs_conf)
    for fid, c in list(obs_conf.items()):
        for anc in ancestors(fid):
            expanded[anc] = max(expanded.get(anc, 0,0), c)
    return expanded

def evaluate_rule(rule: dict, obs_conf: dict):
    cond_ids = rule.get("conditions", [])
    if not cond_ids:
        return (False, 0.0)
    
    cond_scores = []
    for cid in cond_ids:
        c = clamp01(obs_conf.get(cid, 0.0))
        if c <= 0.0:
            return (False, 0.0)
        cond_scores.append(c)
        
    base = min(cond_scores)
    cf = clamp01(rule.get("certainty", 1.0))
    return (True, base * cf)

# -----------------------------
# Flask app & routes
# -----------------------------

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")


# ------ Health & JSON endpoints ------

@app.get("/health")
def health():
    try:   
        mtime = os.path.getmtime(SCHEMAS_FILE)
        schema_time = datetime.datetime.fromtimestamp(mtime).isoformat()
    except Exception:
        schema_time = "unavailable"
    return jsonify({
        "status" : "ok",
        "schemas_file" : SCHEMAS_FILE,
        "schemas_mtime" : schema_time,
        "facts_count": len(facts),
        "rules_count": len(rules)
    })
    
@app.get("/facts.json")
def get_facts_json():
    return jsonify(facts)

@app.get("/rules.json")
def get_rules_json():
    return jsonify(rules)

@app.route("/validate", methods=["GET", "POST"])
def validate_payloads():
    if request.method == "GET":
        return jsonify({
            "usage": "POST JSON with 'facts' and/or 'rules' to validate.",
            "schemas" : ["facts_array_schema", "rules_array_schema"]
        })
        
    payload = request.get_json(force=True, silent=True) or {}
    errors = []
    
    if "facts" in payload:
        try:
            validate(payload["facts"], facts_array_schema)
        except ValidationError as e:
            errors.append(error_payload(e, "facts"))
            
    if "rules" in payload:
        try:
            validate(payload("rules"), rules_array_schema)
        except ValidationError as e:
            errors.append(error_payload(e, "rules"))
            
    return jsonify({"valid": len(errors) == 0, "errors": errors})

@app.route("/infer", methods=["GET", "POST"])
def infer():
    if request.method == "GET":
        facts_param = request.args.get("facts", "")
        weights_param = request.args.get("weights", "")
        use_true_facts = request.args.get("useTrueFacts", "false").lower() == "true"
        
        observed_ids = set(f.strip() for f in facts_param.split(",") if f.strip())
        weights = {}
        if weights_param:
            for pair in weights_param.split(","):
                if ":" in pair:
                    fid, conf = pair.split(":", 1)
                    try:
                        weights[fid.strip()] = float(conf.strip())
                    except ValueError:
                        pass
        else:
            payload = request.get_json(force=True, silent=True) or {}
            observed_ids = set(payload.get("facts", []))
            weights = payload.get("weights", {})
            use_true_facts = bool(payload.get("useTrueFacts", False))
            
        if use_true_facts:
            observed_ids.update([fid for fid, val in FACT_VALUE.items() if val is True])
            
        obs_conf = {}
        for fid in observed_ids:
            obs_conf[fid] = clamp01(weights.get(fid, 1.0))
            
        obs_conf = expand_observations(obs_conf)
        
        fired = []
        for rule in rules:
            fires, score = evaluate_rule(rule, obs_conf)
            if fires and score > 0.0:
                fired.append({
                    "rule": rule["id"],
                    "conclusion": rule["conclusion"],
                    "score": round(score, 3),
                    "explain": rule.get("explain", ""),
                    "conditions": rule.get("conditions",[])
                })
                
        aggregate = {}
        for r in fired:
            k = r["condition"]
            aggregate[k] = max(aggregate.get(k, 0.0), r["score"])
            
        ranked = sorted(
            [{"conclusion": k, "score":round(v,3)} for k, v in aggregate.items()],
            key=lambda x: x["score"],
            reverse=True
        )
        
        return jsonify({
            "matched_rules":fired,
            "ranked_conclusions": ranked,
            "observations": [{"id": k, "confidence": v} for k,v in sorted(obs_conf.items())]
        })            
        
# -----------------------------
# HTML UI - CRUD for Facts & RUles (+ Taxonomy view)
# -----------------------------

@app.route("/")
def home():
    return redirect(url_for("facts_list"))

# ----- Facts -----

@app.get("/facts")
def facts_list():
    return render_template("facts_list.html", facts=facts)

@app.route("/facts/new", methods=["GET", "POST"])
def facts_new():
    if request.method == "POST":
        fid = (request.form.get("id") or "").strip()
        description = (request.form.get("description") or "").strip()
        value = request.form.get("value") == "on"
        tags_raw = request.form.get("tags") or ""
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        
        if not fid:
            flash("ID is required", "danger")
            return render_template("fact_form.html", mode="new", fact=None)
        if any(f.get("id") == fid for f in facts):
            flash(f"Fact id '{fid}' already exists", "danger")
            return render_template("fact_form.html", mode="new", fact=None)
        
        new_item = {"id": fid, "description": description, "value": bool(value), "tags": tags}
        new_facts = facts + [new_item]
        try:
            validate(new_facts, facts_array_schema)
            write_json("facts.json", new_facts)
        except ValidationError as e:
            flash(f"Validation error: {e.message}", "danger")
            return render_template("fact_form.html", mode="new", fact=new_item)
    
        facts.clear(); facts.extend(new_facts)
        global FACT_VALUE
        FACT_VALUE = {f["id"]: bool(f.get("value", False)) for f in facts}
        flash("Fact created", "success")
        return redirect(url_for("facts_list"))
    
    return render_template("fact_form.html", mode="new", fact=None)

@app.route("/facts/<fid>/edit", methods=["GET", "POST"])
def facts_edit(fid):
    fact = next((f for f in facts if f.get("id") == fid), None)
    if not fact:
        flash("Fact not found", "warning")
        return redirect(url_for("facts_list"))
    
    if request.method == "POST":
        description = (request.form.get("description") or "").strip()
        value = request.form.get("value") == "on"
        tags_raw = request.form.get("tags") or ""
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        
        updated = {"id": fact["id"], "description": description, "value": bool(value), "tags": tags}
        new_facts = [updated if f["id"] == fact["id"] else f for f in facts]
        try:
            validate(new_facts, facts_array_schema)
            write_json("facts.json", new_facts)
        except ValidationError as e:
            flash(f"Validation error: {e.message}", "danger")
            return render_template("fact_form.html", mode="edit", fact=updated)
        
        facts.clear(); facts.extend(new_facts)
        global FACT_VALUE
        FACT_VALUE = {f["id"]: bool(f.get("value", False)) for f in facts}
        flash("Fact updated", "success")
        return redirect(url_for("facts_list"))
    
    return render_template("fact_form.html", mode="edit", fact=fact)

@app.post("/facts/<fid>/delete")
def facts_delete(fid):
    if not any(f.get("id") == fid for f in facts):
        flash("Fact not found", "warning")
        return redirect(url_for("facts_list"))
    
    new_facts = [f for f in facts if f.get("id") != fid]
    try:
        validate(new_facts, facts_array_schema)
        write_json("facts.json", new_facts)
    except ValidationError as e:
        flash(f"Validation error: {e.message}", "danger")
        return redirect(url_for("facts_list"))
    
    facts.clear(); facts.extend(new_facts)
    global FACT_VALUE
    FACT_VALUE = {f["id"]: bool(f.get("value", False)) for f in facts}
    flash("Fact deleted", "success")
    return redirect(url_for("facts_list"))

# ----- Rules -----

@app.get("/rules")
def rules_list():
    return render_template("rules_list.html", rules=rules)

@app.route("/rules/new", methods=["GET","POST"])
def rules_new():
    if request.method == "POST":
        rid = (request.form.get("id") or "").strip()
        conditions_raw = request.form.get("conditions") or ""
        conclusion = (request.form.get("conclusion") or "").strip()
        certainty = clamp01(request.form.get("certainty") or 1.0)
        explain = (request.form.get("explain") or "").strip()
        
        if not rid:
            flash("ID is required", "danger")
            return render_template("rule_form.html", mode="new", rule=None)
        if any(r.get("id") == rid for r in rules):
            flash(f"Rule id '{id}' already exists", "danger")
            return render_template("rule_form.html", mode="new", rule=None)
        
        conditions = [c.strip() for c in conditions_raw.split(",") if c.strip()]
        new_item = {
            "id" : rid,
            "conditions": conditions,
            "conclusion": conclusion,
            "certainty": certainty,
            "explain":explain
        }
        new_rules = rules + [new_item]
        try:
            validate(new_rules, rules_array_schema)
            write_json("rules.json", new_rules)
        except ValidationError as e:
            flash(f"Validation error: {e.message}", "danger")
            return render_template("rule_form.html", mode="new",rule=new_item)
        
        rules.clear(); rules.extend(new_rules)
        flash("Rule created", "success")
        return redirect(url_for("rules_list"))
    
    return render_template("rule_form.html", mode="new", rule=None)

@app.route("/rules/<rid>/edit", methods=["GET","POST"])
def rules_edit(rid):
    rule = next((r for r in rules if r.get("id") == rid), None)
    if not rule:
        flash("Rule not found", "warning")
        return redirect(url_for("rules_list"))
    
    if request.method == "POST":
        conditions_raw = request.form.get("conditions") or ""
        conclusion = (request.form.get("conclusion") or "").strip()
        certainty = clamp01(request.form.get("certainty") or 1.0)
        explain = (request.form.get("explain") or "").strip()
        
        updated = {
            "id": rule["id"],
            "conditions": [c.strip() for c in conditions_raw.split(",") if c.strip()],
            "conclusion": conclusion,
            "certainty" : certainty,
            "explain": explain
        }
        new_rules = [updated if r["id"]==rule["id"] else r for r in rules]
        try:
            validate(new_rules, rules_array_schema)
            write_json("rules.json", new_rules)
        except ValidationError as e:
            flash(f"Validation error: {e.message}", "danger")
            return render_template("rule_form.html", mode="edit", rule=updated)
        
        rules.clear(); rules.extend(new_rules)
        flash("Rule updated", "success")
        return redirect(url_for("rules_list"))
    
    return render_template("rule_form.html", mode="edit",rule=rule)

@app.post("/rules/<rid>/delete")
def rules_delete(rid):
    if not any(r.get("id") == rid for r in rules):
        flash("Rule not found", "danger")
        return redirect(url_for("rules_list"))
    
    new_rules = [r for r in rules if r.get("id") != rid]
    try:
        validate(new_rules, rules_array_schema)
        write_json("rules.json", new_rules)
    except ValidationError as e:
        flash(f"Validation error: {e.message}", "danger")
        return redirect(url_for("rules_list"))
    
    rules.clear(); rules.extend(new_rules)
    flash("Rule deleted", "success")
    return redirect(url_for("rules_list"))

# ----- Taxonomy (view and raw edit) -----

@app.get("/taxonomy")
def taxonomy_view():
    return render_template("taxonomy.html", taxonomy=taxonomy)

@app.get("/taxonomy")
def taxonomy_save():
    raw = request.form.get("raw_json") or "{}"
    try:
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("Taxonomy must be an object")
        if "parent" in parsed and not isinstance(parsed["parent"], dict):
            raise ValueError("Taxonomy.parent must be an object")
        write_json("taxonomy.json", parsed)
    except Exception as e:
        flash(f"Failed to save taxonomy: {e}", "danger")
        return render_template("taxonomy.html", taxonomy=taxonomy, raw_override=raw)
    
    taxonomy.clear(); taxonomy.update(parsed)
    global PARENT
    PARENT = taxonomy.get("parent", {})
    flash("Taxonomy saved", "success")
    return redirect(url_for("taxonomy_view"))

# ------------------------------
# App runner
# ------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG") == "1"
    )
        