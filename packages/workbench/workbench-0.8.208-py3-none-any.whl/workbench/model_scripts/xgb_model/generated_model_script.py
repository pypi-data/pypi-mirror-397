# Imports for XGB Model
import xgboost as xgb
import awswrangler as wr
import numpy as np

# Classification Encoder
from sklearn.preprocessing import LabelEncoder

# Scikit Learn Imports
from sklearn.model_selection import train_test_split, KFold, StratifiedKFold

import json
import argparse
import joblib
import os
import pandas as pd

# Shared model script utilities
from model_script_utils import (
    check_dataframe,
    expand_proba_column,
    match_features_case_insensitive,
    convert_categorical_types,
    decompress_features,
    input_fn,
    output_fn,
    compute_regression_metrics,
    print_regression_metrics,
    compute_classification_metrics,
    print_classification_metrics,
    print_confusion_matrix,
)

# UQ Harness for uncertainty quantification (regression models only)
from uq_harness import (
    train_uq_models,
    save_uq_models,
    load_uq_models,
    predict_intervals,
    compute_confidence,
)

# Default Hyperparameters for XGBoost
DEFAULT_HYPERPARAMETERS = {
    # Training parameters
    "n_folds": 5,  # Number of CV folds (1 = single train/val split)

    # Core tree parameters
    "n_estimators": 200,  # More trees for better signal capture when we have lots of features
    "max_depth": 6,  # Medium depth
    "learning_rate": 0.05,  # Lower rate with more estimators for smoother learning

    # Sampling parameters
    "subsample": 0.7,  # Moderate row sampling to reduce overfitting
    "colsample_bytree": 0.6,  # More aggressive feature sampling given lots of features
    "colsample_bylevel": 0.8,  # Additional feature sampling at each tree level

    # Regularization
    "min_child_weight": 5,  # Higher to prevent overfitting on small groups
    "gamma": 0.2,  # Moderate pruning - you have real signal so don't over-prune
    "reg_alpha": 0.5,  # L1 for feature selection (useful with many features)
    "reg_lambda": 2.0,  # Strong L2 to smooth predictions

    # Random seed
    "random_state": 42,
}

# Workbench-specific hyperparameters (these are used by the training harness, not passed to XGBoost)
WORKBENCH_PARAMS = {"n_folds"}

# Template Parameters
TEMPLATE_PARAMS = {
    "model_type": "uq_regressor",
    "target": "udm_asy_res_efflux_ratio",
    "features": ['chi2v', 'fr_sulfone', 'chi1v', 'bcut2d_logplow', 'fr_piperzine', 'kappa3', 'smr_vsa1', 'slogp_vsa5', 'fr_ketone_topliss', 'fr_sulfonamd', 'fr_imine', 'fr_benzene', 'fr_ester', 'chi2n', 'labuteasa', 'peoe_vsa2', 'smr_vsa6', 'bcut2d_chglo', 'fr_sh', 'peoe_vsa1', 'fr_allylic_oxid', 'chi4n', 'fr_ar_oh', 'fr_nh0', 'fr_term_acetylene', 'slogp_vsa7', 'slogp_vsa4', 'estate_vsa1', 'vsa_estate4', 'numbridgeheadatoms', 'numheterocycles', 'fr_ketone', 'fr_morpholine', 'fr_guanido', 'estate_vsa2', 'numheteroatoms', 'fr_nitro_arom_nonortho', 'fr_piperdine', 'nocount', 'numspiroatoms', 'fr_aniline', 'fr_thiophene', 'slogp_vsa10', 'fr_amide', 'slogp_vsa2', 'fr_epoxide', 'vsa_estate7', 'fr_ar_coo', 'fr_imidazole', 'fr_nitrile', 'fr_oxazole', 'numsaturatedrings', 'fr_pyridine', 'fr_hoccn', 'fr_ndealkylation1', 'numaliphaticheterocycles', 'fr_phenol', 'maxpartialcharge', 'vsa_estate5', 'peoe_vsa13', 'minpartialcharge', 'qed', 'fr_al_oh', 'slogp_vsa11', 'chi0n', 'fr_bicyclic', 'peoe_vsa12', 'fpdensitymorgan1', 'fr_oxime', 'molwt', 'fr_dihydropyridine', 'smr_vsa5', 'peoe_vsa5', 'fr_nitro', 'hallkieralpha', 'heavyatommolwt', 'fr_alkyl_halide', 'peoe_vsa8', 'fr_nhpyrrole', 'fr_isocyan', 'bcut2d_chghi', 'fr_lactam', 'peoe_vsa11', 'smr_vsa9', 'tpsa', 'chi4v', 'slogp_vsa1', 'phi', 'bcut2d_logphi', 'avgipc', 'estate_vsa11', 'fr_coo', 'bcut2d_mwhi', 'numunspecifiedatomstereocenters', 'vsa_estate10', 'estate_vsa8', 'numvalenceelectrons', 'fr_nh2', 'fr_lactone', 'vsa_estate1', 'estate_vsa4', 'numatomstereocenters', 'vsa_estate8', 'fr_para_hydroxylation', 'peoe_vsa3', 'fr_thiazole', 'peoe_vsa10', 'fr_ndealkylation2', 'slogp_vsa12', 'peoe_vsa9', 'maxestateindex', 'fr_quatn', 'smr_vsa7', 'minestateindex', 'numaromaticheterocycles', 'numrotatablebonds', 'fr_ar_nh', 'fr_ether', 'exactmolwt', 'fr_phenol_noorthohbond', 'slogp_vsa3', 'fr_ar_n', 'sps', 'fr_c_o_nocoo', 'bertzct', 'peoe_vsa7', 'slogp_vsa8', 'numradicalelectrons', 'molmr', 'fr_tetrazole', 'numsaturatedcarbocycles', 'bcut2d_mrhi', 'kappa1', 'numamidebonds', 'fpdensitymorgan2', 'smr_vsa8', 'chi1n', 'estate_vsa6', 'fr_barbitur', 'fr_diazo', 'kappa2', 'chi0', 'bcut2d_mrlow', 'balabanj', 'peoe_vsa4', 'numhacceptors', 'fr_sulfide', 'chi3n', 'smr_vsa2', 'fr_al_oh_notert', 'fr_benzodiazepine', 'fr_phos_ester', 'fr_aldehyde', 'fr_coo2', 'estate_vsa5', 'fr_prisulfonamd', 'numaromaticcarbocycles', 'fr_unbrch_alkane', 'fr_urea', 'fr_nitroso', 'smr_vsa10', 'fr_c_s', 'smr_vsa3', 'fr_methoxy', 'maxabspartialcharge', 'slogp_vsa9', 'heavyatomcount', 'fr_azide', 'chi3v', 'smr_vsa4', 'mollogp', 'chi0v', 'fr_aryl_methyl', 'fr_nh1', 'fpdensitymorgan3', 'fr_furan', 'fr_hdrzine', 'fr_arn', 'numaromaticrings', 'vsa_estate3', 'fr_azo', 'fr_halogen', 'estate_vsa9', 'fr_hdrzone', 'numhdonors', 'fr_alkyl_carbamate', 'fr_isothiocyan', 'minabspartialcharge', 'fr_al_coo', 'ringcount', 'chi1', 'estate_vsa7', 'fr_nitro_arom', 'vsa_estate9', 'minabsestateindex', 'maxabsestateindex', 'vsa_estate6', 'estate_vsa10', 'estate_vsa3', 'fr_n_o', 'fr_amidine', 'fr_thiocyan', 'fr_phos_acid', 'fr_c_o', 'fr_imide', 'numaliphaticrings', 'peoe_vsa6', 'vsa_estate2', 'nhohcount', 'numsaturatedheterocycles', 'slogp_vsa6', 'peoe_vsa14', 'fractioncsp3', 'bcut2d_mwlow', 'numaliphaticcarbocycles', 'fr_priamide', 'nacid', 'nbase', 'naromatom', 'narombond', 'sz', 'sm', 'sv', 'sse', 'spe', 'sare', 'sp', 'si', 'mz', 'mm', 'mv', 'mse', 'mpe', 'mare', 'mp', 'mi', 'xch_3d', 'xch_4d', 'xch_5d', 'xch_6d', 'xch_7d', 'xch_3dv', 'xch_4dv', 'xch_5dv', 'xch_6dv', 'xch_7dv', 'xc_3d', 'xc_4d', 'xc_5d', 'xc_6d', 'xc_3dv', 'xc_4dv', 'xc_5dv', 'xc_6dv', 'xpc_4d', 'xpc_5d', 'xpc_6d', 'xpc_4dv', 'xpc_5dv', 'xpc_6dv', 'xp_0d', 'xp_1d', 'xp_2d', 'xp_3d', 'xp_4d', 'xp_5d', 'xp_6d', 'xp_7d', 'axp_0d', 'axp_1d', 'axp_2d', 'axp_3d', 'axp_4d', 'axp_5d', 'axp_6d', 'axp_7d', 'xp_0dv', 'xp_1dv', 'xp_2dv', 'xp_3dv', 'xp_4dv', 'xp_5dv', 'xp_6dv', 'xp_7dv', 'axp_0dv', 'axp_1dv', 'axp_2dv', 'axp_3dv', 'axp_4dv', 'axp_5dv', 'axp_6dv', 'axp_7dv', 'c1sp1', 'c2sp1', 'c1sp2', 'c2sp2', 'c3sp2', 'c1sp3', 'c2sp3', 'c3sp3', 'c4sp3', 'hybratio', 'fcsp3', 'num_stereocenters', 'num_unspecified_stereocenters', 'num_defined_stereocenters', 'num_r_centers', 'num_s_centers', 'num_stereobonds', 'num_e_bonds', 'num_z_bonds', 'stereo_complexity', 'frac_defined_stereo'],
    "id_column": "udm_mol_bat_id",
    "compressed_features": [],
    "model_metrics_s3_path": "s3://ideaya-sageworks-bucket/models/caco2-er-reg-test/training",
    "hyperparameters": None,
}


if __name__ == "__main__":
    """The main function is for training the XGBoost model ensemble"""

    # Harness Template Parameters
    target = TEMPLATE_PARAMS["target"]
    features = TEMPLATE_PARAMS["features"]
    orig_features = features.copy()
    id_column = TEMPLATE_PARAMS["id_column"]
    compressed_features = TEMPLATE_PARAMS["compressed_features"]
    model_type = TEMPLATE_PARAMS["model_type"]
    model_metrics_s3_path = TEMPLATE_PARAMS["model_metrics_s3_path"]
    hyperparameters = {**DEFAULT_HYPERPARAMETERS, **(TEMPLATE_PARAMS["hyperparameters"] or {})}

    # Script arguments for input/output directories
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=str, default=os.environ.get("SM_MODEL_DIR", "/opt/ml/model"))
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN", "/opt/ml/input/data/train"))
    parser.add_argument(
        "--output-data-dir", type=str, default=os.environ.get("SM_OUTPUT_DATA_DIR", "/opt/ml/output/data")
    )
    args = parser.parse_args()

    # Read the training data into DataFrames
    training_files = [os.path.join(args.train, file) for file in os.listdir(args.train) if file.endswith(".csv")]
    print(f"Training Files: {training_files}")

    # Combine files and read them all into a single pandas dataframe
    all_df = pd.concat([pd.read_csv(file, engine="python") for file in training_files])

    # Check if the dataframe is empty
    check_dataframe(all_df, "training_df")

    # Features/Target output
    print(f"Target: {target}")
    print(f"Features: {str(features)}")

    # Convert any features that might be categorical to 'category' type
    all_df, category_mappings = convert_categorical_types(all_df, features)

    # If we have compressed features, decompress them
    if compressed_features:
        print(f"Decompressing features {compressed_features}...")
        all_df, features = decompress_features(all_df, features, compressed_features)

    # Use hyperparameters (merged with defaults)
    print(f"Hyperparameters: {hyperparameters}")
    n_folds = hyperparameters["n_folds"]

    # Filter out Workbench-specific parameters, pass the rest to XGBoost
    xgb_params = {k: v for k, v in hyperparameters.items() if k not in WORKBENCH_PARAMS}
    print(f"XGBoost params: {xgb_params}")

    # Set up label encoder for classification
    if model_type == "classifier":
        label_encoder = LabelEncoder()
        all_df[target] = label_encoder.fit_transform(all_df[target])
        num_classes = len(label_encoder.classes_)
    else:
        label_encoder = None
        num_classes = None

    # =========================================================================
    # UNIFIED TRAINING: Works for n_folds=1 (single model) or n_folds>1 (K-fold CV)
    # =========================================================================
    print(f"Training {'single model' if n_folds == 1 else f'{n_folds}-fold cross-validation ensemble'}...")

    # Create fold splits
    if n_folds == 1:
        # Single fold: use train/val split from "training" column or random split
        if "training" in all_df.columns:
            print("Found training column, splitting data based on training column")
            train_idx = np.where(all_df["training"])[0]
            val_idx = np.where(~all_df["training"])[0]
        else:
            print("WARNING: No training column found, splitting data with random 80/20 split")
            indices = np.arange(len(all_df))
            train_idx, val_idx = train_test_split(indices, test_size=0.2, random_state=42)
        folds = [(train_idx, val_idx)]
    else:
        # K-Fold CV
        if model_type == "classifier":
            kfold = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
            split_target = all_df[target]
        else:
            kfold = KFold(n_splits=n_folds, shuffle=True, random_state=42)
            split_target = None
        folds = list(kfold.split(all_df, split_target))

    # Initialize storage for out-of-fold predictions
    oof_predictions = np.full(len(all_df), np.nan, dtype=np.float64)
    if model_type == "classifier" and num_classes and num_classes > 1:
        oof_proba = np.full((len(all_df), num_classes), np.nan, dtype=np.float64)
    else:
        oof_proba = None

    ensemble_models = []

    # Check for sample weights
    if "sample_weight" in all_df.columns:
        has_sample_weights = True
        print(f"Using sample weights: min={all_df['sample_weight'].min():.2f}, "
              f"max={all_df['sample_weight'].max():.2f}, mean={all_df['sample_weight'].mean():.2f}")
    else:
        has_sample_weights = False
        print("No sample weights found, training with equal weights")

    for fold_idx, (train_idx, val_idx) in enumerate(folds):
        print(f"\n{'='*50}")
        print(f"Training Fold {fold_idx + 1}/{len(folds)}")
        print(f"{'='*50}")

        # Split data for this fold
        df_train = all_df.iloc[train_idx]
        df_val = all_df.iloc[val_idx]
        print(f"Fold {fold_idx + 1} - Train: {len(df_train)}, Val: {len(df_val)}")

        # Get training data
        X_train = df_train[features]
        y_train = df_train[target]
        sample_weights = df_train["sample_weight"] if has_sample_weights else None

        # Create and train XGBoost model for this fold
        # Use different random state per fold for ensemble diversity
        fold_params = {**xgb_params, "random_state": xgb_params.get("random_state", 42) + fold_idx}

        if model_type == "classifier":
            xgb_model = xgb.XGBClassifier(enable_categorical=True, **fold_params)
        else:
            xgb_model = xgb.XGBRegressor(enable_categorical=True, **fold_params)

        xgb_model.fit(X_train, y_train, sample_weight=sample_weights)
        ensemble_models.append(xgb_model)

        # Make out-of-fold predictions
        X_val = df_val[features]
        fold_preds = xgb_model.predict(X_val)

        if model_type == "classifier":
            oof_predictions[val_idx] = fold_preds.astype(int)
            if oof_proba is not None:
                oof_proba[val_idx] = xgb_model.predict_proba(X_val)
        else:
            oof_predictions[val_idx] = fold_preds

        print(f"Fold {fold_idx + 1} complete!")

    print(f"\nTraining complete! Trained {len(ensemble_models)} model(s).")

    # Compute validation metrics and predictions
    if n_folds == 1:
        # Single fold - use validation predictions
        val_mask = ~np.isnan(oof_predictions)
        preds = oof_predictions[val_mask]
        df_val = all_df[val_mask].copy()
        if oof_proba is not None:
            oof_proba = oof_proba[val_mask]
        # Compute prediction_std (will be 0 for single model)
        preds_std = np.zeros_like(preds)
    else:
        # K-fold CV - use out-of-fold predictions
        preds = oof_predictions
        df_val = all_df.copy()
        # Compute prediction_std by running all ensemble models on all data
        print("Computing prediction_std from ensemble predictions...")
        all_ensemble_preds = [m.predict(all_df[features]) for m in ensemble_models]
        ensemble_preds = np.stack(all_ensemble_preds, axis=0)
        preds_std = np.std(ensemble_preds, axis=0)
        print(f"Ensemble prediction_std - mean: {np.mean(preds_std):.4f}, max: {np.max(preds_std):.4f}")

    # Process predictions for output
    if model_type == "classifier":
        # Get probabilities for classification
        if oof_proba is not None:
            df_val = df_val.copy()
            df_val["pred_proba"] = [p.tolist() for p in oof_proba]
            df_val = expand_proba_column(df_val, label_encoder.classes_)

        # Decode the target and prediction labels
        y_validate = label_encoder.inverse_transform(df_val[target])
        preds_decoded = label_encoder.inverse_transform(preds.astype(int))
    else:
        y_validate = df_val[target].values
        preds_decoded = preds

    # Save predictions to S3
    df_val = df_val.copy()
    df_val["prediction"] = preds_decoded

    # Build output columns - include id_column if it exists
    output_columns = []
    if id_column in df_val.columns:
        output_columns.append(id_column)
    output_columns += [target, "prediction"]

    # Add prediction_std for regression models
    if model_type != "classifier":
        df_val["prediction_std"] = preds_std
        output_columns.append("prediction_std")
        print(f"Ensemble std - mean: {df_val['prediction_std'].mean():.4f}, max: {df_val['prediction_std'].max():.4f}")

    output_columns += [col for col in df_val.columns if col.endswith("_proba")]
    wr.s3.to_csv(
        df_val[output_columns],
        path=f"{model_metrics_s3_path}/validation_predictions.csv",
        index=False,
    )

    # Report Performance Metrics
    if model_type == "classifier":
        label_names = label_encoder.classes_
        score_df = compute_classification_metrics(y_validate, preds_decoded, label_names, target)
        print_classification_metrics(score_df, target, label_names)
        print_confusion_matrix(y_validate, preds_decoded, label_names)
    else:
        # Calculate and print regression metrics
        metrics = compute_regression_metrics(y_validate, preds_decoded)
        print_regression_metrics(metrics)

        # ==========================================
        # Train UQ models for regression (uncertainty quantification)
        # ==========================================
        print("\n" + "=" * 50)
        print("Training UQ Models for Uncertainty Quantification")
        print("=" * 50)
        X_all = all_df[features]
        y_all = all_df[target]
        uq_models, uq_metadata = train_uq_models(X_all, y_all, df_val[features], y_validate)

    # Save ensemble models
    for model_idx, ens_model in enumerate(ensemble_models):
        model_path = os.path.join(args.model_dir, f"xgb_model_{model_idx}.joblib")
        joblib.dump(ens_model, model_path)
        print(f"Saved model {model_idx + 1} to {model_path}")

    # Save ensemble metadata
    n_ensemble = len(ensemble_models)
    ensemble_metadata = {"n_ensemble": n_ensemble, "n_folds": n_folds}
    with open(os.path.join(args.model_dir, "ensemble_metadata.json"), "w") as fp:
        json.dump(ensemble_metadata, fp)
    print(f"Saved ensemble metadata (n_ensemble={n_ensemble}, n_folds={n_folds})")

    # Save the label encoder if we have one
    if label_encoder:
        joblib.dump(label_encoder, os.path.join(args.model_dir, "label_encoder.joblib"))

    # Save the features (this will validate input during predictions)
    with open(os.path.join(args.model_dir, "feature_columns.json"), "w") as fp:
        json.dump(orig_features, fp)  # We save the original features, not the decompressed ones

    # Save the category mappings
    with open(os.path.join(args.model_dir, "category_mappings.json"), "w") as fp:
        json.dump(category_mappings, fp)

    # Save hyperparameters (merged defaults + user overrides) for reproducibility
    with open(os.path.join(args.model_dir, "hyperparameters.json"), "w") as fp:
        json.dump(hyperparameters, fp, indent=2)

    # Save UQ models for regression
    if model_type != "classifier":
        save_uq_models(uq_models, uq_metadata, args.model_dir)
        print(f"\nModel training complete!")
        print(f"Saved {n_ensemble} XGBoost model(s) and {len(uq_models)} UQ models to {args.model_dir}")


def model_fn(model_dir) -> dict:
    """Load XGBoost ensemble models and UQ models (if regression) from the specified directory.

    Returns:
        dict: Dictionary containing ensemble models and optionally UQ models
    """
    # Load ensemble metadata
    ensemble_metadata_path = os.path.join(model_dir, "ensemble_metadata.json")
    if os.path.exists(ensemble_metadata_path):
        with open(ensemble_metadata_path) as fp:
            ensemble_metadata = json.load(fp)
        n_ensemble = ensemble_metadata["n_ensemble"]
    else:
        # Legacy single model
        n_ensemble = 1

    # Load ensemble models
    ensemble_models = []
    for ens_idx in range(n_ensemble):
        # Try numbered model path first, fall back to legacy path
        model_path = os.path.join(model_dir, f"xgb_model_{ens_idx}.joblib")
        if not os.path.exists(model_path):
            model_path = os.path.join(model_dir, "xgb_model.joblib")
        ensemble_models.append(joblib.load(model_path))

    # Load label encoder if it exists (classifier)
    label_encoder = None
    label_encoder_path = os.path.join(model_dir, "label_encoder.joblib")
    if os.path.exists(label_encoder_path):
        label_encoder = joblib.load(label_encoder_path)

    # Load category mappings
    category_mappings = {}
    category_path = os.path.join(model_dir, "category_mappings.json")
    if os.path.exists(category_path):
        with open(category_path) as fp:
            category_mappings = json.load(fp)

    # Load UQ models if they exist (regression only)
    uq_models = None
    uq_metadata = None
    uq_metadata_path = os.path.join(model_dir, "uq_metadata.json")
    if os.path.exists(uq_metadata_path):
        uq_models, uq_metadata = load_uq_models(model_dir)

    return {
        "ensemble_models": ensemble_models,
        "n_ensemble": n_ensemble,
        "label_encoder": label_encoder,
        "category_mappings": category_mappings,
        "uq_models": uq_models,
        "uq_metadata": uq_metadata,
    }


def predict_fn(df, models) -> pd.DataFrame:
    """Make Predictions with our XGBoost Model ensemble.

    Args:
        df (pd.DataFrame): The input DataFrame
        models (dict): Dictionary containing ensemble models and optionally UQ models

    Returns:
        pd.DataFrame: The DataFrame with predictions (and prediction_std for regression)
    """
    compressed_features = TEMPLATE_PARAMS["compressed_features"]

    # Grab our feature columns (from training)
    model_dir = os.environ.get("SM_MODEL_DIR", "/opt/ml/model")
    with open(os.path.join(model_dir, "feature_columns.json")) as fp:
        features = json.load(fp)
    print(f"Model Features: {features}")

    # Extract components from models dict
    ensemble_models = models["ensemble_models"]
    n_ensemble = models["n_ensemble"]
    label_encoder = models.get("label_encoder")
    category_mappings = models.get("category_mappings", {})
    uq_models = models.get("uq_models")
    uq_metadata = models.get("uq_metadata")

    # Match features in a case-insensitive manner
    matched_df = match_features_case_insensitive(df, features)

    # Detect categorical types in the incoming DataFrame
    matched_df, _ = convert_categorical_types(matched_df, features, category_mappings)

    # If we have compressed features, decompress them
    if compressed_features:
        print("Decompressing features for prediction...")
        matched_df, features = decompress_features(matched_df, features, compressed_features)

    # Get feature matrix
    X = matched_df[features]

    # Collect predictions from all ensemble members
    all_ensemble_preds = []
    all_ensemble_probs = []

    for ens_model in ensemble_models:
        ens_preds = ens_model.predict(X)
        all_ensemble_preds.append(ens_preds)

        # For classification, collect probabilities
        if label_encoder is not None and hasattr(ens_model, "predict_proba"):
            all_ensemble_probs.append(ens_model.predict_proba(X))

    # Stack and compute mean/std
    ensemble_preds = np.stack(all_ensemble_preds, axis=0)  # (n_ensemble, n_samples)
    preds = np.mean(ensemble_preds, axis=0)
    preds_std = np.std(ensemble_preds, axis=0)  # Will be 0s for n_ensemble=1

    print(f"Inference: Ensemble predictions shape: {preds.shape}, n_ensemble: {n_ensemble}")

    # Handle classification vs regression
    if label_encoder is not None:
        # For classification, average probabilities then take argmax
        if all_ensemble_probs:
            ensemble_probs = np.stack(all_ensemble_probs, axis=0)  # (n_ensemble, n_samples, n_classes)
            avg_probs = np.mean(ensemble_probs, axis=0)  # (n_samples, n_classes)
            class_preds = np.argmax(avg_probs, axis=1)
            predictions = label_encoder.inverse_transform(class_preds)

            df["pred_proba"] = [p.tolist() for p in avg_probs]
            df = expand_proba_column(df, label_encoder.classes_)
        else:
            predictions = label_encoder.inverse_transform(preds.astype(int))

        df["prediction"] = predictions
    else:
        # Regression
        df["prediction"] = preds
        df["prediction_std"] = preds_std

        # Add UQ prediction intervals for regression models
        if uq_models and uq_metadata:
            df = predict_intervals(df, X, uq_models, uq_metadata)

            # Compute confidence scores
            df = compute_confidence(
                df,
                median_interval_width=uq_metadata["median_interval_width"],
                lower_q="q_10",
                upper_q="q_90",
            )

    return df
