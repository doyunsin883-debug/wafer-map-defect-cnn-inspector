"""Reproducible 9-class baseline CNN; no accuracy is claimed until run."""
import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from wafer_data import CLASS_NAMES, load_eligible, resolve_data_path

def build_model(tf):
    L=tf.keras.layers
    model=tf.keras.Sequential([
        L.Input(shape=(52,52,1)),
        L.Conv2D(32,3,padding="same",activation="relu"),
        L.MaxPooling2D(),
        L.Conv2D(64,3,padding="same",activation="relu"),
        L.MaxPooling2D(),
        L.Conv2D(128,3,padding="same",activation="relu"),
        L.MaxPooling2D(),
        L.GlobalAveragePooling2D(),
        L.Dense(128,activation="relu"),
        L.Dropout(0.3),
        L.Dense(len(CLASS_NAMES),activation="softmax"),
    ])
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3),
                  loss="sparse_categorical_crossentropy",metrics=["accuracy"])
    return model

def run(args):
    import tensorflow as tf
    random.seed(args.seed)
    np.random.seed(args.seed)
    tf.keras.utils.set_random_seed(args.seed)
    maps,y,indices,audit=load_eligible(args.data)
    x=maps.astype(np.float32)[...,None]/2.0
    xdev,xtest,ydev,ytest,idev,itest=train_test_split(
        x,y,indices,test_size=.15,stratify=y,random_state=args.seed)
    xtrain,xval,ytrain,yval=train_test_split(
        xdev,ydev,test_size=.15/.85,stratify=ydev,random_state=args.seed)
    classes=np.unique(ytrain)
    weights=compute_class_weight("balanced",classes=classes,y=ytrain)
    class_weight=dict(zip(map(int,classes),map(float,weights)))
    model=build_model(tf)
    callbacks=[
        tf.keras.callbacks.EarlyStopping(monitor="val_loss",patience=4,
                                         restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss",factor=.5,
                                             patience=2,min_lr=1e-5)]
    history=model.fit(xtrain,ytrain,validation_data=(xval,yval),
        epochs=args.epochs,batch_size=args.batch_size,
        class_weight=class_weight,callbacks=callbacks,verbose=2)
    proba=model.predict(xtest,batch_size=args.batch_size,verbose=0)
    pred=proba.argmax(axis=1)
    loss,kacc=model.evaluate(xtest,ytest,verbose=0)
    output=Path(args.output)
    output.mkdir(parents=True,exist_ok=True)
    model.save(output/"wafer_cnn.keras")
    metrics={
        "status":"measured_local_run",
        "generated_utc":datetime.now(timezone.utc).isoformat(),
        "dataset_path":str(resolve_data_path(args.data)),
        "train_count":int(len(xtrain)),"validation_count":int(len(xval)),
        "test_count":int(len(xtest)),
        "seed":args.seed,"epochs_requested":args.epochs,
        "epochs_ran":len(history.history["loss"]),
        "test_accuracy":float(accuracy_score(ytest,pred)),
        "test_macro_f1":float(f1_score(ytest,pred,average="macro")),
        "keras_test_accuracy":float(kacc),"keras_test_loss":float(loss),
        "confusion_matrix":confusion_matrix(ytest,pred,labels=list(range(9))).tolist(),
        "per_class":classification_report(ytest,pred,
            labels=list(range(9)),target_names=list(CLASS_NAMES),output_dict=True,
            zero_division=0),
        "history":{k:[float(z) for z in values]
                   for k,values in history.history.items()},
        "test_source_indices":itest.tolist(),
        "source_data_audit":audit,
    }
    (output/"evaluation.json").write_text(json.dumps(metrics,indent=2,ensure_ascii=False),encoding="utf-8")
    print("Measured test metrics written to",output/"evaluation.json")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--data",default=None)
    parser.add_argument("--epochs",type=int,default=20)
    parser.add_argument("--batch-size",type=int,default=64)
    parser.add_argument("--seed",type=int,default=42)
    parser.add_argument("--output",default="outputs")
    run(parser.parse_args())
