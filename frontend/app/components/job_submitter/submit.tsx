import { ModelProps } from "../model_hyperparameters/helper/model_components";
import { Button } from "@mui/material";
export default function Submit(props: { inputParams: ModelProps }) {
    const handleSubmit = async () => {
            const response = await fetch('http://localhost:8000/create-job', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: props.inputParams.model,
                    description: props.inputParams.dataset,
                    parameters: props.inputParams.enabled ? props.inputParams.hyperparameters : undefined
                })
            });
            const data = await response.json();
            console.log(data);
        };

    return (
        <div>
            <Button type="submit" variant="outlined" onClick={handleSubmit}>Submit Job</Button>
        </div>
    )
}