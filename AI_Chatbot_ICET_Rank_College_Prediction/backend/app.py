from flask import Flask, render_template, request, jsonify
import sqlite3, re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR.parent / "database" / "icet_predictor.db"

app = Flask(__name__, template_folder="templates", static_folder="static")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    schema = (BASE_DIR.parent / "database" / "schema.sql").read_text(encoding="utf-8")
    conn.executescript(schema)
    conn.commit()
    conn.close()

def get_colleges():
    conn=db()
    rows=conn.execute("SELECT * FROM colleges ORDER BY cutoff_rank ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ---------------- Agentic AI layer ----------------
# Each agent has one focused responsibility. The orchestrator combines
# their outputs into one prediction and chatbot response.

class RankAgent:
    def estimate_rank(self, score):
        # Educational approximation for demo purposes; not an official ICET formula.
        score=float(score)
        if score >= 150: band="1-500"
        elif score >= 140: band="501-1500"
        elif score >= 130: band="1501-4000"
        elif score >= 120: band="4001-9000"
        elif score >= 110: band="9001-18000"
        elif score >= 100: band="18001-35000"
        elif score >= 90: band="35001-60000"
        elif score >= 80: band="60001-90000"
        elif score >= 70: band="90001-130000"
        else: band="130001+"
        return {"score":score,"estimated_rank_band":band}

class CollegeAgent:
    def predict(self, rank, category="OC", region="AU", limit=8):
        colleges=get_colleges()
        try:
            rank_value=int(rank)
        except:
            rank_value=999999

        # cutoff_rank is treated as an approximate last-rank indicator.
        ranked=[]
        for c in colleges:
            cutoff=int(c["cutoff_rank"])
            if rank_value <= cutoff:
                chance="High"
                confidence=90
            elif rank_value <= cutoff*1.35:
                chance="Medium"
                confidence=65
            elif rank_value <= cutoff*1.8:
                chance="Low"
                confidence=40
            else:
                continue
            if category != "All" and c["category"] != category and c["category"] != "All":
                continue
            if region != "All" and c["region"] != region:
                continue
            item=dict(c)
            item.update({"chance":chance,"confidence":confidence})
            ranked.append(item)

        ranked.sort(key=lambda x:(-x["confidence"], x["cutoff_rank"]))
        return ranked[:limit]

class PreferenceAgent:
    def score_preferences(self, colleges, preferred_course="", max_fee=None, preferred_city=""):
        result=[]
        for c in colleges:
            score=0
            reasons=[]
            if preferred_course:
                if preferred_course.lower() in c["course"].lower():
                    score+=30; reasons.append("preferred course")
            if max_fee is not None:
                if float(c["annual_fee"]) <= float(max_fee):
                    score+=25; reasons.append("within fee budget")
                else:
                    score-=10
            if preferred_city:
                if preferred_city.lower() in c["city"].lower():
                    score+=25; reasons.append("preferred city")
            item=dict(c)
            item["preference_score"]=score
            item["preference_reasons"]=", ".join(reasons) if reasons else "rank-based match"
            result.append(item)
        return sorted(result,key=lambda x:(-x["preference_score"], x["cutoff_rank"]))

class ExplanationAgent:
    def explain(self, rank_info, predictions):
        if not predictions:
            return f"Your estimated rank band is {rank_info['estimated_rank_band']}. I could not find a close match in the current demo database. Try a broader category/region or add more colleges."
        high=sum(1 for x in predictions if x["chance"]=="High")
        medium=sum(1 for x in predictions if x["chance"]=="Medium")
        return (f"Based on an estimated rank band of {rank_info['estimated_rank_band']}, "
                f"I found {len(predictions)} possible colleges: {high} high-chance and "
                f"{medium} medium-chance options. These are indicative predictions, not admission guarantees.")

class AgentOrchestrator:
    def __init__(self):
        self.rank_agent=RankAgent()
        self.college_agent=CollegeAgent()
        self.preference_agent=PreferenceAgent()
        self.explanation_agent=ExplanationAgent()

    def predict(self, payload):
        score=float(payload.get("score",0))
        rank_info=self.rank_agent.estimate_rank(score)

        rank_for_lookup = payload.get("rank")
        if not rank_for_lookup:
            # Use midpoint of estimated band for demo matching.
            band=rank_info["estimated_rank_band"]
            if "+" in band:
                rank_for_lookup=150000
            else:
                a,b=map(int,band.split("-"))
                rank_for_lookup=(a+b)//2

        preds=self.college_agent.predict(
            rank_for_lookup,
            payload.get("category","OC"),
            payload.get("region","AU"),
            12
        )
        max_fee=payload.get("max_fee")
        max_fee=float(max_fee) if max_fee not in ("",None) else None
        preds=self.preference_agent.score_preferences(
            preds,
            payload.get("course",""),
            max_fee,
            payload.get("city","")
        )
        explanation=self.explanation_agent.explain(rank_info,preds)
        return {"rank_info":rank_info,"rank_used":rank_for_lookup,"predictions":preds,"explanation":explanation}

orchestrator=AgentOrchestrator()

@app.route("/")
def home(): return render_template("index.html")

@app.route("/predict")
def predict_page(): return render_template("predict.html")

@app.route("/chatbot")
def chatbot_page(): return render_template("chatbot.html")

@app.route("/colleges")
def colleges_page(): return render_template("colleges.html")

@app.get("/api/colleges")
def api_colleges():
    return jsonify(get_colleges())

@app.post("/api/predict")
def api_predict():
    try:
        payload=request.get_json(force=True)
        if not payload.get("score") and not payload.get("rank"):
            return jsonify({"error":"Enter an ICET score or rank."}),400
        if payload.get("score"):
            result=orchestrator.predict(payload)
        else:
            payload["score"]=0
            result=orchestrator.predict(payload)
            result["rank_info"]={"score":None,"estimated_rank_band":f"Provided rank: {payload['rank']}"}
            result["rank_used"]=int(payload["rank"])
            preds=orchestrator.college_agent.predict(
                payload["rank"],payload.get("category","OC"),payload.get("region","AU"),12)
            result["predictions"]=orchestrator.preference_agent.score_preferences(
                preds,payload.get("course",""),
                float(payload["max_fee"]) if payload.get("max_fee") else None,
                payload.get("city",""))
            result["explanation"]=orchestrator.explanation_agent.explain(result["rank_info"],result["predictions"])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error":str(e)}),400

def chatbot_reply(message):
    text=message.lower().strip()
    score_match=re.search(r"(?:score|marks?)\s*[:=]?\s*(\d{1,3}(?:\.\d+)?)",text)
    rank_match=re.search(r"(?:rank|icet rank)\s*[:=]?\s*(\d{1,6})",text)
    if score_match:
        score=float(score_match.group(1))
        result=orchestrator.predict({"score":score,"category":"OC","region":"AU"})
        top=result["predictions"][:5]
        names=", ".join(x["name"] for x in top)
        return (f"With an ICET score of {score:g}, the demo Rank Agent estimates "
                f"{result['rank_info']['estimated_rank_band']}. "
                f"Possible colleges include: {names or 'no close matches'}. "
                f"Ask me about fees, courses, categories, regions, or a specific college.")
    if rank_match:
        rank=int(rank_match.group(1))
        preds=orchestrator.college_agent.predict(rank,"OC","AU",5)
        names=", ".join(x["name"] for x in preds)
        return f"For rank {rank}, the current demo prediction suggests: {names or 'no close matches'}. These are indicative only."
    if "agent" in text:
        return "I use an Agentic AI-style workflow: Rank Agent → College Matching Agent → Preference Agent → Explanation Agent → final response."
    if "fee" in text or "fees" in text:
        return "You can enter a maximum annual fee in the Predictor. I will prioritize colleges within your budget."
    if "course" in text:
        return "Enter a preferred course such as MBA or MCA. The Preference Agent will prioritize matching colleges."
    if "hello" in text or "hi" in text:
        return "Hello! I can estimate your ICET rank and suggest colleges. Try: 'My score is 125'."
    return "I can help with ICET score/rank prediction, college suggestions, fees, courses and regions. Try 'score 125' or 'rank 5000'."

@app.post("/api/chat")
def api_chat():
    data=request.get_json(force=True)
    message=data.get("message","")
    if not message.strip(): return jsonify({"error":"Message is empty."}),400
    return jsonify({"reply":chatbot_reply(message)})

if __name__=="__main__":
    init_db()
    app.run(debug=True)
