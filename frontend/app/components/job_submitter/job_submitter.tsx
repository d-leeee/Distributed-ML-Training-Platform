'use client';

import Input from "./input";
import Output from "./output";
import Submit from "./submit";
import { ModelComponents } from "../model_hyperparameters/helper/model_components";
import { ModelProps } from "../model_hyperparameters/helper/model_components";
import React from "react";

export default function JobSubmitter() {
    const [inputParams, setInputParams] = React.useState<ModelProps>({
        model: "",
        dataset: "",
        enabled: false,
        hyperparameters: {}
    });

    return (
        <div>
            <Input onChange={setInputParams} />
            <Submit inputParams={inputParams} />
            <Output />
        </div>
    );
}