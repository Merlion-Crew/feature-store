**Model registering options**

**Option 1:**

Mlflow run register model directly after run using register\_model method


```
 model_uri = "runs:/{}/model".format(run.info.run_id)
  
 model = mlflow.register_model(model_uri, "lgbm_home_credit_model")
```

**Positive**
- Can click on the run\_id to see the performance metrics of the run
- Does not require local pickling

**Negative**
- Cannot store encoding files together with model. If we are encoding before feature registering then we do not need to store encoding files here. Would have to save it for feature engineering. **Recommended to use this method if we do not need model encoding files together with model file**. If we do need encoding files alongside the model then this method does not work

**Option 2:** 

Pickle Model and encoding files to a folder. Then register the folder as model to Azure ML

```
tagsValue = {"area": "Housing_credit",
               "run_id": run_id,
               "experiment_name": exp_name}
   try:
       model = AMLModel.register(
               workspace= ws,
               model_name='lgbm_home_credit_model',
               model_path='aml-scripts/models/',
               description="Home Credit LGBM model to identify poor credit rating individuals",
               tags=tagsValue,
       )
```

**Positive**
- Can see encoding files along with the model. 

**Negative**
- Cannot click in UI to see the model training performance. Have to go check manually by copying the run\_id. Possible to add run_id as a tag to query run performance later if needed
