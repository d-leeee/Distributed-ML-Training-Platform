import { createTheme } from '@mui/material/styles';

const theme = createTheme({
    typography: {
        fontSize: 8
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    fontSize: '0.7rem',
                    padding: '2px 8px',
                },
            },
        },
        MuiTextField: {
            styleOverrides: {
                root: {
                    fontSize: '0.1rem',
                },
            },
        },
        MuiInputBase: {
            styleOverrides: {
                root: {
                    fontSize: '0.5rem',
                },
            },
        },
        // Add more component overrides for smaller boxes if needed
    },
});

export default theme;