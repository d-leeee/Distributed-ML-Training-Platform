'use client';

import * as React from "react";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
import { ModelComponents } from "../helper/model_components";
import Button from '@mui/material/Button'
import Typography from '@mui/material/Typography';

export default function Input() {
    const [model, setModel] = React.useState("");
    const [dataset, setDataset] = React.useState("");
    const [enabled, setEnabled] = React.useState(false);
    const [c, setC] = React.useState('');
    const [solver, setSolver] = React.useState('');
    const [penalty, setPenalty] = React.useState('');
    const [maxIterations, setMaxIterations] = React.useState('');
    const [fitIntercept, setFitIntercept] = React.useState(true);
    const [classWeight, setClassWeight] = React.useState('');
    const [randomState, setRandomState] = React.useState('');
    const models = ["Logistic Regression", "SVM"];
    const datasets = ["Iris", "Breast Cancer", "Wine"];

    const Hyperparameters = ModelComponents[model];
    const hyperparams = {
        C: c ? c.split(',').map(Number) : undefined,
        penalty: penalty ? [penalty] : undefined, // change to multiple options later
        solver: solver ? [solver]: undefined,
        max_iter: maxIterations ? maxIterations.split(',').map(Number) : undefined,
        fit_intercept: fitIntercept ? [fitIntercept] : undefined,
        class_weight: classWeight ? [classWeight] : undefined,
        random_state: randomState ? [Number(randomState)] : undefined
    }

    const handleSubmit = async () => {
        const response = await fetch('http://localhost:8000/create-job', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: model,
                description: dataset,
                parameters: enabled ? hyperparams : undefined
            })
        });
        const data = await response.json();
        console.log(data);
    };

    return (
        <div>
            <Typography sx={{py:2}}>Model Type</Typography>
            <FormControl fullWidth>
                <InputLabel id="model-list">Models</InputLabel>
                <Select
                    labelId="model-list"
                    id="model-lst"
                    value={model}
                    label="Models"
                    onChange={(e)=> setModel(e.target.value)}
                >
                    {models.map(m => (
                        <MenuItem key={m} value={m}>{m}</MenuItem>
                    ))}
                </Select>
            </FormControl>
            <Typography sx={{py:2}}>Dataset</Typography>
            <FormControl fullWidth>
                <InputLabel id="dataset-list">Datasets</InputLabel>
                <Select
                    labelId="dataset-list"
                    id="dataset-list"
                    value={dataset}
                    label="Datasets"
                    onChange={(e)=> setDataset(e.target.value)}
                >
                    {datasets.map(d => (
                        <MenuItem key={d} value={d}>{d}</MenuItem>
                    ))}
                </Select>
            </FormControl>
            <FormControlLabel
                control={
                    <Switch
                        checked={enabled}
                        onChange={e => setEnabled(e.target.checked)}
                    />
                }
                label="Hyperparameter Tuning"
            />
            {enabled && (
                <div>
                    <Hyperparameters
                        c={c}
                        setC={setC}
                        solver={solver}
                        setSolver={setSolver}
                        penalty={penalty}
                        setPenalty={setPenalty}
                        maxIterations={maxIterations}
                        setMaxIterations={setMaxIterations}
                        fitIntercept={fitIntercept}
                        setFitIntercept={setFitIntercept}
                        classWeight={classWeight}
                        setClassWeight={setClassWeight} 
                        randomState={randomState}
                        setRandomState={setRandomState}
                        hyperparameters={enabled}
                    />
                </div>
            )}
            <Button variant="contained" type="button" onClick={handleSubmit}>Submit</Button>
        </div>
    );
};
