import React from "react";
import LogisticRegression from "../components/model_hyperparameters/logistic_regression";

export interface ModelProps {
  c?: string;
  setC?: (value: string) => void;
  solver?: string;
  setSolver?: (value: string) => void;
  penalty?: string;
  setPenalty?: (value: string) => void;
  maxIterations?: string;
  setMaxIterations?: (value: string) => void;
  fitIntercept?: boolean;
  setFitIntercept?: (value: boolean) => void;
  classWeight?: string;
  setClassWeight?: (value: string) => void;
  randomState?: string;
  setRandomState?: (value: string) => void;
  hyperparameters: boolean;
}

export const ModelComponents: Record<string, React.FC<ModelProps>> = {
  "Logistic Regression": LogisticRegression,
  "SVM": () => <div>SVM Hyperparameters Component</div>, //this is an example
  // Add more models/components here
};