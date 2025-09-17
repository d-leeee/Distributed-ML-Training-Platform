import React from "react";
import LogisticRegression from "../components/model_hyperparameters/logistic_regression";

export const ModelComponents: Record<string, React.ReactElement> = {
  "Logistic Regression": <LogisticRegression />,
  "SVM": <div>SVM Hyperparameters Component</div>, //this is an example
  // Add more models/components here
};