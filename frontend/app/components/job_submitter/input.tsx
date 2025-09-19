'use client';

import * as React from "react";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
import { SelectChangeEvent } from "@mui/material/Select";
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
import Typography from '@mui/material/Typography';
import { ModelComponents, ModelProps } from "../model_hyperparameters/helper/model_components";

export default function Input(props: { onChange: (state: ModelProps) => void }) {
    const [model, setModel] = React.useState("");
    const [dataset, setDataset] = React.useState("");
    const [enabled, setEnabled] = React.useState(false);
    const [hyperparameters, setHyperparameters] = React.useState({});
    const models = ["Logistic Regression", "SVM"];
    const datasets = ["Iris", "Breast Cancer", "Wine"];
    const Hyperparameters = ModelComponents[model];

    // Keep a ref to the latest onChange to avoid stale closures and extra deps
    const onChangeRef = React.useRef(props.onChange);
    React.useEffect(() => {
        onChangeRef.current = props.onChange;
    }, [props.onChange]);

    // Propagate the latest state to the parent whenever it changes
    React.useEffect(() => {
        onChangeRef.current({
            model,
            dataset,
            enabled,
            hyperparameters
        });
    }, [model, dataset, enabled, hyperparameters]);

    return (
        <div style={{display: 'flex', flexDirection: 'column', maxWidth: '400px', marginBottom: '24px'}}>
            <Typography sx={{py:2}}>Model Type</Typography>
            <FormControl fullWidth>
                <InputLabel id="model-list">Models</InputLabel>
                <Select
                    labelId="model-list"
                    id="model-lst"
                    value={model}
                    label="Models"
                    onChange={(e: SelectChangeEvent)=> {
                        setModel(e.target.value as string);
                    }}
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
                    onChange={(e: SelectChangeEvent)=> {
                        setDataset(e.target.value as string);
                    }}
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
                        onChange={(e: React.ChangeEvent<HTMLInputElement>)=> {
                            setEnabled(e.target.checked);
                        }}
                    />
                }
                label="Hyperparameter Tuning"
            />
            {enabled && Hyperparameters && (
                <div>
                    <Hyperparameters onChange={setHyperparameters} />
                </div>
            )}
        </div>
    );
};
