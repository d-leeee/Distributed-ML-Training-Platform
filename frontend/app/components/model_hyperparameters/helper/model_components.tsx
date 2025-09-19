import React from "react";
import {LogisticRegression} from "../logistic_regression";

export interface onChangeProp {
    onChange: (state: object) => void;
}

export interface ModelProps {
  model: string;
  dataset: string;
  enabled: boolean;
  hyperparameters: object;
}

export const ModelComponents: Record<string, React.FC<onChangeProp>> = {
  "Logistic Regression": ({ onChange }) => <LogisticRegression onChange={onChange} />,
  "SVM": () => <div>SVM Hyperparameters Component</div>, //this is an example
  // Add more models/components here
};