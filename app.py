"""Wafer inspection Flask app; never fabricates CNN predictions."""
import os
from pathlib import Path
import numpy as np
from flask import Flask, jsonify, render_template, request
from wafer_data import CLASS_NAMES, die_counts, load_eligible, resolve_data_path

app=Flask(__name__)
STATE={"data_path":None,"maps":None,"labels":None,"indices":None,
       "audit":None,"model":None,"model_error":None}

def ensure_loaded():
    path=str(resolve_data_path())
    if STATE["data_path"]==path:
        return
    maps,y,ids,audit=load_eligible(path)
    STATE.update(data_path=path,maps=maps,labels=y,indices=ids,
                 audit=audit,model=None,model_error=None)
    model_file=Path(os.getenv("WAFER_MODEL_PATH") or "outputs/wafer_cnn.keras")
    if not model_file.is_file():
        STATE["model_error"]="MODEL NOT TRAINED — Run python train_cnn.py"
        return
    try:
        from tensorflow.keras.models import load_model
        STATE["model"]=load_model(model_file)
    except Exception as exc:
        STATE["model_error"]=f"Model load failed: {type(exc).__name__}: {exc}"

def inspect(pos):
    ensure_loaded()
    ids=STATE["indices"]
    pos=int(np.clip(int(pos),0,len(ids)-1))
    wafer=STATE["maps"][pos]
    cls=int(STATE["labels"][pos])
    model=STATE["model"]
    result={
      "position":pos,"dataset_index":int(ids[pos]),
      "wafer":wafer.astype(int).tolist(),
      "ground_truth":CLASS_NAMES[cls],
      "model_ready":model is not None,
      "model_error":STATE["model_error"],
      "prediction":None,"confidence":None,"top5":[],
      "usable_samples":int(len(ids)),**die_counts(wafer)}
    if model is not None:
        probabilities=model.predict(wafer.astype(np.float32)[None,...,None]/2.,verbose=0)[0]
        order=np.argsort(probabilities)[::-1]
        result.update(prediction=CLASS_NAMES[int(order[0])],
           confidence=float(probabilities[order[0]]),
           top5=[{"name":CLASS_NAMES[int(k)],
                  "probability":float(probabilities[k])} for k in order[:5]])
    return result

@app.get("/")
def home():
    ensure_loaded()
    return render_template("index.html")

@app.get("/api/sample")
def sample():
    return jsonify(inspect(request.args.get("pos",0,type=int)))

@app.get("/api/random")
def random_sample():
    ensure_loaded()
    return jsonify(inspect(np.random.default_rng().integers(len(STATE["indices"]))))

if __name__=="__main__":
    print("http://127.0.0.1:5000")
    app.run(host="127.0.0.1",port=5000,debug=False)
