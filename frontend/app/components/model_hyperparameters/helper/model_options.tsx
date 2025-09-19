const modelOptions = {
    "Logistic Regression": {
        solvers: ["liblinear", "saga", "lbfgs", "newton-cg", "sag"],
        hyperparameters: {
            // All solvers
            C: [0.01, 0.1, 1, 10],
            max_iter: [100, 200, 1000],
            fit_intercept: [true, false],
            class_weight: ["balanced", null],
            random_state: [42],
            // By solver
            penalty: {
                liblinear: ["l1", "l2"],
                saga: ["l1", "l2", "elasticnet"],
                lbfgs: ["l2"],
                "newton-cg": ["l2"],
                sag: ["l2"]
            },
            l1_ratio: {
                saga: [0.1, 0.5, 0.9] // Only for elasticnet penalty
            }
        }
    },
    // ...other models
};