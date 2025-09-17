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
    const handleModel = (event: SelectChangeEvent) => {
        setModel(event.target.value as string);
    };
    const handleDataset = (event: SelectChangeEvent) => {
        setDataset(event.target.value as string);
    };

    const models = ["Logistic Regression", "SVM"];
    const datasets = ["Iris", "Breast Cancer", "Wine"];

    return (
        <div>
            <Typography >Model Type</Typography>
            <FormControl fullWidth>
                <InputLabel id="model-list">Models</InputLabel>
                <Select
                    labelId="model-list"
                    id="model-lst"
                    value={model}
                    label="Models"
                    onChange={handleModel}
                >
                    {models.map(m => (
                        <MenuItem key={m} value={m}>{m}</MenuItem>
                    ))}
                </Select>
            </FormControl>
            <Typography>Dataset</Typography>
            <FormControl fullWidth>
                <InputLabel id="dataset-list">Datasets</InputLabel>
                <Select
                    labelId="dataset-list"
                    id="dataset-list"
                    value={dataset}
                    label="Datasets"
                    onChange={handleDataset}
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
                    {ModelComponents[model]}
                </div>
            )}
            <Button variant="contained">Submit</Button>
        </div>
    );
};
