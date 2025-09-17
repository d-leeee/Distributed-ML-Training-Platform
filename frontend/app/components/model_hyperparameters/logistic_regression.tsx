import Grid from '@mui/material/Grid';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import Box from "@mui/material/Box";
import * as React from "react";
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import Switch from '@mui/material/Switch';
import TextField from '@mui/material/TextField';
import { Typography } from '@mui/material';

export default function LogisticRegression() {
    const [alignment, setAlignment] = React.useState('web');
    const [solver, setSolver] = React.useState('');
    const [classWeight, setClassWeight] = React.useState('');

    const handleSolver = (event: SelectChangeEvent) => {
        setSolver(event.target.value as string);
    };
    const handlePenalty = (
        event: React.MouseEvent<HTMLElement>,
        newAlignment: string,
    ) => {
        setAlignment(newAlignment);
    };

    const penaltyOptions: Record<string, string[]> = {
        liblinear: ["l1", "l2"],
        saga: ["l1", "l2", "elasticnet"],
        lbfgs: ["l2"],
        "newton-cg": ["l2"],
        sag: ["l2"]
    };

    return (
        <Box sx={{ flexGrow: 1 }}>
            <Grid container spacing={2} alignItems={'center'}>
                <Grid size={4}>
                    <Typography>C</Typography>
                </Grid>
                <Grid size={8}>
                    <TextField style={{ width: '100%' }} placeholder="Enter values, separated by commas"></TextField>
                </Grid>
                <Grid size={4}>
                    <Typography>Solver</Typography>
                </Grid>
                <Grid size={8}>
                    <Box sx={{ minWidth: 120 }}>
                        <FormControl fullWidth>
                            <InputLabel id="solver">Solver</InputLabel>
                            <Select
                            labelId="solver"
                            id="solver"
                            value={solver}
                            label="Solver"
                            onChange={handleSolver}
                            >
                            <MenuItem value="liblinear">Liblinear</MenuItem>
                            <MenuItem value="saga">Saga</MenuItem>
                            <MenuItem value="lbfgs">LBFGS</MenuItem>
                            <MenuItem value="sag">Sag</MenuItem>
                            </Select>
                        </FormControl>
                    </Box>
                </Grid>
                <Grid size={4}>
                    <Typography>Penalty</Typography>
                </Grid>
                <Grid size={8}>
                    <ToggleButtonGroup
                        color="primary"
                        value={alignment}
                        exclusive
                        onChange={handlePenalty}
                        aria-label="Platform"
                    >
                    {(penaltyOptions[solver] || []).map(p => (
                        <ToggleButton key={p} value={p}>{p}</ToggleButton>
                    ))}
                    </ToggleButtonGroup>
                </Grid>
                <Grid size={4}>
                    <Typography>Max Iterations</Typography>
                </Grid>
                <Grid size={8}>
                    <TextField style={{ width: '100%' }} placeholder="Enter values, separated by commas"></TextField>
                </Grid>
                <Grid size={4}>
                    <Typography>Fit Intercept</Typography>
                </Grid>
                <Grid size={8}>
                    <Switch defaultChecked />
                </Grid>
                <Grid size={4}>
                    <Typography>Class Weight</Typography>
                </Grid>
                <Grid size={8}>
                    <ToggleButtonGroup
                        color="primary"
                        value={alignment}
                        exclusive
                        onChange={handlePenalty}
                        aria-label="Platform"
                    >
                        <ToggleButton value="balanced" onClick={() => setClassWeight('balanced')}>Balanced</ToggleButton>
                        <ToggleButton value="custom" onClick={() => setClassWeight('custom')}>Custom</ToggleButton>
                        <ToggleButton value="none" onClick={() => setClassWeight('none')}>None</ToggleButton>
                    </ToggleButtonGroup>
                    {classWeight === 'custom' && (
                        <TextField style={{ width: '100%', marginTop: '10px' }} placeholder='e.g., {0: 1, 1: 4}'></TextField>
                    )}
                </Grid>
                <Grid size={4}>
                    <Typography>Random State</Typography>
                </Grid>
                <Grid size={8}>
                    <TextField></TextField>
                </Grid>
            </Grid>
        </Box>
    );  
};